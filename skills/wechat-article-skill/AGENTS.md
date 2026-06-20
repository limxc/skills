# Skill: wechat-article-skill

## Purpose
Generate WeChat public account articles from Comet archives. Self-implemented pre-steps (archive reading, writing discussion, diagram generation) + unmodified wewrite pipeline (writing, SEO, visual AI, formatting, publishing).

## Activation
- `/wechat-article`

## Pipeline

| Phase | What happens |
|-------|-------------|
| Pre-1 | Load Comet env, check deps, read position, find pending archives |
| Pre-2 | Checkbox selection, title/skeleton/illustration discussion, persona |
| Pre-3 | Read archive content, delegate to drawio-skill, interactive confirmation |
| Step 4 | wewrite: writing with persona + exemplar injection |
| Step 5 | wewrite: SEO + quality validation |
| Step 6 | wewrite: cover + inline images (skip paragraphs with existing images) |
| Step 7 | wewrite: metadata check → converter → publish/preview |
| Step 8 | wewrite: history + position update |

## WeChat Image Rule

All generated images should use drawio-skill's default export quality. Ensure Microsoft YaHei (微软雅黑) font is available for Chinese text rendering.

## Key Scripts
- `scripts/position.py` — `status`, `pending`, `set`
- `scripts/publish.py` — dry-run conversion (publish via wewrite CLI)

## Position Tracking
- File: `<project-root>/.wechat-article-position.json`
- Commands: `python3 <skill>/scripts/position.py [status|pending|set <dir>]`

## Dependencies
- wewrite (referenced, not bundled) at `~/.agents/skills/wewrite/`
