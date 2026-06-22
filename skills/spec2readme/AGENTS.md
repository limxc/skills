# Skill: spec2readme

## Activation

- `/spec2readme`
- User asks for README/技术文档/文档化/changelog/变更总结 from OpenSpec changes.

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/check_openspec.py` | Check whether the current directory is an OpenSpec project |
| `scripts/env_check.py` | Verify dependencies (`creating-mermaid-diagrams`, `mmdc`, Chrome) |
| `scripts/position.py` | Track processed/skipped changes (`status`, `pending`, `processed`, `skipped`, `unskip`, `list`, `reset`) |
| `scripts/prepare_output.py` | Generate output file path and temporary `.mmd` directory |
| `scripts/get_change_date.py` | Read `created:` from a change directory's `.openspec.yaml` |
| `scripts/get_mermaid_types.py` | Read supported diagram types from creating-mermaid-diagrams |
| `scripts/append_readme.py` | Append a document link to `README.md` 项目文档 section |
| `scripts/cleanup_mmd.py` | Remove the temporary `.mmd` directory |
| `scripts/utils.py` | Shared helpers (`find_project_root`, `resolve_change_path`) |

## Position Tracking

- File: `<project-root>/spec2readme/.spec2readme-position.json`
- Tracks `processed` and `skipped` change directory names.
- Commands:
  - `python <skill>/scripts/position.py pending` — list pending changes
  - `python <skill>/scripts/position.py processed <dir>...` — mark as done
  - `python <skill>/scripts/position.py skipped <dir>...` — mark as skip
  - `python <skill>/scripts/position.py list` — show all changes with status
  - `python <skill>/scripts/position.py unskip <dir>...` — restore skipped change

## Output

- Generated document: `<project-root>/spec2readme/<date>-<change-name>.md`
- Temporary diagram source: `<project-root>/spec2readme/<date>-<change-name>-mmd/`
- README.md section: `## 项目文档`

## Dependencies

- `creating-mermaid-diagrams` skill
- `mmdc` CLI or Kroki API access
- Node.js / npm (for `npx`)

## Notes

- Always delegate actual diagram generation to `creating-mermaid-diagrams`.
- Do not mark changes as `processed` until the user explicitly confirms the final document.
