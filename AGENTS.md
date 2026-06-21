# Project Rules

## Skill Directory Structure

```
skills/<skill-name>/
├── SKILL.md
├── scripts/
├── references/
├── assets/
└── ...
```

## Global Installation

After a skill is created, **automatically install it globally**:

1. Copy to `~\.agents\skills\<skill-name>\`
2. If the current agent is **opencode**, also create a junction: `New-Item -ItemType Junction -Path "$env:USERPROFILE\.config\opencode\skills\<skill-name>" -Target "$env:USERPROFILE\.agents\skills\<skill-name>"`
3. Then **ask the user** using a yes/no choice prompt, defaulting to **Yes**: "Skill created and installed globally! Would you like to copy it to the project's `skills/` directory too?"
   3.1 If yes, copy to `skills/<skill-name>/`
   3.2 If no, remove the project copy

If the user later asks to install/move a skill to global or project, do so promptly.

If a globally installed skill in `~\.agents\skills\` is modified, **automatically sync the changes** to the project's `skills/` directory (overwrite the project copy) if it exists.

If a locally-created skill under `skills/` is modified, **automatically sync the changes** to `~\.agents\skills\<same-name>\` (overwrite the global copy) so the user doesn't need to ask, and **notify the user** when sync is complete.

## Modifying Installed Skills

- **Never modify** the contents of any installed skill under `.agents/skills/` or `.opencode/skills/` if it was installed from an external source (e.g., `npx skills add`, git clone of a third-party repo)
- Installed skills from external sources must remain identical to their original source (github.com)
- Skills created locally by `skill-creator` and `agent-skill-creator` **can be modified freely**
