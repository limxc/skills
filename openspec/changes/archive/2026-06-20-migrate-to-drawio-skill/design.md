## Context

`wechat-article-skill` currently generates article illustrations using Python `diagrams` library with YAML spec files. The `diagrams` library has limited node types (10), no brand icons, no self-check mechanism, and requires Graphviz. The output quality is inconsistent, and there is no iterative feedback loop for refinement.

The drawio-skill from Agents365-ai offers a superior approach: LLM-generated `.drawio` XML → draw.io Desktop CLI export → self-check/auto-fix → iterative feedback. It supports 10,000+ official shapes, 321 AI/LLM brand icons, 6 diagram type presets, and automated layout.

## Goals / Non-Goals

**Goals:**
- Replace Pre-3 diagram generation from `diagrams` library to drawio-skill
- Install drawio-skill as an external dependency
- Pre-3 delegates to drawio-skill directly (no bridge script; same pattern as Step 4-7 delegating to wewrite)
- Update SKILL.md Pre-3 phase instructions
- Update install scripts to install drawio-skill dependency
- Output images at 1080px width for WeChat Retina scaling

**Non-Goals:**
- Not modifying wewrite pipeline (Step 4-8)
- Not changing image embedding/upload logic
- Not removing existing archive reading, writing discussion, or persona loading
- Not modifying other drawing skills (excalidraw, mermaid, plantuml)

## Decisions

### Decision 1: Install drawio-skill via npx skills add
Install drawio-skill as an external skill dependency rather than reimplementing its logic. The wechat-article-skill's Pre-3 phase will load drawio-skill's SKILL.md and delegate diagram generation to it.

**Rationale:** drawio-skill contains extensive scripts (shapesearch.py, aiicons.py, autolayout.py, validate.py) that would be expensive to reimplement. Direct installation via `npx skills add Agents365-ai/365-skills -g` keeps the skills ecosystem aligned.

### Decision 2: Direct delegation to drawio-skill (no bridge script)

Pre-3 directly loads drawio-skill's SKILL.md and delegates diagram generation, the same way Step 4-7 delegates to wewrite without any bridge script. The existing `scripts/diagram.py` is removed (no longer needed) along with the `diagrams` Python package dependency.

**Rationale:** Zero-coupling approach. wechat-article-skill's Pre-3 describes WHAT images are needed and WHICH drawio-skill preset to use, then loads drawio-skill to handle HOW. This avoids maintaining a redundant adapter and keeps both skills independently upgradeable.

### Decision 3: WeChat image dimension via drawio --export --scale
Use draw.io CLI's `--scale` parameter to achieve 1080px output width. The base .drawio file uses a standard canvas (typically ~1920px default), and `--scale` adjusts the export resolution. Alternatively, set the page dimensions in .drawio XML directly.

**Rationale:** `drawio --export --width 1080` is the simplest and most reliable approach. draw.io CLI supports `--width` to specify exact pixel width, maintaining aspect ratio.

### Decision 4: Pre-3 flow modification
The Pre-3 phase changes from:
```
[Old] Describe need → Write YAML spec → diagram.py → PNG → User confirms
```
to:
```
[New] Pre-3 identifies image need + diagram type → loads drawio-skill SKILL.md →
      drawio-skill generates .drawio XML → drawio --export (--width 1080) →
      Self-check → User feedback loop (≤5 rounds) → Final PNG → embed in article
```

**Rationale:** The new flow is more capable (supports iteration and self-check) while maintaining the same confirmation step at the end.

## Risks / Trade-offs

- **[Dependency] draw.io Desktop CLI required** → The user confirmed it is already installed. Document in SKILL.md as a prerequisite.
- **[Migration] Existing YAML spec files no longer work** → The old `diagram.py` (diagrams library) is replaced. Old specs are deprecated but can be manually converted if needed.
- **[Integration] drawio-skill availability** → If drawio-skill fails to install or load, we lose diagram generation. Mitigation: add a check in Pre-1 that validates drawio-skill availability and draw.io CLI presence, failing early with clear instructions.
- **[Quality] draw.io CLI export fidelity** → Font rendering may differ between platforms. Mitigation: document font requirements (Microsoft YaHei for Chinese support) and test on Windows before release.
