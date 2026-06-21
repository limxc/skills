#!/usr/bin/env python3
"""Append a document link entry to README.md project docs section.

Usage:
    python scripts/append_readme.py <project-root> "<title>" <doc-path> <change-dir>

<change-dir> is the change directory name (e.g., tweak-spec2md-diagram-prompts).
Looks for it under openspec/changes/ or openspec/changes/archive/.
Entry date comes from git author date, or filesystem ctime as fallback.
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _get_change_date(project_root, change_dir):
    candidates = [
        project_root / "openspec" / "changes" / change_dir,
        project_root / "openspec" / "changes" / "archive" / change_dir,
    ]
    change_path = None
    for p in candidates:
        if p.is_dir():
            change_path = p
            break
    if not change_path:
        return ""
    try:
        r = subprocess.run(
            ["git", "log", "--follow", "--diff-filter=A", "--format=%aI", "-1", "--", str(change_path)],
            capture_output=True, text=True, cwd=project_root, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()[:10]
    except Exception:
        pass
    ctime = change_path.stat().st_ctime
    return datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")


def find_project_root() -> Path:
    root_override = Path(os.environ.get("SPEC2README_PROJECT_ROOT", ""))
    if root_override.is_dir():
        return root_override.resolve()
    cwd = Path.cwd().resolve()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").is_dir() or (parent / "openspec").is_dir():
            return parent
    return cwd


def main():
    if len(sys.argv) < 4:
        print("Usage: python scripts/append_readme.py <project-root> \"<title>\" <doc-path> <change-dir>", file=sys.stderr)
        sys.exit(1)

    project_root = Path(sys.argv[1]).resolve()
    title = sys.argv[2]
    doc_relative = sys.argv[3]
    change_dir = sys.argv[4]

    date_str = _get_change_date(project_root, change_dir)
    date_label = f"{date_str} \u2014 " if date_str else ""

    readme_path = project_root / "README.md"
    link_entry = f"- [{date_label}{title}]({doc_relative})"
    section_header = "## \u9879\u76ee\u6587\u6863"

    if not readme_path.exists():
        readme_path.write_text(f"\n{section_header}\n\n{link_entry}\n", encoding="utf-8")
        print(f"Created {readme_path} with project docs section")
        return

    content = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(rf"^{re.escape(section_header)}\s*\n(.*?)(?=\n## |\Z)", re.DOTALL | re.MULTILINE)
    match = pattern.search(content)

    if match:
        section = match.group(0).rstrip()
        new_section = f"{section}\n{link_entry}"
        content = content.replace(section, new_section)
    else:
        content = content.rstrip() + f"\n\n{section_header}\n\n{link_entry}\n"

    readme_path.write_text(content, encoding="utf-8")
    print(f"Appended to project docs section in {readme_path}")


if __name__ == "__main__":
    main()
