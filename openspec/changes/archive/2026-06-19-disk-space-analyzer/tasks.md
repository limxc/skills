## 1. Skill Structure

- [x] 1.1 Create `skills/disk-analyser-skill/` directory with SKILL.md, scripts/, references/
- [x] 1.2 Write SKILL.md with activation triggers, workflow instructions, and output format guidance

## 2. PowerShell Scripts

- [x] 2.1 Implement `scripts/scan_disk.py` — recursive directory scanning with size calculation
- [x] 2.2 Implement `scripts/categorize_folder.py` — folder classification by content type
- [x] 2.3 Implement `scripts/format_report.py` — structured output formatting
- [x] 2.4 Create `scripts/__init__.py` — main entry point orchestrating all modules

## 3. Integration & Verification

- [x] 3.1 Add `/disk-space-analyzer` command definition in SKILL.md
- [x] 3.2 Verify skill directory structure and file completeness
- [x] 3.3 Create `requirements.txt` if needed (stdlib-only, no external deps)
- [x] 3.4 Test scripts locally against a sample directory
- [x] 3.5 Install skill globally and verify agent can trigger it
