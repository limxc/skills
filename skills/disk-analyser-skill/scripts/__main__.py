import argparse
import sys
import time

from .scanner import scan
from .categorizer import classify
from .formatter import format_report, format_size


def _progress(path: str, size_hint: int):
    hint = format_size(size_hint) if size_hint else "?"
    print(f"[PROGRESS] Deep scanning: {path} ({hint})", file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser(
        description="Disk space analyzer \u2014 scan directories and identify large folders",
    )
    ap.add_argument("path", help="Root directory to scan")
    ap.add_argument("--min-size", type=int, default=1_000_000_000,
                    help="Minimum folder size in bytes to recurse into (default: 1GB)")
    ap.add_argument("--max-depth", type=int, default=5,
                    help="Maximum recursion depth (default: 5)")
    ap.add_argument("--timeout", type=int, default=0,
                    help="Timeout in seconds (0 = no timeout)")
    args = ap.parse_args()

    deadline = time.time() + args.timeout if args.timeout else 0

    print(f"[PROGRESS] Scanning top-level folders in {args.path}...",
          file=sys.stderr, flush=True)

    start = time.time()
    root = scan(args.path, args.max_depth, args.min_size,
                _progress, _deadline=deadline)
    elapsed = time.time() - start

    classify(root)
    print(format_report(root, elapsed))


if __name__ == "__main__":
    main()
