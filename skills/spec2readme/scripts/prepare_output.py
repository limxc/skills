#!/usr/bin/env python3
"""Prepare output paths and directories for a spec2readme run.

Usage:
    python scripts/prepare_output.py <change-name> [<project-root>]

Outputs JSON:
    {
        "changeName": "...",
        "changeDir": "<absolute-path>",
        "projectRoot": "<absolute-path>",
        "date": "<created-date>",
        "outputFile": "spec2readme/<date>-<change-name>.md",
        "mmdDir": "spec2readme/<date>-<change-name>-mmd"
    }
"""

import argparse
import json
import sys
from pathlib import Path

from get_change_date import get_change_date
from utils import find_project_root, resolve_change_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare spec2readme output paths")
    parser.add_argument("change_name", help="Change directory name")
    parser.add_argument("--project-root", help="Project root (optional)")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve() if args.project_root else find_project_root()
    change_path = resolve_change_path(args.change_name, project_root)

    if not change_path.is_dir():
        print(
            f"Change directory not found: {args.change_name} "
            f"(looked under openspec/changes/ and openspec/changes/archive/)",
            file=sys.stderr,
        )
        return 1

    date = get_change_date(change_path)
    if not date:
        print(
            f"Could not read created: from {change_path / '.openspec.yaml'}",
            file=sys.stderr,
        )
        return 1

    output_dir = project_root / "spec2readme"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{date}-{args.change_name}.md"
    mmd_dir = output_dir / f"{date}-{args.change_name}-mmd"
    mmd_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "changeName": args.change_name,
        "changeDir": str(change_path),
        "projectRoot": str(project_root),
        "date": date,
        "outputFile": str(output_file.relative_to(project_root)).replace("\\", "/"),
        "mmdDir": str(mmd_dir.relative_to(project_root)).replace("\\", "/"),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
