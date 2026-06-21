#!/usr/bin/env python3
"""Position tracker for spec2md skill.

Tracks which OpenSpec changes have been processed or skipped for articles.
Uses change folder names (from openspec/changes/ or openspec/changes/archive/)
as stable identifiers — works across archive moves.

Position file: <skill-dir>/.spec2md-position.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Position:
    processed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    updated_at: Optional[str] = None


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
POSITION_FILE = SKILL_DIR / ".spec2md-position.json"


def get_position_path(project_root: Optional[Path] = None) -> Path:
    return POSITION_FILE


def read_position(project_root: Optional[Path] = None) -> Position:
    pos_path = get_position_path(project_root)
    if not pos_path.exists():
        return Position()
    try:
        data = json.loads(pos_path.read_text(encoding="utf-8"))
        if "last_change_dir" in data and data["last_change_dir"]:
            if data["last_change_dir"] not in data.get("processed", []):
                data.setdefault("processed", []).append(data["last_change_dir"])
            data.pop("last_change", None)
            data.pop("last_change_dir", None)
        return Position(**data)
    except (json.JSONDecodeError, TypeError):
        return Position()


def write_position(position: Position, project_root: Optional[Path] = None) -> None:
    pos_path = get_position_path(project_root)
    position.updated_at = datetime.now().isoformat()
    pos_path.write_text(
        json.dumps(asdict(position), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def mark_processed(dir_names: list[str], project_root: Optional[Path] = None) -> Position:
    pos = read_position(project_root)
    for d in dir_names:
        if d not in pos.processed:
            pos.processed.append(d)
        pos.skipped = [s for s in pos.skipped if s != d]
    write_position(pos, project_root)
    return pos


def mark_skipped(dir_names: list[str], project_root: Optional[Path] = None) -> Position:
    pos = read_position(project_root)
    for d in dir_names:
        if d not in pos.skipped:
            pos.skipped.append(d)
        pos.processed = [p for p in pos.processed if p != d]
    write_position(pos, project_root)
    return pos


def reset_position(project_root: Optional[Path] = None) -> None:
    write_position(Position(), project_root)


def find_changes(project_root: Optional[Path] = None) -> list[dict]:
    """List all changes (active + archived), sorted by folder name."""
    if project_root is None:
        project_root = _find_project_root()

    changes_dir = project_root / "openspec" / "changes"
    if not changes_dir.is_dir():
        return []

    changes = []
    for entry in sorted(changes_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name == "archive":
            continue
        comet_yaml = entry / ".comet.yaml"
        proposal = entry / "proposal.md"
        design = entry / "design.md"
        tasks = entry / "tasks.md"

        changes.append({
            "dir_name": entry.name,
            "path": str(entry),
            "has_comet_yaml": comet_yaml.exists(),
            "has_proposal": proposal.exists(),
            "has_design": design.exists(),
            "has_tasks": tasks.exists(),
        })

    archive_dir = changes_dir / "archive"
    if archive_dir.is_dir():
        for entry in sorted(archive_dir.iterdir()):
            if not entry.is_dir():
                continue
            comet_yaml = entry / ".comet.yaml"
            proposal = entry / "proposal.md"
            design = entry / "design.md"
            tasks = entry / "tasks.md"
            changes.append({
                "dir_name": entry.name,
                "path": str(entry),
                "has_comet_yaml": comet_yaml.exists(),
                "has_proposal": proposal.exists(),
                "has_design": design.exists(),
                "has_tasks": tasks.exists(),
            })

    return changes


def find_pending_changes(project_root: Optional[Path] = None) -> list[dict]:
    """Find changes not yet processed or skipped."""
    pos = read_position(project_root)
    changes = find_changes(project_root)
    if not changes:
        return []
    return [
        c for c in changes
        if c["dir_name"] not in pos.processed and c["dir_name"] not in pos.skipped
    ]


def main():
    parser = argparse.ArgumentParser(description="OpenSpec change position tracker")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show current position (processed + skipped lists)")
    sub.add_parser("list", help="List all changes")
    sub.add_parser("pending", help="List unprocessed + unskipped changes")

    p_processed = sub.add_parser("processed", help="Mark change(s) as processed")
    p_processed.add_argument("dir_names", nargs="+", help="Change dir name(s)")

    p_skipped = sub.add_parser("skipped", help="Mark change(s) as skipped (hide from pending)")
    p_skipped.add_argument("dir_names", nargs="+", help="Change dir name(s)")

    p_unskip = sub.add_parser("unskip", help="Remove change(s) from skipped list")
    p_unskip.add_argument("dir_names", nargs="+", help="Change dir name(s)")

    sub.add_parser("reset", help="Reset position (clear all tracking)")

    args = parser.parse_args()

    if args.command == "status":
        pos = read_position()
        print(json.dumps(asdict(pos), ensure_ascii=False, indent=2))

    elif args.command == "list":
        all_changes = find_changes()
        if not all_changes:
            print("No changes found.")
            return
        pos = read_position()
        for c in all_changes:
            flag = "[P]" if c["dir_name"] in pos.processed else "[S]" if c["dir_name"] in pos.skipped else "[ ]"
            missing = ""
            if not c["has_proposal"]:
                missing += "!"
            print(f"  {flag} {c['dir_name']}{missing}")

    elif args.command == "pending":
        pending = find_pending_changes()
        if not pending:
            print("No unprocessed changes.")
            return
        for c in pending:
            print(f"  {c['dir_name']}")

    elif args.command == "processed":
        pos = mark_processed(args.dir_names)
        print(f"Processed {len(args.dir_names)} change(s).")

    elif args.command == "skipped":
        pos = mark_skipped(args.dir_names)
        print(f"Skipped {len(args.dir_names)} change(s).")

    elif args.command == "unskip":
        pos = read_position()
        for d in args.dir_names:
            pos.skipped = [s for s in pos.skipped if s != d]
        write_position(pos)
        print(f"Unskipped {len(args.dir_names)} change(s).")

    elif args.command == "reset":
        reset_position()
        print("Position reset.")


if __name__ == "__main__":
    main()
