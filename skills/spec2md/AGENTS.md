# Skill: spec2md

## Activation
- `/spec2md`

## Key Scripts
- `scripts/position.py` — `status`, `pending`, `processed`, `skipped`, `unskip`, `list`, `reset` (track position across OpenSpec changes)
- `scripts/append_readme.py` — append article link to README.md 需求时间线 section

## Position Tracking
- File: `<project-root>/.wechat-article-position.json`
- Tracks: `processed` (used in articles) + `skipped` (user dismissed) lists
- Commands:
  - `python <skill>/scripts/position.py pending` — list change to process
  - `python <skill>/scripts/position.py processed <dir>...` — mark as done
  - `python <skill>/scripts/position.py skipped <dir>...` — mark as skip
  - `python <skill>/scripts/position.py list` — show all with status flags
  - `python <skill>/scripts/position.py unskip <dir>...` — restore skipped change
- Env override: `$env:SPEC2MD_PROJECT_ROOT` — explicitly set project root path

## Output Directory
- `<project-root>/spec2md/` — generated articles and assets

## Dependencies
- drawio-skill at `~/.agents/skills/drawio-skill/`
