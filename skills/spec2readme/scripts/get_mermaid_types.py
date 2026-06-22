#!/usr/bin/env python3
"""Read creating-mermaid-diagrams SKILL.md and extract supported diagram types.

Usage:
    python scripts/get_mermaid_types.py

Outputs JSON array of supported diagram types with their keywords and use cases.
"""

import json
import os
import re
import sys
from pathlib import Path


def find_creating_mermaid_skill() -> Path | None:
    """Locate creating-mermaid-diagrams skill installation."""
    candidates = [
        Path.home() / ".agents" / "skills" / "creating-mermaid-diagrams",
        Path.home() / ".config" / "opencode" / "skills" / "creating-mermaid-diagrams",
        Path.home() / ".opencode" / "skills" / "creating-mermaid-diagrams",
    ]
    for cand in candidates:
        if (cand / "SKILL.md").is_file():
            return cand
    return None


def parse_diagram_types(skill_md: str) -> list[dict]:
    """Extract diagram types from the '## Diagram Types' table in SKILL.md."""
    # Find the Diagram Types section
    match = re.search(
        r"## Diagram Types\s*\n\s*\|[^\n]*\|\s*\n\s*\|[-:\s|]+\|\s*\n((?:\s*\|[^\n]*\|\s*\n?)+)",
        skill_md,
        re.IGNORECASE,
    )
    if not match:
        return []

    table_body = match.group(1).strip()
    types = []
    for line in table_body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 3:
            types.append(
                {
                    "type": cells[0],
                    "keyword": cells[1].strip("`"),
                    "use_for": cells[2],
                }
            )
    return types


def main() -> int:
    skill_dir = find_creating_mermaid_skill()
    if not skill_dir:
        print(
            "Error: creating-mermaid-diagrams skill not found. "
            "Expected under ~/.agents/skills/ or ~/.config/opencode/skills/",
            file=sys.stderr,
        )
        return 1

    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    types = parse_diagram_types(skill_md)

    if not types:
        print("Error: Could not parse diagram types from SKILL.md", file=sys.stderr)
        return 1

    print(json.dumps(types, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
