#!/usr/bin/env python3
"""Position tracker for wechat-article skill.

Tracks which Comet changes have been processed for WeChat articles.
Position file: <project-root>/.wechat-article-position.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Position:
    last_change: Optional[str] = None
    last_change_dir: Optional[str] = None
    updated_at: Optional[str] = None


POSITION_FILE = ".wechat-article-position.json"


def _find_project_root() -> Path:
    """Walk up from cwd to find project root (has .git dir)."""
    cwd = Path.cwd().resolve()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").is_dir():
            return parent
    return cwd


def get_position_path(project_root: Optional[Path] = None) -> Path:
    if project_root is None:
        project_root = _find_project_root()
    return project_root / POSITION_FILE


_OLD_KEYS = {
    "last_archive": "last_change",
    "last_archive_dir": "last_change_dir",
}


def read_position(project_root: Optional[Path] = None) -> Position:
    pos_path = get_position_path(project_root)
    if not pos_path.exists():
        return Position()
    try:
        data = json.loads(pos_path.read_text(encoding="utf-8"))
        for old_key, new_key in _OLD_KEYS.items():
            if old_key in data:
                data[new_key] = data.pop(old_key)
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


def update_position(change_name: str, change_dir: str, project_root: Optional[Path] = None) -> Position:
    pos = Position(last_change=change_name, last_change_dir=change_dir)
    write_position(pos, project_root)
    return pos


def reset_position(project_root: Optional[Path] = None) -> None:
    write_position(Position(), project_root)


def find_changes(project_root: Optional[Path] = None) -> list[dict]:
    """List all changes under openspec/changes/, sorted by name."""
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

    # Also scan archive/ for completed changes
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


def find_unprocessed_changes(project_root: Optional[Path] = None) -> list[dict]:
    """Find changes that haven't been processed yet (after last position)."""
    pos = read_position(project_root)
    changes = find_changes(project_root)

    if not changes:
        return []

    if pos.last_change_dir is None:
        return changes

    # Find index of last processed change
    last_idx = -1
    for i, c in enumerate(changes):
        if c["dir_name"] == pos.last_change_dir:
            last_idx = i
            break

    if last_idx < 0:
        return changes

    return changes[last_idx + 1:]


def main():
    parser = argparse.ArgumentParser(description="Comet change position tracker")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show current position")
    sub.add_parser("list", help="List all changes")
    sub.add_parser("pending", help="List unprocessed changes")
    sub.add_parser("reset", help="Reset position")

    p_set = sub.add_parser("set", help="Set position to specific change")
    p_set.add_argument("dir_name", help="Change dir name (e.g. my-feature-change)")

    args = parser.parse_args()

    if args.command == "status":
        pos = read_position()
        print(json.dumps(asdict(pos), ensure_ascii=False, indent=2))

    elif args.command == "list":
        all_changes = find_changes()
        if not all_changes:
            print("No changes found.")
            return
        for c in all_changes:
            flag = " " if c["has_proposal"] else "!"
            print(f"  {flag} {c['dir_name']}")

    elif args.command == "pending":
        pending = find_unprocessed_changes()
        if not pending:
            print("No unprocessed changes.")
            return
        for c in pending:
            print(f"  {c['dir_name']}")

    elif args.command == "reset":
        reset_position()
        print("Position reset.")

    elif args.command == "set":
        update_position(args.dir_name, args.dir_name)
        print(f"Position set to: {args.dir_name}")


if __name__ == "__main__":
    main()
