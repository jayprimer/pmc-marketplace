#!/usr/bin/env python3
"""
Check test status: trajectory completeness, RED verification, coverage vs 3-spec.md.

Usage:
    python check_tests.py T00001
    python check_tests.py T00001 --json
    python check_tests.py T00001 --docs-path .pmc/docs
"""

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict


@dataclass
class TestDetail:
    id: str
    name: str
    status: str
    required: bool
    red_verified: bool
    has_trajectory: bool
    trajectory_count: int
    has_red_marker: bool
    has_green_marker: bool
    issues: list[str] = field(default_factory=list)


@dataclass
class SpecCase:
    name: str
    covered: bool
    test_id: str | None = None


@dataclass
class TestsCheckStatus:
    ticket_id: str
    tests_json_exists: bool = False
    spec_exists: bool = False
    total_tests: int = 0
    tests: list[TestDetail] = field(default_factory=list)
    spec_cases: list[SpecCase] = field(default_factory=list)
    coverage_pct: float = 0.0
    all_red_verified: bool = False
    all_trajectories_complete: bool = False
    issues: list[str] = field(default_factory=list)
    valid: bool = False
    next_step: str = ""


def parse_spec_cases(spec_path: Path) -> list[str]:
    """Extract test case names from 3-spec.md."""
    if not spec_path.exists():
        return []

    content = spec_path.read_text(encoding="utf-8")
    cases = []

    # Look for test case tables: | test_name | ... |
    # Or bullet points: - test_name:
    # Or headers: ### test_name

    # Table format: | name | input | expected |
    table_matches = re.findall(r'^\|\s*([a-z_][a-z0-9_]*)\s*\|', content, re.MULTILINE | re.IGNORECASE)
    cases.extend(table_matches)

    # Bullet format: - test_something or * test_something
    bullet_matches = re.findall(r'^[-*]\s*(test_[a-z0-9_]+)', content, re.MULTILINE | re.IGNORECASE)
    cases.extend(bullet_matches)

    # Header format: ### Test: Something or #### test_something
    header_matches = re.findall(r'^#{2,4}\s*(?:Test:\s*)?([A-Za-z][A-Za-z0-9_\s]+)', content, re.MULTILINE)
    # Filter to likely test names
    for h in header_matches:
        h_clean = h.strip().lower().replace(' ', '_')
        if 'test' in h_clean or h_clean.startswith(('unit', 'integration', 'e2e')):
            cases.append(h_clean)

    # Deduplicate and filter out table headers/separators
    seen = set()
    unique = []
    # These are exact header words to exclude, not prefixes
    header_words = {'name', 'test', 'input', 'expected', 'file', 'setup', 'action', 'verify', '---'}
    for c in cases:
        c_lower = c.lower().strip()
        # Exclude empty, seen, exact header matches, and separator patterns
        if (c_lower
            and c_lower not in seen
            and c_lower not in header_words
            and not c_lower.startswith('---')):
            seen.add(c_lower)
            unique.append(c)

    return unique


def check_tests(ticket_id: str, docs_path: Path) -> TestsCheckStatus:
    """Check test status for a ticket."""
    status = TestsCheckStatus(ticket_id=ticket_id)

    # Check 3-spec.md
    spec_path = docs_path / "tickets" / ticket_id / "3-spec.md"
    if spec_path.exists():
        status.spec_exists = True
        spec_cases = parse_spec_cases(spec_path)
        status.spec_cases = [SpecCase(name=c, covered=False) for c in spec_cases]

    # Check tests.json
    tests_path = docs_path / "tests" / "tickets" / ticket_id / "tests.json"
    if not tests_path.exists():
        status.issues.append("tests.json not found")
        status.next_step = "Create tests.json from 3-spec.md"
        return status

    status.tests_json_exists = True

    try:
        data = json.loads(tests_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        status.issues.append(f"Failed to parse tests.json: {e}")
        status.next_step = "Fix tests.json syntax"
        return status

    tests = data.get("tests", [])
    status.total_tests = len(tests)

    if status.total_tests == 0:
        status.issues.append("tests.json has no tests defined")
        status.next_step = "Add test definitions to tests.json"
        return status

    all_red = True
    all_trajectory = True

    for t in tests:
        trajectory = t.get("trajectory", [])
        trajectory_str = " ".join(str(x) for x in trajectory)

        detail = TestDetail(
            id=t.get("id", ""),
            name=t.get("name", ""),
            status=t.get("status", "pending"),
            required=t.get("required", False),
            red_verified=bool(t.get("red_verified")),
            has_trajectory=len(trajectory) > 0,
            trajectory_count=len(trajectory),
            has_red_marker="[RED]" in trajectory_str,
            has_green_marker="[GREEN]" in trajectory_str,
        )

        # Check for issues
        if detail.status == "passed":
            if not detail.has_trajectory:
                detail.issues.append("Passed but no trajectory recorded")
                status.issues.append(f"{detail.id}: passed without trajectory")
            if not detail.red_verified:
                detail.issues.append("Passed but RED phase not verified")
                status.issues.append(f"{detail.id}: missing red_verified")
            if not detail.has_red_marker and detail.has_trajectory:
                detail.issues.append("Trajectory missing [RED] marker")
            if not detail.has_green_marker and detail.has_trajectory:
                detail.issues.append("Trajectory missing [GREEN] marker")

        if not detail.red_verified:
            all_red = False

        if detail.status == "passed" and not detail.has_trajectory:
            all_trajectory = False

        status.tests.append(detail)

        # Check coverage against spec cases
        test_name_lower = detail.name.lower().replace(' ', '_')
        test_id_lower = detail.id.lower()
        for sc in status.spec_cases:
            sc_lower = sc.name.lower()
            if sc_lower in test_name_lower or sc_lower in test_id_lower or test_name_lower in sc_lower:
                sc.covered = True
                sc.test_id = detail.id

    status.all_red_verified = all_red
    status.all_trajectories_complete = all_trajectory

    # Calculate coverage
    if status.spec_cases:
        covered = sum(1 for sc in status.spec_cases if sc.covered)
        status.coverage_pct = (covered / len(status.spec_cases)) * 100

    # Determine overall status
    if status.issues:
        status.valid = False
        if not all_red:
            status.next_step = "Run RED phase for tests missing red_verified"
        elif not all_trajectory:
            status.next_step = "Re-run tests and record trajectory"
        else:
            status.next_step = "Fix issues listed above"
    else:
        status.valid = True
        # Check if any tests still pending
        pending = [t for t in status.tests if t.status == "pending"]
        failed = [t for t in status.tests if t.status == "failed"]
        blocked = [t for t in status.tests if t.status == "blocked"]

        if blocked:
            status.next_step = f"Resolve blocked tests: {', '.join(t.id for t in blocked)}"
        elif failed:
            status.next_step = f"Fix failing tests: {', '.join(t.id for t in failed)}"
        elif pending:
            if not all_red:
                status.next_step = f"Run RED phase: {', '.join(t.id for t in pending if not t.red_verified)}"
            else:
                status.next_step = f"Implement to pass: {', '.join(t.id for t in pending)}"
        else:
            status.next_step = "All tests passed with valid trajectory"

    return status


def format_output(status: TestsCheckStatus, as_json: bool = False) -> str:
    """Format the status output."""
    if as_json:
        data = asdict(status)
        return json.dumps(data, indent=2)

    lines = []
    lines.append(f"# Test Status: {status.ticket_id}")
    lines.append("")

    if not status.tests_json_exists:
        lines.append("ERROR: tests.json not found")
        lines.append(f"Next: {status.next_step}")
        return "\n".join(lines)

    # Summary
    lines.append("## Summary")
    lines.append("")
    passed = sum(1 for t in status.tests if t.status == "passed")
    failed = sum(1 for t in status.tests if t.status == "failed")
    blocked = sum(1 for t in status.tests if t.status == "blocked")
    pending = sum(1 for t in status.tests if t.status == "pending")

    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total tests | {status.total_tests} |")
    lines.append(f"| Passed | {passed} |")
    lines.append(f"| Failed | {failed} |")
    lines.append(f"| Blocked | {blocked} |")
    lines.append(f"| Pending | {pending} |")
    lines.append(f"| RED verified | {'all' if status.all_red_verified else 'incomplete'} |")
    lines.append(f"| Trajectories | {'complete' if status.all_trajectories_complete else 'incomplete'} |")
    lines.append("")

    # Tests detail
    lines.append("## Tests")
    lines.append("")
    lines.append("| ID | Name | Status | RED | Trajectory | Issues |")
    lines.append("|----|------|--------|-----|------------|--------|")
    for t in status.tests:
        red = "+" if t.red_verified else "x"
        traj = f"{t.trajectory_count}" if t.has_trajectory else "none"
        issues = "; ".join(t.issues) if t.issues else "-"
        lines.append(f"| {t.id} | {t.name[:30]} | {t.status} | {red} | {traj} | {issues} |")
    lines.append("")

    # Coverage
    if status.spec_cases:
        lines.append("## Coverage vs 3-spec.md")
        lines.append("")
        lines.append(f"Coverage: {status.coverage_pct:.0f}%")
        lines.append("")
        lines.append("| Spec Case | Covered | Test |")
        lines.append("|-----------|---------|------|")
        for sc in status.spec_cases:
            covered = "+" if sc.covered else "x"
            test = sc.test_id or "-"
            lines.append(f"| {sc.name} | {covered} | {test} |")
        lines.append("")

    # Issues
    if status.issues:
        lines.append("## Issues")
        lines.append("")
        for issue in status.issues:
            lines.append(f"- {issue}")
        lines.append("")

    # Next step
    lines.append("## Next Step")
    lines.append("")
    lines.append(f"**{status.next_step}**")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check test status: trajectory, RED verification, coverage"
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

    status = check_tests(args.ticket_id, docs_path)
    print(format_output(status, as_json=args.json))

    # Exit codes: 0=valid, 1=issues
    sys.exit(0 if status.valid and not status.issues else 1)


if __name__ == "__main__":
    main()
