#!/usr/bin/env python3
"""Append a document link entry to README.md project docs section.

Usage:
    python scripts/append_readme.py <project-root> "<title>" <doc-path> <change-path-or-name>

<change-path-or-name> can be either:
- the absolute/relative path to the change directory, or
- the change directory name (e.g., tweak-spec2md-diagram-prompts).

If a directory name is given, the script looks for it under
openspec/changes/ or openspec/changes/archive/.
Entry date comes from the change directory's .openspec.yaml `created:` field.
"""

import re
import sys
from pathlib import Path

from get_change_date import get_change_date
from utils import find_project_root, resolve_change_path


def main():
    if len(sys.argv) < 5:
        print(
            "Usage: python scripts/append_readme.py <project-root> \"<title>\" <doc-path> <change-path-or-name>",
            file=sys.stderr,
        )
        sys.exit(1)

    project_root = Path(sys.argv[1]).resolve()
    title = sys.argv[2]
    doc_path = Path(sys.argv[3])
    change_arg = sys.argv[4]

    # Ensure link is relative to README.md (project root)
    if doc_path.is_absolute():
        try:
            doc_relative = doc_path.relative_to(project_root).as_posix()
        except ValueError:
            doc_relative = doc_path.as_posix()
    else:
        doc_relative = doc_path.as_posix()

    change_path = resolve_change_path(change_arg, project_root)
    date_str = get_change_date(change_path)
    date_label = f"{date_str} \u2014 " if date_str else ""

    readme_path = project_root / "README.md"
    link_entry = f"- [{date_label}{title}]({doc_relative})"
    section_header = "## \u9879\u76ee\u6587\u6863"

    if not readme_path.exists():
        readme_path.write_text(f"\n{section_header}\n\n{link_entry}\n", encoding="utf-8")
        print(f"Created {readme_path} with project docs section")
        return

    content = readme_path.read_text(encoding="utf-8")

    # Avoid duplicate entries
    if link_entry in content:
        print(f"Entry already exists in {readme_path}; skipping")
        return

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
