#!/usr/bin/env python3
"""
Check phase completion status by verifying all tickets in phase are complete.

Usage:
    python check_phase.py 1                    # Check phase 1
    python check_phase.py 1 --json
    python check_phase.py 1 --docs-path .pmc/docs
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Literal


@dataclass
class TicketSummary:
    ticket_id: str
    exists: bool
    has_final: bool
    final_status: str | None  # COMPLETE, BLOCKED, None
    next_step: str


@dataclass
class PhaseStatus:
    phase_id: str
    found: bool = False
    goal: str = ""
    tickets: list[TicketSummary] = field(default_factory=list)
    total: int = 0
    complete: int = 0
    blocked: int = 0
    in_progress: int = 0
    phase_complete: bool = False
    next_step: str = ""
    next_ticket: str | None = None


def parse_roadmap_phase(roadmap_path: Path, phase_id: str) -> tuple[bool, str, list[str]]:
    """Parse roadmap.md to find phase and its tickets.

    Supports multiple phase header formats:
    - ### Phase N: Description
    - ### Phase N - Description
    - ### feat-name: Phase N - Description
    - ### feat-name Phase N: Description
    """
    if not roadmap_path.exists():
        return False, "", []

    content = roadmap_path.read_text(encoding="utf-8")

    # More flexible pattern that matches:
    # ### Phase N: Description
    # ### Phase N - Description
    # ### feat-name: Phase N - Description
    # ### feat-name Phase N: Description
    phase_pattern = rf'###\s*(?:[\w-]+[:\s]+)?Phase\s*{phase_id}[:\s-]+([^\n]*)\n(.*?)(?=\n###|\Z)'
    match = re.search(phase_pattern, content, re.IGNORECASE | re.DOTALL)

    if not match:
        return False, "", []

    phase_title = match.group(1).strip()
    phase_content = match.group(2)

    # Extract goal if present
    goal_match = re.search(r'\*\*Goal:\*\*\s*([^\n]+)', phase_content)
    goal = goal_match.group(1).strip() if goal_match else phase_title

    # Extract ticket IDs
    tickets = re.findall(r'\b(T\d+)\b', phase_content)

    return True, goal, list(dict.fromkeys(tickets))  # Remove duplicates, keep order


def check_ticket_status(ticket_id: str, docs_path: Path) -> TicketSummary:
    """Check individual ticket status using check_ticket.py logic."""
    ticket_path = docs_path / "tickets" / ticket_id

    summary = TicketSummary(
        ticket_id=ticket_id,
        exists=False,
        has_final=False,
        final_status=None,
        next_step="missing"
    )

    if not ticket_path.exists():
        return summary

    summary.exists = True

    # Check 5-final.md
    final_path = ticket_path / "5-final.md"
    if final_path.exists():
        summary.has_final = True
        content = final_path.read_text(encoding="utf-8")
        status_match = re.search(r'Status:\s*(COMPLETE|BLOCKED)', content, re.IGNORECASE)
        if status_match:
            summary.final_status = status_match.group(1).upper()
            summary.next_step = "complete" if summary.final_status == "COMPLETE" else "blocked"
        else:
            summary.next_step = "needs-final-status"
    else:
        # Check what's missing
        required_docs = ["1-definition.md", "2-plan.md", "3-spec.md"]
        missing = [d for d in required_docs if not (ticket_path / d).exists()]
        if missing:
            summary.next_step = "missing-docs"
        else:
            # Has docs but no 5-final.md - in progress
            summary.next_step = "in-progress"

    return summary


def check_phase(phase_id: str, docs_path: Path) -> PhaseStatus:
    """Check complete phase status."""
    status = PhaseStatus(phase_id=phase_id)

    roadmap_path = docs_path / "3-plan" / "roadmap.md"
    found, goal, tickets = parse_roadmap_phase(roadmap_path, phase_id)

    if not found:
        status.next_step = f"Phase {phase_id} not found in roadmap.md"
        return status

    status.found = True
    status.goal = goal
    status.total = len(tickets)

    # Check each ticket
    for ticket_id in tickets:
        ticket_summary = check_ticket_status(ticket_id, docs_path)
        status.tickets.append(ticket_summary)

        if ticket_summary.final_status == "COMPLETE":
            status.complete += 1
        elif ticket_summary.final_status == "BLOCKED":
            status.blocked += 1
        else:
            status.in_progress += 1
            if status.next_ticket is None:
                status.next_ticket = ticket_id

    # Determine phase status
    if status.total == 0:
        status.next_step = "No tickets in phase"
    elif status.blocked > 0:
        status.next_step = f"{status.blocked} ticket(s) blocked"
    elif status.complete == status.total:
        status.phase_complete = True
        status.next_step = "Phase complete - ready to archive"
    else:
        remaining = status.total - status.complete
        status.next_step = f"{remaining} ticket(s) remaining - next: {status.next_ticket}"

    return status


def format_output(status: PhaseStatus, as_json: bool = False) -> str:
    """Format the status output."""
    if as_json:
        data = asdict(status)
        return json.dumps(data, indent=2)

    lines = []
    lines.append(f"# Phase {status.phase_id} Status")
    lines.append("")

    if not status.found:
        lines.append(f"ERROR: {status.next_step}")
        return "\n".join(lines)

    lines.append(f"**Goal:** {status.goal}")
    lines.append("")

    # Progress bar
    if status.total > 0:
        pct = (status.complete / status.total) * 100
        filled = int(pct / 5)  # 20 chars total
        bar = "█" * filled + "░" * (20 - filled)
        lines.append(f"Progress: [{bar}] {pct:.0f}%")
        lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Status | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Complete | {status.complete} |")
    lines.append(f"| Blocked | {status.blocked} |")
    lines.append(f"| In Progress | {status.in_progress} |")
    lines.append(f"| **Total** | **{status.total}** |")
    lines.append("")

    # Tickets
    lines.append("## Tickets")
    lines.append("")
    lines.append("| Ticket | Status | Next Step |")
    lines.append("|--------|--------|-----------|")
    for t in status.tickets:
        status_str = t.final_status if t.final_status else "in-progress"
        lines.append(f"| {t.ticket_id} | {status_str} | {t.next_step} |")
    lines.append("")

    # Result
    lines.append("## Next Step")
    lines.append("")
    if status.phase_complete:
        lines.append("**PHASE COMPLETE**")
        lines.append("Ready to:")
        lines.append("1. Archive all phase tickets")
        lines.append("2. Update 3-plan/archive.md")
        lines.append("3. Run /pmc:reflect for phase-level learnings")
    else:
        lines.append(f"**{status.next_step}**")
        if status.next_ticket:
            lines.append(f"Continue with: {status.next_ticket}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check phase completion status"
    )
    parser.add_argument("phase_id", help="Phase number (e.g., 1, 2)")
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

    status = check_phase(args.phase_id, docs_path)
    print(format_output(status, as_json=args.json))

    # Exit codes: 0=complete, 1=in-progress, 2=blocked, 3=not-found
    if not status.found:
        sys.exit(3)
    elif status.phase_complete:
        sys.exit(0)
    elif status.blocked > 0:
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
