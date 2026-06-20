#!/usr/bin/env python3
"""Position tracker for wechat-article skill.

Tracks which Comet archives have been processed for WeChat articles.
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
    last_archive: Optional[str] = None
    last_archive_dir: Optional[str] = None
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
    position.updated_at = datetime.now().isoformat()
    pos_path.write_text(
        json.dumps(asdict(position), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def update_position(archive_name: str, archive_dir: str, project_root: Optional[Path] = None) -> Position:
    pos = Position(last_archive=archive_name, last_archive_dir=archive_dir)
    write_position(pos, project_root)
    return pos


def reset_position(project_root: Optional[Path] = None) -> None:
    write_position(Position(), project_root)


def find_archives(project_root: Optional[Path] = None) -> list[dict]:
    """List all archived changes in openspec/changes/archive/, sorted by date."""
    if project_root is None:
        project_root = _find_project_root()

    archive_dir = project_root / "openspec" / "changes" / "archive"
    if not archive_dir.is_dir():
        return []

    archives = []
    for entry in sorted(archive_dir.iterdir()):
        if not entry.is_dir():
            continue
        comet_yaml = entry / ".comet.yaml"
        proposal = entry / "proposal.md"
        design = entry / "design.md"
        tasks = entry / "tasks.md"

        archives.append({
            "dir_name": entry.name,
            "path": str(entry),
            "has_comet_yaml": comet_yaml.exists(),
            "has_proposal": proposal.exists(),
            "has_design": design.exists(),
            "has_tasks": tasks.exists(),
        })

    return archives


def find_unprocessed_archives(project_root: Optional[Path] = None) -> list[dict]:
    """Find archives that haven't been processed yet (after last position)."""
    pos = read_position(project_root)
    archives = find_archives(project_root)

    if not archives:
        return []

    if pos.last_archive_dir is None:
        return archives

    # Find index of last processed archive
    last_idx = -1
    for i, a in enumerate(archives):
        if a["dir_name"] == pos.last_archive_dir:
            last_idx = i
            break

    if last_idx < 0:
        # Last processed archive not found; return all
        return archives

    # Return archives after the last processed one
    return archives[last_idx + 1:]


def main():
    parser = argparse.ArgumentParser(description="Comet archive position tracker")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show current position")
    sub.add_parser("list", help="List all archives")
    sub.add_parser("pending", help="List unprocessed archives")
    sub.add_parser("reset", help="Reset position")

    p_set = sub.add_parser("set", help="Set position to specific archive")
    p_set.add_argument("dir_name", help="Archive dir name (e.g. 2026-06-19-my-change)")

    args = parser.parse_args()

    if args.command == "status":
        pos = read_position()
        print(json.dumps(asdict(pos), ensure_ascii=False, indent=2))

    elif args.command == "list":
        archives = find_archives()
        if not archives:
            print("No archives found.")
            return
        for a in archives:
            flag = " " if a["has_proposal"] else "!"
            print(f"  {flag} {a['dir_name']}")

    elif args.command == "pending":
        pending = find_unprocessed_archives()
        if not pending:
            print("No unprocessed archives.")
            return
        for a in pending:
            print(f"  {a['dir_name']}")

    elif args.command == "reset":
        reset_position()
        print("Position reset.")

    elif args.command == "set":
        update_position(args.dir_name, args.dir_name)
        print(f"Position set to: {args.dir_name}")


if __name__ == "__main__":
    main()
