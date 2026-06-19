## Why

Windows users frequently run out of disk space but struggle to identify which folders consume the most storage and whether those folders can be safely cleaned. Existing tools (TreeSize, WinDirStat) require manual installation and separate operation. An agent skill enables natural-language-driven disk analysis directly in the AI workflow, combining scanning, content classification, and cleanup recommendations in one seamless experience.

## What Changes

- Create `disk-analyser-skill` — an agent skill for Windows disk space analysis
- Provide PowerShell scripts for recursive directory scanning (>1GB recurse up to 5 levels, <1GB skip recursion)
- Implement folder content classification (cache, temp, downloads, media, code, system, user data, etc.)
- Provide cleanup recommendations with safety levels (safe, cautious, unsafe)
- Skip system folders (Windows, Program Files, etc.) and paths without access permissions
- Provide `/disk-space-analyzer` command entry point for direct invocation in agent
- Output tree-structured text report directly in agent conversation

## Capabilities

### New Capabilities
- `disk-scan`: Recursively scan Windows directories to identify large folders and their contents up to configurable depth
- `folder-categorization`: Classify folders by content type and determine safe cleanup actions
- `report-formatter`: Format scan results as tree-structured tables with size, category, and recommendation columns

### Modified Capabilities

(none)

## Impact

- New skill package in `skills/disk-analyser-skill/` (or global install path)
- New PowerShell scripts for scanning, categorization, and reporting
- No changes to existing skills, specs, or application code
