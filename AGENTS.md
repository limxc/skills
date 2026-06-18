# Project Rules

## Skill Output Location

When using any skill-creator agent (including `/agent-skill-creator` and `/skill-creator`) to create new skills:

- **All generated skills MUST be placed in the `skills/` directory** at the project root (`D:\WorkSpace\skills\skills\`)
- Do NOT install created skills to `.agents/skills/`, `.opencode/skills/`, or any other global/project-level path
- The `skills/` directory is the single canonical location for all custom skills in this project

## Skill Directory Structure

```
skills/<skill-name>/
├── SKILL.md
├── scripts/
├── references/
├── assets/
└── ...
```

## Modifying Installed Skills

- **Never modify** the contents of any installed skill under `.agents/skills/` or `.opencode/skills/`
- Installed skills must remain identical to their original source (github.com)
- If a skill needs changes, create a new skill in `skills/` instead, or update the upstream source
