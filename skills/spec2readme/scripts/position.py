#!/usr/bin/env python3
"""Position tracker for spec2readme skill.

Tracks which OpenSpec changes have been processed or skipped for README documentation.
Uses change folder names (from openspec/changes/ or openspec/changes/archive/)
as stable identifiers.

Position file: <project-root>/spec2readme/.spec2readme-position.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

from utils import find_project_root


@dataclass
class Position:
    processed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    updated_at: Optional[str] = None


def get_position_path(project_root: Optional[Path] = None) -> Path:
    if project_root is None:
        project_root = find_project_root()
    return project_root / "spec2readme" / ".spec2readme-position.json"


def read_position(project_root: Optional[Path] = None) -> Position:
    pos_path = get_position_path(project_root)
    if not pos_path.exists():
        return Position()
    try:
        data = json.loads(pos_path.read_text(encoding="utf-8"))
        return Position(**data)
    except (json.JSONDecodeError, TypeError):
        return Position()


def write_position(position: Position, project_root: Optional[Path] = None) -> None:
    pos_path = get_position_path(project_root)
    pos_path.parent.mkdir(parents=True, exist_ok=True)
    position.updated_at = datetime.now().isoformat()
    pos_path.write_text(
        json.dumps(asdict(position), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _filter_valid_dir_names(dir_names: list[str], project_root: Optional[Path] = None) -> list[str]:
    """Return only dir_names that correspond to existing change directories."""
    valid = {c["dir_name"] for c in find_changes(project_root)}
    valid_names = []
    for d in dir_names:
        if d in valid:
            valid_names.append(d)
        else:
            print(f"Warning: '{d}' is not a valid change directory, skipping", file=sys.stderr)
    return valid_names


def mark_processed(dir_names: list[str], project_root: Optional[Path] = None) -> tuple[Position, list[str]]:
    valid_names = _filter_valid_dir_names(dir_names, project_root)
    pos = read_position(project_root)
    for d in valid_names:
        if d not in pos.processed:
            pos.processed.append(d)
        pos.skipped = [s for s in pos.skipped if s != d]
    write_position(pos, project_root)
    return pos, valid_names


def mark_skipped(dir_names: list[str], project_root: Optional[Path] = None) -> tuple[Position, list[str]]:
    valid_names = _filter_valid_dir_names(dir_names, project_root)
    pos = read_position(project_root)
    for d in valid_names:
        if d not in pos.skipped:
            pos.skipped.append(d)
        pos.processed = [p for p in pos.processed if p != d]
    write_position(pos, project_root)
    return pos, valid_names


def reset_position(project_root: Optional[Path] = None) -> None:
    write_position(Position(), project_root)


def unskip_changes(dir_names: list[str], project_root: Optional[Path] = None) -> Position:
    pos = read_position(project_root)
    for d in dir_names:
        pos.skipped = [s for s in pos.skipped if s != d]
    write_position(pos, project_root)
    return pos


def find_changes(project_root: Optional[Path] = None) -> list[dict]:
    if project_root is None:
        project_root = find_project_root()

    changes_dir = project_root / "openspec" / "changes"
    if not changes_dir.is_dir():
        return []

    changes = []
    for entry in sorted(changes_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name == "archive":
            continue
        changes.append({
            "dir_name": entry.name,
            "path": str(entry),
            "has_proposal": (entry / "proposal.md").exists(),
            "has_design": (entry / "design.md").exists(),
            "has_tasks": (entry / "tasks.md").exists(),
        })

    archive_dir = changes_dir / "archive"
    if archive_dir.is_dir():
        for entry in sorted(archive_dir.iterdir()):
            if not entry.is_dir():
                continue
            changes.append({
                "dir_name": entry.name,
                "path": str(entry),
                "has_proposal": (entry / "proposal.md").exists(),
                "has_design": (entry / "design.md").exists(),
                "has_tasks": (entry / "tasks.md").exists(),
            })

    changes.sort(key=lambda c: c["dir_name"])
    return changes


def find_pending_changes(project_root: Optional[Path] = None) -> list[dict]:
    pos = read_position(project_root)
    changes = find_changes(project_root)
    if not changes:
        return []
    return [
        c for c in changes
        if c["dir_name"] not in pos.processed and c["dir_name"] not in pos.skipped
    ]


def find_all_changes_with_status(project_root: Optional[Path] = None) -> list[dict]:
    pos = read_position(project_root)
    changes = find_changes(project_root)
    for c in changes:
        if c["dir_name"] in pos.processed:
            c["status"] = "processed"
        elif c["dir_name"] in pos.skipped:
            c["status"] = "skipped"
        else:
            c["status"] = "pending"
    return changes


def main():
    parser = argparse.ArgumentParser(description="OpenSpec change position tracker (spec2readme)")
    parser.add_argument("--print-root", action="store_true", help="Print resolved project root path and exit")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show current position (processed + skipped lists)")
    sub.add_parser("list", help="List all changes with status")
    sub.add_parser("pending", help="List unprocessed + unskipped changes")

    p_processed = sub.add_parser("processed", help="Mark change(s) as processed")
    p_processed.add_argument("dir_names", nargs="+", help="Change dir name(s)")

    p_skipped = sub.add_parser("skipped", help="Mark change(s) as skipped")
    p_skipped.add_argument("dir_names", nargs="+", help="Change dir name(s)")

    p_unskip = sub.add_parser("unskip", help="Remove change(s) from skipped list")
    p_unskip.add_argument("dir_names", nargs="+", help="Change dir name(s)")

    sub.add_parser("reset", help="Reset position (clear all tracking)")

    args = parser.parse_args()

    if args.print_root:
        print(str(find_project_root()))
        return

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "status":
        pos = read_position()
        print(json.dumps(asdict(pos), ensure_ascii=False, indent=2))

    elif args.command == "list":
        all_changes = find_all_changes_with_status()
        if not all_changes:
            print("No changes found.")
            return
        for c in all_changes:
            flag = {"processed": "[P]", "skipped": "[S]", "pending": "[ ]"}[c["status"]]
            missing = "!" if not c["has_proposal"] else ""
            print(f"  {flag} {c['dir_name']}{missing}")

    elif args.command == "pending":
        pending = find_pending_changes()
        if not pending:
            print("No unprocessed changes.")
            return
        for c in pending:
            print(f"  {c['dir_name']}")

    elif args.command == "processed":
        pos, valid_names = mark_processed(args.dir_names)
        print(f"Processed {len(valid_names)} change(s).")

    elif args.command == "skipped":
        pos, valid_names = mark_skipped(args.dir_names)
        print(f"Skipped {len(valid_names)} change(s).")

    elif args.command == "unskip":
        pos = unskip_changes(args.dir_names)
        print(f"Unskipped {len(args.dir_names)} change(s).")

    elif args.command == "reset":
        reset_position()
        print("Position reset.")


if __name__ == "__main__":
    main()
