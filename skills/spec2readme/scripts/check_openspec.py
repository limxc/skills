#!/usr/bin/env python3
"""Check whether the current directory is inside an OpenSpec project.

Usage:
    python scripts/check_openspec.py

Exit codes:
    0  openspec/ found
    1  openspec/ not found
"""

import sys

from utils import find_project_root


def main() -> int:
    root = find_project_root()
    if (root / "openspec").is_dir():
        print(str(root))
        return 0

    print(
        "OpenSpec 项目结构未找到。请在已初始化 OpenSpec（含 openspec/changes/ 目录）的项目中运行本 skill。",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
