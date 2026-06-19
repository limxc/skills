# Comet Design Handoff

- Change: disk-space-analyzer
- Phase: design
- Mode: compact
- Context hash: d70b48401bd70855c8fb43e67a869d261cfa12c16bc590b1d48fa8664c90fcfe

Generated-by: comet-handoff.sh

OpenSpec remains the canonical capability spec. This handoff is a deterministic, source-traceable context pack, not an agent-authored summary.

## openspec/changes/disk-space-analyzer/proposal.md

- Source: openspec/changes/disk-space-analyzer/proposal.md
- Lines: 1-30
- SHA256: ddc5a1126fa181f79bed758c169d12cb68bcfe1e530e0f3b940018d22e75a0d3

```md
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
```

## openspec/changes/disk-space-analyzer/design.md

- Source: openspec/changes/disk-space-analyzer/design.md
- Lines: 1-37
- SHA256: 62700b4e7c3c3c5668908b53c7ec2c3209e1f3e0bb7687d2ef6cc40f7aa5b8ac

```md
## Context

The `disk-analyser-skill` is an agent skill triggered when a user asks about disk space on Windows. The agent runs bundled PowerShell scripts to scan directories, classify folders, and present findings. No external dependencies, no daemon, no persistent state — the skill is fully self-contained in its SKILL.md + scripts.

## Goals / Non-Goals

**Goals:**
- Provide a set of reusable PowerShell scripts for disk scanning, categorization, and reporting
- Define agent activation rules in SKILL.md so the agent correctly triggers on disk-related queries
- Output formatted tree tables directly in the agent conversation

**Non-Goals:**
- No GUI or interactive console mode
- No real-time monitoring or file watchers
- No cross-platform support (Windows/PowerShell only)
- No disk performance or health analysis

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.8+ | Cross-platform portable, rich standard library for filesystem traversal and formatting |
| Script architecture | 3 standalone Python modules (scan, categorize, format) | Separation of concerns; each independently runnable; output via stdout |
| Data format | Scripts output structured dict as JSON | Agent parses JSON and formats flexibly; no intermediate files |
| Categorization | Hardcoded rules in Python dict | Simple to maintain; no external config dependencies |
| Recursion strategy | Depth-limited (>1GB recurse ≤5 levels; <1GB stop) | Balances thoroughness with responsiveness; prevents runaway scans |
| System folder exclusion | Hardcoded list | Well-known system paths are stable across Windows versions |
| Output format | Markdown-friendly tables from agent | No external formatting library needed; agent renders naturally |
| Invocation | `/disk-space-analyzer` command in SKILL.md + trigger in description | User can either type the command or ask naturally; skill triggers both ways |

## Risks / Trade-offs

- [Large directories] Deep 5-level recursion on a folder with thousands of sub-items may be slow → Add a scan duration cap (30s default) and inform user if scan is truncated
- [Permission denied] Some folders inherently inaccessible → Skip gracefully, report count of skipped folders
- [Python availability] Windows may not have Python installed → Document Python requirement in SKILL.md; add install check in entry point
- [False classification] Heuristic-based categorization may misclassify → Mark "unknown" for unclassifiable folders; never auto-delete anything
- [Cross-platform potential] Python enables future Linux/Mac support with minimal changes → Mark platform in SKILL.md as `windows` initially, note cross-platform in references
```

## openspec/changes/disk-space-analyzer/tasks.md

- Source: openspec/changes/disk-space-analyzer/tasks.md
- Lines: 1-19
- SHA256: a57b5be11dd5034d4e9ef7a8f08f0476ae386b1dd09ffb64a18183acb21f4eb9

```md
## 1. Skill Structure

- [ ] 1.1 Create `skills/disk-analyser-skill/` directory with SKILL.md, scripts/, references/
- [ ] 1.2 Write SKILL.md with activation triggers, workflow instructions, and output format guidance

## 2. PowerShell Scripts

- [ ] 2.1 Implement `scripts/scan_disk.py` — recursive directory scanning with size calculation
- [ ] 2.2 Implement `scripts/categorize_folder.py` — folder classification by content type
- [ ] 2.3 Implement `scripts/format_report.py` — structured output formatting
- [ ] 2.4 Create `scripts/__init__.py` — main entry point orchestrating all modules

## 3. Integration & Verification

- [ ] 3.1 Add `/disk-space-analyzer` command definition in SKILL.md
- [ ] 3.2 Verify skill directory structure and file completeness
- [ ] 3.3 Create `requirements.txt` if needed (stdlib-only, no external deps)
- [ ] 3.4 Test scripts locally against a sample directory
- [ ] 3.4 Install skill globally and verify agent can trigger it
```

## openspec/changes/disk-space-analyzer/specs/disk-scan/spec.md

- Source: openspec/changes/disk-space-analyzer/specs/disk-scan/spec.md
- Lines: 1-46
- SHA256: 20085f5f9a2be7c2f262666705a3dc20886e44196eba7fc7feab61775368efc2

```md
## ADDED Requirements

### Requirement: Scan directory tree
The system SHALL recursively scan a specified directory path on Windows, enumerating all subdirectories and computing their total size.

#### Scenario: Scan top-level directory
- **WHEN** user requests analysis of path `C:\Users\TestUser`
- **THEN** system shall enumerate all immediate subdirectories of that path and compute their sizes

#### Scenario: Recursive scan of large folders
- **WHEN** a subdirectory exceeds 1 GB in size
- **THEN** system shall recurse into that subdirectory to enumerate its children, up to a maximum depth of 5 levels
- **THEN** subdirectories smaller than 1 GB shall not be recursed into

### Requirement: Skip system folders
The system SHALL NOT analyze protected Windows system folders, including but not limited to `Windows`, `Program Files`, `Program Files (x86)`, and `System32`.

#### Scenario: System folder exclusion
- **WHEN** scanning encounters a path matching a known system folder name
- **THEN** system shall skip that folder and note it was excluded

### Requirement: Handle permission errors
The system SHALL gracefully skip directories it does not have permission to access, without halting the scan.

#### Scenario: Access denied
- **WHEN** scanning encounters a directory without read permission
- **THEN** system shall skip that directory and continue scanning sibling directories
- **THEN** system shall report that the directory was skipped due to insufficient permissions

### Requirement: Report folder sizes
The system SHALL report each directory's total size in human-readable units (Bytes, KB, MB, GB).

#### Scenario: Size formatting
- **WHEN** a folder size is 1,500,000,000 bytes
- **THEN** system shall display it as "1.40 GB"

### Requirement: Filter by size threshold
The system SHALL support a minimum size threshold, returning only folders whose size equals or exceeds the threshold.

#### Scenario: Default threshold
- **WHEN** user does not specify a minimum size
- **THEN** system shall use a default threshold of 1 GB

#### Scenario: Custom threshold
- **WHEN** user specifies a minimum size of 500 MB
- **THEN** system shall include only folders >= 500 MB
```

## openspec/changes/disk-space-analyzer/specs/folder-categorization/spec.md

- Source: openspec/changes/disk-space-analyzer/specs/folder-categorization/spec.md
- Lines: 1-50
- SHA256: 3af5d30524614cb743b3c7c80edb87e4faaec060a1534682c11c4473ac45cda7

```md
## ADDED Requirements

### Requirement: Classify folder content
The system SHALL classify each scanned folder into one or more content categories based on its name, path patterns, and contents.

#### Scenario: Classify by folder name
- **WHEN** a folder is named `node_modules`, `.npm`, or `.yarn`
- **THEN** system shall classify it as `dependency-cache`

#### Scenario: Classify by path pattern
- **WHEN** a folder path contains `AppData\Local\Temp`
- **THEN** system shall classify it as `temporary-files`

### Requirement: Content category types
The system SHALL use at minimum the following content categories for classification:
- `dependency-cache` — package manager caches (npm, pip, maven, nuget, etc.)
- `temporary-files` — system/app temp files (Temp, tmp, cache)
- `downloads` — user download folders
- `media` — images, videos, audio files
- `code-build` — build artifacts, compiled output (dist, build, out, obj, bin)
- `documents` — user documents, office files
- `virtualization` — VM images, WSL distros, Docker data
- `user-data` — personal user data (Desktop, Documents, Pictures, etc.)
- `recycle-bin` — Recycle Bin / $Recycle.Bin
- `browser-cache` — browser profile data, cache
- `logs` — application and system logs
- `unknown` — unclassifiable content

#### Scenario: Single category assignment
- **WHEN** a folder content type is clearly identifiable
- **THEN** system shall assign exactly one primary category

#### Scenario: Mixed content
- **WHEN** a folder contains files from multiple categories
- **THEN** system shall assign the dominant category based on total file size per type

### Requirement: Assign cleanup recommendation
The system SHALL assign each scanned folder a cleanup recommendation level based on its category.

#### Scenario: Safe to clean
- **WHEN** a folder is classified as `temporary-files`, `browser-cache`, or `recycle-bin`
- **THEN** system shall mark it as `✅ safe-to-clean`

#### Scenario: Cautious
- **WHEN** a folder is classified as `dependency-cache`, `code-build`, or `logs`
- **THEN** system shall mark it as `⚠️ cautious` and explain what would be affected

#### Scenario: Not recommended
- **WHEN** a folder is classified as `downloads`, `user-data`, `documents`, `media`, or `virtualization`
- **THEN** system shall mark it as `🔍 review-manually` and suggest user inspect before deleting
```

## openspec/changes/disk-space-analyzer/specs/report-formatter/spec.md

- Source: openspec/changes/disk-space-analyzer/specs/report-formatter/spec.md
- Lines: 1-33
- SHA256: bda619323c5bec01f5623d9c283dbfd151907c3e95dc39779bbdbbaddf477b8d

```md
## ADDED Requirements

### Requirement: Format as tree table
The system SHALL format scan results as a tree-structured table showing folder hierarchy, size, category, and recommendation.

#### Scenario: Top-level table
- **WHEN** scan results are ready
- **THEN** system shall output a table with columns: Folder Path | Size | Category | Recommendation

#### Scenario: Tree indentation
- **WHEN** showing nested folders (recursion result)
- **THEN** system shall indent child folders under their parent using tree characters (├── └──)

### Requirement: Sort by size
The system SHALL sort folders by size in descending order, with the largest folder first.

#### Scenario: Descending sort
- **WHEN** displaying scan results
- **THEN** folders at the same hierarchy level shall be ordered from largest to smallest

### Requirement: Show summary
The system SHALL display a summary at the top of the report showing total scanned path, total analyzed size, number of folders found, and scan duration.

#### Scenario: Summary line
- **WHEN** scan completes
- **THEN** system shall display: "Scanned: C:\Users | Total: 85.3 GB | Folders >1GB: 12 | Duration: 3.2s"

### Requirement: Highlight large offenders
The system SHALL visually highlight the top 5 largest folders (of the top-level scan) to draw user attention.

#### Scenario: Top 5 emphasis
- **WHEN** more than 5 folders are returned
- **THEN** the 5 largest folders shall be marked with a visual indicator (e.g. `**` or `[TOP]`)
```

