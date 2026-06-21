#!/usr/bin/env python3
"""Append a document link entry to README.md 项目文档 section.

Usage:
    python scripts/append_readme.py <project-root> "<title>" <doc-path>

Reads SPEC2README_PROJECT_ROOT env var for project root override.
"""

import os
import re
import sys
from pathlib import Path


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
    if len(sys.argv) < 3:
        print("Usage: python scripts/append_readme.py <project-root> \"<title>\" <doc-path>", file=sys.stderr)
        sys.exit(1)

    project_root = Path(sys.argv[1]).resolve()
    title = sys.argv[2]
    doc_relative = sys.argv[3]

    # Extract date from filename pattern: {date}-{changeName}.md
    date_label = ""
    doc_name = Path(doc_relative).stem
    if doc_name and len(doc_name) >= 10 and doc_name[4] == "-" and doc_name[7] == "-":
        date_label = doc_name[:10] + " — "

    readme_path = project_root / "README.md"
    link_entry = f"- [{date_label}{title}]({doc_relative})"
    section_header = "## 项目文档"

    if not readme_path.exists():
        readme_path.write_text(f"\n{section_header}\n\n{link_entry}\n", encoding="utf-8")
        print(f"Created {readme_path} with 项目文档 section")
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
    print(f"Appended to 项目文档 section in {readme_path}")


if __name__ == "__main__":
    main()
