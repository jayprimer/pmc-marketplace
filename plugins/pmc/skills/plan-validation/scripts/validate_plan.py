#!/usr/bin/env python3
"""Validate planning documents for completeness before implementation.

Checks:
1. Ambiguity - Open questions resolved, no TBD/TODO markers
2. Prerequisites - Tooling, env setup, repo management documented
3. Testing - All test methods clearly identified with verification steps

Exit codes:
  0 - Plan is valid and ready for implementation
  1 - Plan has issues that need resolution
  2 - Plan has blocking issues (missing critical sections)
  3 - Ticket not found or invalid structure
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationIssue:
    severity: str  # "error", "warning", "info"
    category: str  # "ambiguity", "prerequisites", "testing"
    message: str
    file: str = ""
    line: int = 0


@dataclass
class ValidationResult:
    ticket_id: str
    status: str  # "valid", "issues", "blocked", "not_found"
    issues: list[ValidationIssue] = field(default_factory=list)
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)

    @property
    def roadmap_marker(self) -> str:
        """Return suggested roadmap marker based on validation status."""
        if self.status == "valid":
            return "[+ ready]"
        elif self.status == "blocked":
            return "[x missing]"
        else:  # "issues" - has warnings or non-blocking errors
            has_questions = any(
                "question" in i.message.lower() or "unresolved" in i.message.lower()
                for i in self.issues
            )
            if has_questions:
                return "[? questions]"
            return "[x missing]"

    def to_dict(self) -> dict:
        return {
            "ticket_id": self.ticket_id,
            "status": self.status,
            "roadmap_marker": self.roadmap_marker,
            "summary": {
                "errors": len([i for i in self.issues if i.severity == "error"]),
                "warnings": len([i for i in self.issues if i.severity == "warning"]),
                "passed": len(self.checks_passed),
                "failed": len(self.checks_failed),
            },
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "message": i.message,
                    "file": i.file,
                    "line": i.line,
                }
                for i in self.issues
            ],
        }


def find_docs_path(start_path: Path) -> Path | None:
    """Find .pmc/docs directory."""
    current = start_path.resolve()
    while current != current.parent:
        docs_path = current / ".pmc" / "docs"
        if docs_path.exists():
            return docs_path
        current = current.parent
    return None


def check_ambiguity(ticket_path: Path, result: ValidationResult) -> None:
    """Check for unresolved ambiguity in planning docs."""

    # Check 2-plan.md for TBD/TODO
    plan_file = ticket_path / "2-plan.md"
    if plan_file.exists():
        content = plan_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Check for TBD/TODO markers
        ambiguity_patterns = [
            (r"\bTBD\b", "TBD marker found"),
            (r"\bTODO\b", "TODO marker found"),
            (r"\b\?\?\?\b", "??? placeholder found"),
            (r"\[TBD\]", "[TBD] placeholder found"),
            (r"\{TBD\}", "{TBD} placeholder found"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, msg in ambiguity_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    result.issues.append(ValidationIssue(
                        severity="error",
                        category="ambiguity",
                        message=f"{msg}: {line.strip()[:60]}",
                        file="2-plan.md",
                        line=i,
                    ))

        # Check Technical Decisions table
        if "Technical Decisions" not in content:
            result.issues.append(ValidationIssue(
                severity="warning",
                category="ambiguity",
                message="No Technical Decisions section found",
                file="2-plan.md",
            ))
        else:
            result.checks_passed.append("Technical Decisions section exists")

    # Check 3-spec.md for Open Questions
    spec_file = ticket_path / "3-spec.md"
    if spec_file.exists():
        content = spec_file.read_text(encoding="utf-8")

        # Check Open Questions section
        open_q_match = re.search(
            r"##\s*Open Questions\s*\n(.*?)(?=\n## [^#]|\Z)",
            content,
            re.DOTALL | re.IGNORECASE
        )

        if open_q_match:
            section = open_q_match.group(1).strip()
            # Check if there are unresolved questions (numbered items without RESOLVED)
            questions = re.findall(r"^\d+\.\s+(.+)$", section, re.MULTILINE)
            unresolved = [q for q in questions if "RESOLVED" not in q.upper()]

            if unresolved:
                for q in unresolved:
                    result.issues.append(ValidationIssue(
                        severity="error",
                        category="ambiguity",
                        message=f"Unresolved question: {q[:60]}",
                        file="3-spec.md",
                    ))
            elif questions:
                result.checks_passed.append(f"All {len(questions)} open questions resolved")
            else:
                result.checks_passed.append("No open questions")

        # Check for TBD in spec
        for i, line in enumerate(content.split("\n"), 1):
            if re.search(r"\bTBD\b|\bTODO\b", line, re.IGNORECASE):
                result.issues.append(ValidationIssue(
                    severity="error",
                    category="ambiguity",
                    message=f"Unresolved marker: {line.strip()[:60]}",
                    file="3-spec.md",
                    line=i,
                ))


def check_prerequisites(ticket_path: Path, result: ValidationResult) -> None:
    """Check that prerequisites are documented and actionable."""

    spec_file = ticket_path / "3-spec.md"
    if not spec_file.exists():
        result.issues.append(ValidationIssue(
            severity="error",
            category="prerequisites",
            message="3-spec.md not found - cannot verify prerequisites",
            file="3-spec.md",
        ))
        return

    content = spec_file.read_text(encoding="utf-8")

    # Check Test Environment Setup section
    env_match = re.search(
        r"##\s*Test Environment Setup\s*\n(.*?)(?=\n## [^#]|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not env_match:
        result.issues.append(ValidationIssue(
            severity="error",
            category="prerequisites",
            message="Missing 'Test Environment Setup' section",
            file="3-spec.md",
        ))
    else:
        section = env_match.group(1)

        # Check for Prerequisites subsection
        if "### Prerequisites" in section or "#### Prerequisites" in section:
            result.checks_passed.append("Prerequisites subsection exists")
        else:
            result.issues.append(ValidationIssue(
                severity="warning",
                category="prerequisites",
                message="No Prerequisites subsection in Test Environment Setup",
                file="3-spec.md",
            ))

        # Check for Environment Variables
        if "Environment Variables" in section:
            # Check if there are actual variables defined
            if re.search(r"```\s*\n\s*```|None required|N/A", section):
                result.checks_passed.append("Environment variables documented (none needed)")
            elif re.search(r"export\s+\w+|```bash", section):
                result.checks_passed.append("Environment variables documented")
            else:
                result.issues.append(ValidationIssue(
                    severity="warning",
                    category="prerequisites",
                    message="Environment Variables section exists but unclear",
                    file="3-spec.md",
                ))

        # Check for Database/State Setup if mentioned
        if re.search(r"database|db|state setup", section, re.IGNORECASE):
            if re.search(r"```|command|script", section, re.IGNORECASE):
                result.checks_passed.append("Database/State setup documented")
            else:
                result.issues.append(ValidationIssue(
                    severity="warning",
                    category="prerequisites",
                    message="Database/State mentioned but setup commands unclear",
                    file="3-spec.md",
                ))

    # Check Mock Data section
    mock_match = re.search(
        r"##\s*Mock Data\s*\n(.*?)(?=\n## [^#]|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if mock_match:
        section = mock_match.group(1)
        if re.search(r"\|.*\|.*\|", section):  # Has table
            result.checks_passed.append("Mock data documented with table")
        elif "None" in section or "N/A" in section:
            result.checks_passed.append("Mock data documented (none needed)")
        else:
            result.issues.append(ValidationIssue(
                severity="warning",
                category="prerequisites",
                message="Mock Data section unclear - use table format",
                file="3-spec.md",
            ))

    # Check 1-definition.md for Dependencies
    def_file = ticket_path / "1-definition.md"
    if def_file.exists():
        def_content = def_file.read_text(encoding="utf-8")
        if "Dependencies:" in def_content:
            deps_match = re.search(r"Dependencies:\s*(.+?)(?:\n|$)", def_content)
            if deps_match:
                deps = deps_match.group(1).strip()
                if deps and deps.lower() not in ["none", "n/a", "-"]:
                    result.checks_passed.append(f"Dependencies documented: {deps[:40]}")
                else:
                    result.checks_passed.append("Dependencies documented (none)")


def check_testing_methods(ticket_path: Path, result: ValidationResult) -> None:
    """Check that testing methods are clearly identified."""

    spec_file = ticket_path / "3-spec.md"
    if not spec_file.exists():
        return

    content = spec_file.read_text(encoding="utf-8")

    # Check Unit Tests section
    unit_match = re.search(
        r"###?\s*Unit Tests\s*\n(.*?)(?=\n###?|\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if unit_match:
        section = unit_match.group(1)
        # Check for table with Input/Expected columns
        if re.search(r"\|\s*Test\s*\|.*\|\s*Input\s*\|.*\|\s*Expected\s*\|", section, re.IGNORECASE):
            result.checks_passed.append("Unit tests have Input/Expected columns")
        elif re.search(r"\|.*\|.*\|.*\|", section):
            result.checks_passed.append("Unit tests documented in table")
        else:
            result.issues.append(ValidationIssue(
                severity="warning",
                category="testing",
                message="Unit tests should use table format with Input/Expected",
                file="3-spec.md",
            ))

    # Check Integration Tests section
    int_match = re.search(
        r"###?\s*Integration Tests\s*\n(.*?)(?=\n###?|\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if int_match:
        section = int_match.group(1)
        # Check for Setup/Action/Verify pattern
        has_setup = bool(re.search(r"\bSetup\b", section, re.IGNORECASE))
        has_action = bool(re.search(r"\bAction\b", section, re.IGNORECASE))
        has_verify = bool(re.search(r"\bVerify\b", section, re.IGNORECASE))

        if has_setup and has_action and has_verify:
            result.checks_passed.append("Integration tests have Setup/Action/Verify")
        else:
            missing = []
            if not has_setup: missing.append("Setup")
            if not has_action: missing.append("Action")
            if not has_verify: missing.append("Verify")
            result.issues.append(ValidationIssue(
                severity="warning",
                category="testing",
                message=f"Integration tests missing: {', '.join(missing)}",
                file="3-spec.md",
            ))

    # Check E2E Test Procedure section - CRITICAL
    e2e_match = re.search(
        r"##\s*E2E Test Procedure\s*\n(.*?)(?=\n## [^#]|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not e2e_match:
        result.issues.append(ValidationIssue(
            severity="error",
            category="testing",
            message="Missing 'E2E Test Procedure' section",
            file="3-spec.md",
        ))
    else:
        section = e2e_match.group(1)

        # Check for required subsections
        required_subs = ["Setup", "Execution", "Verification"]
        for sub in required_subs:
            if f"### {sub}" in section or f"#### {sub}" in section:
                result.checks_passed.append(f"E2E has {sub} subsection")
            else:
                result.issues.append(ValidationIssue(
                    severity="error",
                    category="testing",
                    message=f"E2E Test Procedure missing '{sub}' subsection",
                    file="3-spec.md",
                ))

        # Check for Teardown (optional but recommended)
        if "Teardown" in section:
            result.checks_passed.append("E2E has Teardown subsection")

        # Check Verification has specific checks
        verify_match = re.search(
            r"###?\s*Verification\s*\n(.*?)(?=\n###?|\n##|\Z)",
            section,
            re.DOTALL | re.IGNORECASE
        )
        if verify_match:
            verify_section = verify_match.group(1)
            if re.search(r"\|.*\|.*\|", verify_section):  # Has table
                result.checks_passed.append("E2E Verification has checklist table")
            elif re.search(r"^\s*[-*]\s+", verify_section, re.MULTILINE):  # Has bullets
                result.checks_passed.append("E2E Verification has checklist")
            else:
                result.issues.append(ValidationIssue(
                    severity="warning",
                    category="testing",
                    message="E2E Verification should have specific checks (table or list)",
                    file="3-spec.md",
                ))

        # Check for manual inspection indicators
        manual_patterns = [
            (r"screenshot", "screenshot verification"),
            (r"visual", "visual inspection"),
            (r"manual", "manual check"),
            (r"inspect", "inspection step"),
            (r"observe", "observation step"),
        ]

        manual_found = []
        for pattern, desc in manual_patterns:
            if re.search(pattern, section, re.IGNORECASE):
                manual_found.append(desc)

        if manual_found:
            # Check if manual steps have clear instructions
            if re.search(r"save|capture|record|document", section, re.IGNORECASE):
                result.checks_passed.append(f"Manual verification documented: {', '.join(manual_found[:2])}")
            else:
                result.issues.append(ValidationIssue(
                    severity="warning",
                    category="testing",
                    message=f"Manual steps ({', '.join(manual_found[:2])}) need clear capture/save instructions",
                    file="3-spec.md",
                ))

    # Check Edge Cases section
    edge_match = re.search(
        r"##\s*Edge Cases\s*\n(.*?)(?=\n## [^#]|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if edge_match:
        section = edge_match.group(1)
        if re.search(r"\|.*\|.*\|.*\|", section):  # Has table
            result.checks_passed.append("Edge cases documented in table")
        else:
            result.issues.append(ValidationIssue(
                severity="warning",
                category="testing",
                message="Edge cases should use table format",
                file="3-spec.md",
            ))
    else:
        result.issues.append(ValidationIssue(
            severity="warning",
            category="testing",
            message="No Edge Cases section - consider adding",
            file="3-spec.md",
        ))


def check_repo_management(ticket_path: Path, docs_path: Path, result: ValidationResult) -> None:
    """Check repo management documentation (git worktree/branch)."""

    plan_file = ticket_path / "2-plan.md"
    if not plan_file.exists():
        return

    content = plan_file.read_text(encoding="utf-8")

    # Check if Files to Modify section exists
    if "Files to Modify" in content:
        if re.search(r"\|.*\|.*\|", content):
            result.checks_passed.append("Files to Modify documented")
        else:
            result.issues.append(ValidationIssue(
                severity="warning",
                category="prerequisites",
                message="Files to Modify should use table format",
                file="2-plan.md",
            ))
    else:
        result.issues.append(ValidationIssue(
            severity="warning",
            category="prerequisites",
            message="No 'Files to Modify' section in plan",
            file="2-plan.md",
        ))

    # Check roadmap for ticket entry
    roadmap_file = docs_path / "3-plan" / "roadmap.md"
    if roadmap_file.exists():
        roadmap = roadmap_file.read_text(encoding="utf-8")
        ticket_id = ticket_path.name
        if ticket_id in roadmap:
            result.checks_passed.append(f"{ticket_id} found in roadmap.md")
        else:
            result.issues.append(ValidationIssue(
                severity="warning",
                category="prerequisites",
                message=f"{ticket_id} not found in roadmap.md",
                file="3-plan/roadmap.md",
            ))


def validate_ticket(ticket_id: str, docs_path: Path) -> ValidationResult:
    """Validate a ticket's planning documents."""

    result = ValidationResult(ticket_id=ticket_id, status="valid")

    # Find ticket directory
    ticket_path = docs_path / "tickets" / ticket_id
    if not ticket_path.exists():
        # Check archive
        ticket_path = docs_path / "tickets" / "archive" / ticket_id
        if not ticket_path.exists():
            result.status = "not_found"
            result.issues.append(ValidationIssue(
                severity="error",
                category="prerequisites",
                message=f"Ticket {ticket_id} not found",
            ))
            return result

    # Check required documents exist
    required_docs = ["1-definition.md", "2-plan.md", "3-spec.md"]
    for doc in required_docs:
        if (ticket_path / doc).exists():
            result.checks_passed.append(f"{doc} exists")
        else:
            result.issues.append(ValidationIssue(
                severity="error",
                category="prerequisites",
                message=f"Required document missing: {doc}",
                file=doc,
            ))

    # Run validation checks
    check_ambiguity(ticket_path, result)
    check_prerequisites(ticket_path, result)
    check_testing_methods(ticket_path, result)
    check_repo_management(ticket_path, docs_path, result)

    # Determine overall status
    errors = [i for i in result.issues if i.severity == "error"]
    warnings = [i for i in result.issues if i.severity == "warning"]

    if errors:
        # Check if blocking (missing critical sections)
        critical_missing = any(
            "missing" in i.message.lower() and i.category == "prerequisites"
            for i in errors
        )
        result.status = "blocked" if critical_missing else "issues"
    elif warnings:
        result.status = "issues"
    else:
        result.status = "valid"

    # Add summary checks
    result.checks_failed = [i.message for i in errors]

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Validate planning documents before implementation"
    )
    parser.add_argument("ticket_id", help="Ticket ID (e.g., T00021)")
    parser.add_argument(
        "--docs-path",
        help="Path to .pmc/docs directory",
        default=None,
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format",
    )

    args = parser.parse_args()

    # Find docs path
    if args.docs_path:
        docs_path = Path(args.docs_path)
    else:
        docs_path = find_docs_path(Path.cwd())

    if not docs_path or not docs_path.exists():
        print(json.dumps({
            "ticket_id": args.ticket_id,
            "status": "not_found",
            "error": "Could not find .pmc/docs directory",
        }))
        sys.exit(3)

    # Validate
    result = validate_ticket(args.ticket_id, docs_path)

    # Output
    if args.format == "json":
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Ticket: {result.ticket_id}")
        print(f"Status: {result.status.upper()}")
        print(f"Roadmap marker: {result.roadmap_marker}")
        print()

        if result.checks_passed:
            print("PASSED:")
            for check in result.checks_passed:
                print(f"  [+] {check}")
            print()

        if result.issues:
            print("ISSUES:")
            for issue in result.issues:
                icon = "!" if issue.severity == "error" else "?"
                loc = f" ({issue.file}:{issue.line})" if issue.line else f" ({issue.file})" if issue.file else ""
                print(f"  [{icon}] [{issue.category}] {issue.message}{loc}")

    # Exit code based on status
    exit_codes = {
        "valid": 0,
        "issues": 1,
        "blocked": 2,
        "not_found": 3,
    }
    sys.exit(exit_codes.get(result.status, 1))


if __name__ == "__main__":
    main()
