# Reading Comet Archives

This reference describes how to read and understand Comet archive directories.

## Archive Location

Archived changes are stored at:
```
<project-root>/openspec/changes/archive/YYYY-MM-DD-<change-name>/
```

## Directory Structure

```
YYYY-MM-DD-<change-name>/
├── .comet.yaml            # State machine metadata (required)
├── .openspec.yaml         # OpenSpec metadata (required)
├── proposal.md            # Why + What changes (required)
├── design.md              # Design decisions (full workflow only)
├── tasks.md               # Task checklist (required)
├── specs/                 # Delta capability specs (optional)
│   └── <capability>/spec.md
└── .comet/handoff/        # Context packs (optional)
    ├── design-context.json
    ├── design-context.md
    └── brainstorm-summary.md
```

## Key Files to Read

### `.comet.yaml`

| Field | What it tells you |
|-------|-------------------|
| `workflow` | full / hotfix / tweak — type of change |
| `created_at` | When the change was started |
| `verified_at` | When verification passed |
| `verify_result` | Should be "pass" |

### `proposal.md`

Contains the rationale and summary. Key sections:
- **## Why** — Motivation and problem statement
- **## What Changes** — Concrete changes made
- **## Capabilities** — New or modified capabilities
- **## Impact** — Effects on other parts of the project

### `design.md` (if present)

Only for full workflow. Key sections:
- **## Context** — Background and scope
- **## Decisions** — Table with Decision, Choice, Rationale
- **## Risks / Trade-offs** — Risk register

### `tasks.md`

Completed tasks in checklist format. Shows what was actually done.

## Writing Approach

When writing articles from archives:

1. **Group related changes** — Multiple archives from the same day or theme can be combined into one article
2. **Extract the story** — Each archive has a "why" (proposal.md) that becomes the narrative hook
3. **Highlight impact** — What does this mean for users/readers?
4. **Keep it human** — Avoid listing tasks; tell the story behind the changes

## Example Archive Reading

For archive `2026-06-19-disk-space-analyzer`:
- workflow: full (significant new feature)
- Created a new disk analyzer tool with Python scripts
- Read proposal.md for the motivation (why disk analysis was needed)
- Read design.md for architecture decisions
- Read tasks.md for what was actually built
