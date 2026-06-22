#!/usr/bin/env python3
"""Remove the temporary Mermaid directory created during a spec2readme run.

Usage:
    python scripts/cleanup_mmd.py <mmd-dir>
"""

import argparse
import shutil
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove temporary mmd directory")
    parser.add_argument("mmd_dir", help="Path to the temporary mmd directory")
    args = parser.parse_args()

    path = Path(args.mmd_dir)
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
