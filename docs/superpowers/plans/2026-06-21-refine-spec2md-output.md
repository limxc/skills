---
change: refine-spec2md-output
design-doc: docs/superpowers/specs/2026-06-21-refine-spec2md-output-design.md
base-ref: 523a2fe5c60f92b60136b062f3f1176e387d628d
---

# Refine spec2md output — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Change spec2md output path from `docs/` to `spec2md/`, add no-framework option to Step 3.3, restructure Step 4 with README timeline append, then optimize workflow with skill-creator.

**Architecture:** Single file modification (SKILL.md, README.md). All changes are textual find-and-replace or inline additions to the markdown-based skill definition.

**Tech Stack:** PowerShell (pwsh), Markdown

## Global Constraints

- All code blocks in SKILL.md must use correct PowerShell syntax
- `{change-name}` and `{date}` variable naming must remain consistent
- Article output directory changes from `docs/` to `spec2md/` everywhere

---

### Task 1: Replace all `docs/` references with `spec2md/` in SKILL.md

**Files:**
- Modify: `skills/spec2md/SKILL.md` — all occurrences

- [x] **Step 1: Replace all `docs/` with `spec2md/` in SKILL.md**

  Replace every occurrence of `docs/` with `spec2md/` in the SKILL.md file. This affects:
  - Step 3 Input/Output description
  - Step 3.2 image output directory
  - Step 3.6 directory creation (`New-Item -ItemType Directory -Path "spec2md/{...}"`)
  - Step 3.6 file writing paths
  - Step 4 reply path

  Run: `(Get-Content skills/spec2md/SKILL.md) -replace 'docs/', 'spec2md/' | Set-Content skills/spec2md/SKILL.md`

- [x] **Step 2: Verify replacements**

  Check no remaining `docs/` references in the output path context:
  ` Select-String -Path skills/spec2md/SKILL.md -Pattern 'docs/'`

  Expected: no matches (or only false positives like "documentation")

- [x] **Step 3: Commit**

  ```
  git add skills/spec2md/SKILL.md
  git commit -m "refactor: change spec2md output path from docs/ to spec2md/"
  ```

### Task 2: Add "不使用框架" option to Step 3.3

**Files:**
- Modify: `skills/spec2md/SKILL.md` — Step 3.3 section

- [x] **Step 1: Edit Step 3.3 to add the no-framework option**

  Append a new option to the question tool in Step 3.3:
  ```
  D) 不使用框架 — 跳过框架选择，仅按骨架结构组织文章
  ```

- [x] **Step 2: Commit**

  ```
  git add skills/spec2md/SKILL.md
  git commit -m "feat: add no-framework option to Step 3.3"
  ```

### Task 3: Restructure Step 4 — add README timeline, reorganize reply

**Files:**
- Modify: `skills/spec2md/SKILL.md` — Step 4 section

- [x] **Step 1: Restructure Step 4 sections**

  Renumber:
  - 4.1 position.py processed (unchanged)
  - 4.2 history.yaml update (unchanged)
  - 4.3 Add: README 需求时间线追加 (new)
  - 4.4 Reply summary (was 4.3, enhanced)

  Add Step 4.3 content — PowerShell code block to append timeline link to README.md:
  ```powershell
  $readmePath = Join-Path $projectRoot "README.md"
  $linkEntry = "- [$title - $date](spec2md/$articleDir/article.md)"
  $sectionHeader = "## 需求时间线"

  if (-not (Test-Path $readmePath)) {
      "`n$sectionHeader`n`n$linkEntry" | Set-Content $readmePath
  } else {
      $content = Get-Content $readmePath -Raw
      if ($content -match "$sectionHeader[\s\S]*?(?=\n## |\z)") {
          $section = $matches[0]
          $newSection = "$section`n$linkEntry"
          $content = $content.Replace($section, $newSection)
          Set-Content $readmePath $content
      } else {
          Add-Content $readmePath "`n$sectionHeader`n`n$linkEntry"
      }
  }
  ```

  Update Step 4.4 (reply) to include:
  - ✅ position 已更新
  - ✅ history.yaml 已记录
  - ✅ 需求时间线已追加
  - Output path: `spec2md/{article-name}-{date}/article.md`

- [x] **Step 2: Commit**

  ```
  git add skills/spec2md/SKILL.md
  git commit -m "feat: add README timeline append, restructure Step 4"
  ```

### Task 4: Optimize spec2md workflow with skill-creator

**Files:**
- Read: `skills/spec2md/SKILL.md`
- Modify: `skills/spec2md/SKILL.md` (based on skill-creator output)

- [x] **Step 1: Run skill-creator on spec2md**

  Use skill-creator to analyze and optimize spec2md workflow efficiency.

- [x] **Step 2: Review skill-creator suggestions and apply**

  Review the optimization recommendations. Apply improvements that enhance workflow efficiency without changing the skill's core capabilities.

- [x] **Step 3: Commit**

  ```
  git add skills/spec2md/SKILL.md
  git commit -m "perf: apply skill-creator workflow efficiency suggestions"
  ```
