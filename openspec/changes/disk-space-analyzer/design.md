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
