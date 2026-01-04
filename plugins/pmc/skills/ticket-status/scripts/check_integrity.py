#!/usr/bin/env python3
"""
Check KB integrity: index.md matches directories, roadmap has all active items.

Usage:
    python check_integrity.py
    python check_integrity.py --json
    python check_integrity.py --docs-path .pmc/docs
"""

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict


@dataclass
class IntegrityIssue:
    type: str  # missing_index, orphan_index, missing_roadmap, stale_roadmap
    item: str  # T00001 or I00042
    detail: str


@dataclass
class IntegrityStatus:
    valid: bool = True
    tickets_in_dir: list[str] = field(default_factory=list)
    tickets_in_index: list[str] = field(default_factory=list)
    tickets_in_roadmap: list[str] = field(default_factory=list)
    issues_in_dir: list[str] = field(default_factory=list)
    issues_in_index: list[str] = field(default_factory=list)
    issues_in_roadmap: list[str] = field(default_factory=list)
    archived_tickets: list[str] = field(default_factory=list)
    archived_issues: list[str] = field(default_factory=list)
    issues: list[IntegrityIssue] = field(default_factory=list)


def get_directories(path: Path, prefix: str) -> list[str]:
    """Get list of directories matching prefix (T or I)."""
    if not path.exists():
        return []
    return sorted([
        d.name for d in path.iterdir()
        if d.is_dir() and d.name.startswith(prefix)
    ])


def parse_index(index_path: Path) -> list[str]:
    """Parse index.md to get list of items."""
    if not index_path.exists():
        return []

    content = index_path.read_text(encoding="utf-8")
    # Match T00001 or I00001 at start of line
    items = re.findall(r'^([TI]\d+)', content, re.MULTILINE)
    return sorted(set(items))


def parse_roadmap(roadmap_path: Path) -> tuple[list[str], list[str]]:
    """Parse roadmap.md to get tickets and issues mentioned."""
    if not roadmap_path.exists():
        return [], []

    content = roadmap_path.read_text(encoding="utf-8")

    # Find all ticket references (T followed by digits)
    tickets = re.findall(r'\b(T\d+)\b', content)
    # Find all issue references (I followed by digits)
    issues = re.findall(r'\b(I\d+)\b', content)

    return sorted(set(tickets)), sorted(set(issues))


def check_integrity(docs_path: Path) -> IntegrityStatus:
    """Check KB integrity."""
    status = IntegrityStatus()

    # Get active directories
    tickets_path = docs_path / "tickets"
    issues_path = docs_path / "issues"

    status.tickets_in_dir = get_directories(tickets_path, "T")
    status.issues_in_dir = get_directories(issues_path, "I")

    # Get archived directories
    status.archived_tickets = get_directories(tickets_path / "archive", "T")
    status.archived_issues = get_directories(issues_path / "archive", "I")

    # Parse indexes
    status.tickets_in_index = parse_index(tickets_path / "index.md")
    status.issues_in_index = parse_index(issues_path / "index.md")

    # Parse roadmap
    roadmap_path = docs_path / "3-plan" / "roadmap.md"
    roadmap_tickets, roadmap_issues = parse_roadmap(roadmap_path)
    status.tickets_in_roadmap = roadmap_tickets
    status.issues_in_roadmap = roadmap_issues

    # Check tickets: directory exists but not in index
    for ticket in status.tickets_in_dir:
        if ticket not in status.tickets_in_index:
            status.issues.append(IntegrityIssue(
                type="missing_index",
                item=ticket,
                detail=f"{ticket} directory exists but not in tickets/index.md"
            ))
            status.valid = False

    # Check tickets: in index but directory doesn't exist
    for ticket in status.tickets_in_index:
        if ticket not in status.tickets_in_dir and ticket not in status.archived_tickets:
            status.issues.append(IntegrityIssue(
                type="orphan_index",
                item=ticket,
                detail=f"{ticket} in index.md but directory not found"
            ))
            status.valid = False

    # Check tickets: active but not in roadmap
    for ticket in status.tickets_in_dir:
        if ticket not in status.tickets_in_roadmap:
            status.issues.append(IntegrityIssue(
                type="missing_roadmap",
                item=ticket,
                detail=f"{ticket} is active but not in roadmap.md"
            ))
            status.valid = False

    # Check tickets: in roadmap but archived (stale reference)
    for ticket in status.tickets_in_roadmap:
        if ticket in status.archived_tickets:
            status.issues.append(IntegrityIssue(
                type="stale_roadmap",
                item=ticket,
                detail=f"{ticket} in roadmap.md but already archived"
            ))
            status.valid = False

    # Same checks for issues
    for issue in status.issues_in_dir:
        if issue not in status.issues_in_index:
            status.issues.append(IntegrityIssue(
                type="missing_index",
                item=issue,
                detail=f"{issue} directory exists but not in issues/index.md"
            ))
            status.valid = False

    for issue in status.issues_in_index:
        if issue not in status.issues_in_dir and issue not in status.archived_issues:
            status.issues.append(IntegrityIssue(
                type="orphan_index",
                item=issue,
                detail=f"{issue} in index.md but directory not found"
            ))
            status.valid = False

    for issue in status.issues_in_dir:
        if issue not in status.issues_in_roadmap:
            status.issues.append(IntegrityIssue(
                type="missing_roadmap",
                item=issue,
                detail=f"{issue} is active but not in roadmap.md"
            ))
            status.valid = False

    for issue in status.issues_in_roadmap:
        if issue in status.archived_issues:
            status.issues.append(IntegrityIssue(
                type="stale_roadmap",
                item=issue,
                detail=f"{issue} in roadmap.md but already archived"
            ))
            status.valid = False

    return status


def format_output(status: IntegrityStatus, as_json: bool = False) -> str:
    """Format the status output."""
    if as_json:
        data = asdict(status)
        # Convert IntegrityIssue objects to dicts
        data["issues"] = [asdict(i) for i in status.issues]
        return json.dumps(data, indent=2)

    lines = []
    lines.append("# KB Integrity Check")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Type | Active | Archived | In Index | In Roadmap |")
    lines.append(f"|------|--------|----------|----------|------------|")
    lines.append(f"| Tickets | {len(status.tickets_in_dir)} | {len(status.archived_tickets)} | {len(status.tickets_in_index)} | {len(status.tickets_in_roadmap)} |")
    lines.append(f"| Issues | {len(status.issues_in_dir)} | {len(status.archived_issues)} | {len(status.issues_in_index)} | {len(status.issues_in_roadmap)} |")
    lines.append("")

    # Issues
    if status.issues:
        lines.append("## Issues Found")
        lines.append("")
        lines.append("| Type | Item | Detail |")
        lines.append("|------|------|--------|")
        for issue in status.issues:
            lines.append(f"| {issue.type} | {issue.item} | {issue.detail} |")
        lines.append("")

    # Result
    lines.append("## Result")
    lines.append("")
    if status.valid:
        lines.append("**VALID** - All integrity checks passed")
    else:
        lines.append(f"**INVALID** - {len(status.issues)} issues found")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check KB integrity: indexes and roadmap consistency"
    )
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

    status = check_integrity(docs_path)
    print(format_output(status, as_json=args.json))

    sys.exit(0 if status.valid else 1)


if __name__ == "__main__":
    main()
