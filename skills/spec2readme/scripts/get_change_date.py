#!/usr/bin/env python3
"""Read the `created:` date from an OpenSpec change directory's .openspec.yaml.

Usage:
    python scripts/get_change_date.py <change-path>
    python scripts/get_change_date.py <change-dir-name> [<project-root>]
"""

import argparse
import sys
from pathlib import Path

from utils import find_project_root, resolve_change_path


def get_change_date(change_path: Path) -> str:
    """Return the `created:` value from `.openspec.yaml` in `change_path`."""
    if not change_path or not change_path.is_dir():
        return ""
    yaml_path = change_path / ".openspec.yaml"
    if not yaml_path.is_file():
        return ""
    try:
        for line in yaml_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("created:"):
                return stripped.split(":", 1)[1].strip()
    except Exception:
        pass
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Get created date of an OpenSpec change")
    parser.add_argument("change", help="Change directory path or directory name")
    parser.add_argument("--project-root", help="Project root (optional)")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve() if args.project_root else find_project_root()
    change_path = resolve_change_path(args.change, project_root)
    if not change_path.is_dir():
        print(f"Change directory not found: {args.change}", file=sys.stderr)
        return 1

    date = get_change_date(change_path)
    if not date:
        print(f"No created: field found in {change_path / '.openspec.yaml'}", file=sys.stderr)
        return 1

    print(date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
