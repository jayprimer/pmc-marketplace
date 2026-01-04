#!/usr/bin/env python3
"""
Check ticket completion status based on KB rules.

Usage:
    python check_ticket.py T00001
    python check_ticket.py T00001 --json
    python check_ticket.py T00001 --docs-path .pmc/docs
"""

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Literal

# Required documents for a ticket
REQUIRED_DOCS = [
    "1-definition.md",
    "2-plan.md",
    "3-spec.md",
]

PROGRESS_DOC = "4-progress.md"
FINAL_DOC = "5-final.md"

# Possible next steps
NextStep = Literal[
    "missing-docs",      # Required documents missing
    "needs-spec",        # 3-spec.md missing or empty
    "needs-tests",       # No tests.json or tests not written
    "red-phase",         # Tests need RED verification
    "needs-impl",        # Tests RED verified, needs implementation
    "tests-failing",     # Implementation exists but tests failing
    "tests-blocked",     # Tests blocked, needs human input
    "needs-final",       # Tests pass but no 5-final.md
    "blocked",           # 5-final.md says BLOCKED
    "complete",          # All done
]


@dataclass
class DocStatus:
    exists: bool = False
    has_content: bool = False


@dataclass
class TestInfo:
    id: str
    name: str
    status: str  # pending, running, passed, failed, blocked
    required: bool
    red_verified: bool
    has_trajectory: bool


@dataclass
class TestsStatus:
    exists: bool = False
    total: int = 0
    passed: int = 0
    failed: int = 0
    blocked: int = 0
    pending: int = 0
    required_passed: int = 0
    required_total: int = 0
    all_red_verified: bool = False
    tests: list[TestInfo] = field(default_factory=list)


@dataclass
class TicketStatus:
    ticket_id: str
    exists: bool = False
    docs: dict[str, DocStatus] = field(default_factory=dict)
    final_status: str | None = None  # COMPLETE, BLOCKED, or None
    tests: TestsStatus = field(default_factory=TestsStatus)
    next_step: str = "missing-docs"
    next_step_detail: str = ""
    tdd_enabled: bool = True


def check_doc(ticket_path: Path, doc_name: str) -> DocStatus:
    """Check if a document exists and has content."""
    doc_path = ticket_path / doc_name
    if not doc_path.exists():
        return DocStatus(exists=False, has_content=False)

    content = doc_path.read_text(encoding="utf-8").strip()
    # Consider content meaningful if > 50 chars (not just template)
    has_content = len(content) > 50
    return DocStatus(exists=True, has_content=has_content)


def parse_final_status(ticket_path: Path) -> str | None:
    """Parse 5-final.md for Status: COMPLETE or BLOCKED."""
    final_path = ticket_path / FINAL_DOC
    if not final_path.exists():
        return None

    content = final_path.read_text(encoding="utf-8")
    # Look for Status: COMPLETE or Status: BLOCKED
    match = re.search(r'Status:\s*(COMPLETE|BLOCKED)', content, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def check_tdd_enabled(ticket_path: Path) -> bool:
    """Check if TDD is enabled for this ticket (default: yes).

    TDD opt-out must be under ## Constraints section:
        ## Constraints
        - TDD: no (trivial: reason)
    """
    def_path = ticket_path / "1-definition.md"
    if not def_path.exists():
        return True  # Default to TDD enabled

    content = def_path.read_text(encoding="utf-8")

    # Find Constraints section
    constraints_match = re.search(
        r'##\s*Constraints\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not constraints_match:
        return True  # No Constraints section, default to TDD enabled

    constraints_section = constraints_match.group(1)
    # Look for TDD: no within Constraints section only
    if re.search(r'TDD:\s*no', constraints_section, re.IGNORECASE):
        return False
    return True


def check_tests(docs_path: Path, ticket_id: str) -> TestsStatus:
    """Check tests.json for test status."""
    tests_path = docs_path / "tests" / "tickets" / ticket_id / "tests.json"

    status = TestsStatus()
    if not tests_path.exists():
        return status

    try:
        data = json.loads(tests_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return status

    status.exists = True
    tests = data.get("tests", [])
    status.total = len(tests)

    all_red_verified = True
    for t in tests:
        test_info = TestInfo(
            id=t.get("id", ""),
            name=t.get("name", ""),
            status=t.get("status", "pending"),
            required=t.get("required", False),
            red_verified=bool(t.get("red_verified")),
            has_trajectory=bool(t.get("trajectory", [])),
        )
        status.tests.append(test_info)

        test_status = t.get("status", "pending")
        required = t.get("required", False)

        if test_status == "passed":
            status.passed += 1
            if required:
                status.required_passed += 1
        elif test_status == "failed":
            status.failed += 1
        elif test_status == "blocked":
            status.blocked += 1
        else:  # pending, running
            status.pending += 1

        if required:
            status.required_total += 1

        if not t.get("red_verified"):
            all_red_verified = False

    status.all_red_verified = all_red_verified and status.total > 0
    return status


def determine_next_step(status: TicketStatus) -> tuple[str, str]:
    """Determine the next step based on ticket status."""

    # Check if ticket exists
    if not status.exists:
        return "missing-docs", f"Ticket directory {status.ticket_id} not found"

    # Check required docs
    missing_docs = []
    for doc in REQUIRED_DOCS:
        if doc not in status.docs or not status.docs[doc].exists:
            missing_docs.append(doc)

    if missing_docs:
        return "missing-docs", f"Missing: {', '.join(missing_docs)}"

    # Check if 3-spec.md has content (for TDD tickets)
    if status.tdd_enabled:
        spec_status = status.docs.get("3-spec.md")
        if spec_status and not spec_status.has_content:
            return "needs-spec", "3-spec.md exists but needs test specification"

    # Check final status first (might be manually marked)
    if status.final_status == "COMPLETE":
        return "complete", "Ticket marked COMPLETE in 5-final.md"

    if status.final_status == "BLOCKED":
        return "blocked", "Ticket marked BLOCKED in 5-final.md"

    # For TDD tickets, check tests
    if status.tdd_enabled:
        if not status.tests.exists:
            return "needs-tests", "No tests.json found - create test definitions"

        if status.tests.total == 0:
            return "needs-tests", "tests.json exists but has no tests defined"

        # Check if any tests are blocked
        if status.tests.blocked > 0:
            blocked_tests = [t.id for t in status.tests.tests if t.status == "blocked"]
            return "tests-blocked", f"Blocked tests: {', '.join(blocked_tests)}"

        # Check RED phase (tests need red_verified before implementation)
        if not status.tests.all_red_verified:
            unverified = [t.id for t in status.tests.tests if not t.red_verified]
            return "red-phase", f"Run RED phase for: {', '.join(unverified)}"

        # Check if tests are failing
        if status.tests.failed > 0:
            failed_tests = [t.id for t in status.tests.tests if t.status == "failed"]
            return "tests-failing", f"Failing tests: {', '.join(failed_tests)}"

        # Check if tests are pending (need implementation)
        if status.tests.pending > 0:
            pending_tests = [t.id for t in status.tests.tests if t.status == "pending"]
            return "needs-impl", f"Implement to pass: {', '.join(pending_tests)}"

        # All tests pass, check if required tests pass
        if status.tests.required_passed < status.tests.required_total:
            return "needs-impl", f"Required tests: {status.tests.required_passed}/{status.tests.required_total} passed"

    # All tests pass (or TDD disabled), check for 5-final.md
    final_status = status.docs.get(FINAL_DOC)
    if not final_status or not final_status.exists:
        return "needs-final", "Tests pass - create 5-final.md with Status: COMPLETE"

    if not final_status.has_content:
        return "needs-final", "5-final.md exists but needs Status: COMPLETE"

    # If we have 5-final.md but no status parsed
    if not status.final_status:
        return "needs-final", "5-final.md missing Status: COMPLETE or BLOCKED"

    return "complete", "All requirements met"


def check_ticket(ticket_id: str, docs_path: Path) -> TicketStatus:
    """Check complete ticket status."""
    status = TicketStatus(ticket_id=ticket_id)

    ticket_path = docs_path / "tickets" / ticket_id
    if not ticket_path.exists():
        status.next_step, status.next_step_detail = determine_next_step(status)
        return status

    status.exists = True

    # Check TDD setting
    status.tdd_enabled = check_tdd_enabled(ticket_path)

    # Check all documents
    all_docs = REQUIRED_DOCS + [PROGRESS_DOC, FINAL_DOC]
    for doc in all_docs:
        status.docs[doc] = check_doc(ticket_path, doc)

    # Parse final status
    status.final_status = parse_final_status(ticket_path)

    # Check tests
    status.tests = check_tests(docs_path, ticket_id)

    # Determine next step
    status.next_step, status.next_step_detail = determine_next_step(status)

    return status


def format_output(status: TicketStatus, as_json: bool = False) -> str:
    """Format the status output."""
    if as_json:
        # Convert to dict, handling dataclasses
        data = asdict(status)
        return json.dumps(data, indent=2)

    lines = []
    lines.append(f"# Ticket Status: {status.ticket_id}")
    lines.append("")

    if not status.exists:
        lines.append(f"ERROR: Ticket not found")
        lines.append(f"Next: {status.next_step_detail}")
        return "\n".join(lines)

    # Documents
    lines.append("## Documents")
    lines.append("")
    lines.append("| Document | Exists | Content |")
    lines.append("|----------|--------|---------|")
    for doc in REQUIRED_DOCS + [PROGRESS_DOC, FINAL_DOC]:
        doc_status = status.docs.get(doc, DocStatus())
        exists = "OK" if doc_status.exists else "MISSING"
        content = "OK" if doc_status.has_content else ("empty" if doc_status.exists else "-")
        lines.append(f"| {doc} | {exists} | {content} |")
    lines.append("")

    # TDD Status
    lines.append(f"## TDD: {'enabled' if status.tdd_enabled else 'disabled'}")
    lines.append("")

    # Tests
    if status.tdd_enabled:
        lines.append("## Tests")
        lines.append("")
        if status.tests.exists:
            lines.append(f"Total: {status.tests.total} | "
                        f"Passed: {status.tests.passed} | "
                        f"Failed: {status.tests.failed} | "
                        f"Blocked: {status.tests.blocked} | "
                        f"Pending: {status.tests.pending}")
            lines.append(f"Required: {status.tests.required_passed}/{status.tests.required_total} passed")
            lines.append(f"RED verified: {'all' if status.tests.all_red_verified else 'incomplete'}")
            lines.append("")

            if status.tests.tests:
                lines.append("| Test | Status | Required | RED |")
                lines.append("|------|--------|----------|-----|")
                for t in status.tests.tests:
                    red = "OK" if t.red_verified else "-"
                    req = "yes" if t.required else "no"
                    lines.append(f"| {t.id} | {t.status} | {req} | {red} |")
                lines.append("")
        else:
            lines.append("No tests.json found")
            lines.append("")

    # Final Status
    lines.append("## Status")
    lines.append("")
    if status.final_status:
        lines.append(f"5-final.md: **{status.final_status}**")
    else:
        lines.append("5-final.md: not set")
    lines.append("")

    # Next Step
    lines.append("## Next Step")
    lines.append("")
    step_emoji = {
        "complete": "COMPLETE",
        "blocked": "BLOCKED",
        "missing-docs": "CREATE DOCS",
        "needs-spec": "WRITE SPEC",
        "needs-tests": "WRITE TESTS",
        "red-phase": "RUN RED",
        "needs-impl": "IMPLEMENT",
        "tests-failing": "FIX TESTS",
        "tests-blocked": "UNBLOCK",
        "needs-final": "FINALIZE",
    }
    lines.append(f"**{step_emoji.get(status.next_step, status.next_step)}**")
    lines.append(f"{status.next_step_detail}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check ticket completion status based on KB rules"
    )
    parser.add_argument("ticket_id", help="Ticket ID (e.g., T00001)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--docs-path",
        default=".pmc/docs",
        help="Path to docs directory (default: .pmc/docs)"
    )

    args = parser.parse_args()

    docs_path = Path(args.docs_path)
    if not docs_path.exists():
        print(f"Error: Docs path not found: {docs_path}", file=sys.stderr)
        sys.exit(1)

    status = check_ticket(args.ticket_id, docs_path)
    print(format_output(status, as_json=args.json))

    # Exit code based on status
    if status.next_step == "complete":
        sys.exit(0)
    elif status.next_step == "blocked":
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
