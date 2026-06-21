#!/usr/bin/env python3
"""Append an article link entry to README.md 需求时间线 section.

Usage:
    python scripts/append_readme.py <project-root> "<title>" <article-dir>

Reads SPEC2MD_PROJECT_ROOT env var for project root override.
"""

import os
import re
import sys
from pathlib import Path


def find_project_root() -> Path:
    root_override = Path(os.environ.get("SPEC2MD_PROJECT_ROOT", ""))
    if root_override.is_dir():
        return root_override.resolve()
    cwd = Path.cwd().resolve()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").is_dir() or (parent / ".openspec.yaml").is_file() or (parent / "openspec").is_dir():
            return parent
    return cwd


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/append_readme.py <project-root> \"<title>\" <article-dir>", file=sys.stderr)
        sys.exit(1)

    project_root = Path(sys.argv[1]).resolve()
    title = sys.argv[2]
    article_dir = sys.argv[3]

    readme_path = project_root / "README.md"
    link_entry = f"- [{title}](spec2md/{article_dir}/article.md)"
    section_header = "## 需求时间线"

    if not readme_path.exists():
        readme_path.write_text(f"\n{section_header}\n\n{link_entry}\n", encoding="utf-8")
        print(f"Created {readme_path} with 需求时间线 section")
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
    print(f"Appended to 需求时间线 in {readme_path}")


if __name__ == "__main__":
    main()
