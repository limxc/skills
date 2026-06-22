#!/usr/bin/env python3
"""Check whether the current directory is an OpenSpec project.

Usage:
    python scripts/check_openspec.py [--try-parent]

Exit codes:
    0  openspec/ found
    1  openspec/ not found
"""

import argparse
import sys
from pathlib import Path

from utils import find_project_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for OpenSpec project structure")
    parser.add_argument("--try-parent", action="store_true", help="Also check parent directory")
    args = parser.parse_args()

    candidates = [find_project_root()]
    if args.try_parent:
        cwd = Path.cwd().resolve()
        if cwd.parent != cwd:
            candidates.append(cwd.parent)

    for candidate in candidates:
        if (candidate / "openspec").is_dir():
            print(str(candidate))
            return 0

    print("OpenSpec 项目结构未找到。请在已初始化 OpenSpec（含 openspec/changes/ 目录）的项目中运行本 skill。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
