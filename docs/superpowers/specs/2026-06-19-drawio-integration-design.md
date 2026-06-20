---
comet_change: migrate-to-drawio-skill
role: technical-design
canonical_spec: openspec
archived-with: 2026-06-20-migrate-to-drawio-skill
status: final
---

# Design: drawio-skill Integration for wechat-article-skill

## Context

`wechat-article-skill` currently generates article illustrations using Python `diagrams` library with YAML spec files. The `diagrams` library has limited node types (10), no brand icons, no self-check mechanism, and requires Graphviz. Output quality is inconsistent and there is no iterative feedback loop.

`drawio-skill` (Agents365-ai) offers LLM-generated `.drawio` XML → draw.io Desktop CLI export → self-check/auto-fix → iterative feedback. It supports 10,000+ official shapes, 321 AI/LLM brand icons, 6 diagram type presets, and automated layout.

## Goals / Non-Goals

**Goals:**
- Replace Pre-3 diagram generation from `diagrams` library to drawio-skill
- Pre-3 directly delegates to drawio-skill (same pattern as Step 4-7 delegating to wewrite)
- Extend Pre-2.2c diagram type matching to cover all 6 drawio-skill presets
- Remove `scripts/diagram.py` and `diagrams` Python dependency
- Update install scripts to install drawio-skill as dependency
- Output images at drawio-skill's default high-quality settings

**Non-Goals:**
- Not modifying wewrite pipeline (Step 4-8)
- Not changing image embedding/upload logic
- Not removing existing archive reading, writing discussion, or persona loading
- Not modifying other drawing skills (excalidraw, mermaid, plantuml)

## Integration Pattern

```
Pre-3: Image Generation (NEW)
┌──────────────────────────────────────────────────────────────┐
│ 1. Identify image need + diagram type from archive content   │
│                                                              │
│ 2. Load drawio-skill SKILL.md via Skill tool                 │
│                                                              │
│ 3. Invoke drawio-skill with:                                 │
│    - Natural language description of the diagram             │
│    - Diagram type preset (architecture/ML/flow/UML/seq/ER)   │
│    - WeChat quality note (high-DPI for downscaling)          │
│                                                              │
│ 4. drawio-skill generates .drawio XML                        │
│    → drawio CLI export PNG                                   │
│    → Self-check + auto-fix (≤2 rounds)                       │
│    → Present to user                                         │
│                                                              │
│ 5. User feedback loop (≤5 rounds):                           │
│    A) Accept → embed in article                              │
│    B) Modify → describe changes → re-render                  │
│    C) Skip → no image for this section                       │
└──────────────────────────────────────────────────────────────┘
```

## Diagram Type Mapping

| Archive Content Pattern | drawio-skill Preset |
|------------------------|-------------------|
| Architecture changes, system design | Architecture diagram |
| Business process changes, workflow | Flow diagram |
| ML model changes, training pipeline | ML/Deep Learning diagram |
| Class/interface changes | UML class diagram |
| Protocol/interaction changes | Sequence diagram |
| Data model/schema changes | ER diagram |

## Affected Files

| File | Action |
|------|--------|
| `SKILL.md` | Update Pre-1 deps, Pre-2.2c matching, Pre-3 flow, scripts table |
| `scripts/diagram.py` | Remove |
| `scripts/requirements.txt` | Remove `diagrams` |
| `references/complete-flow.md` | Update Pre-3 flow |
| `AGENTS.md` | Update diagram generation approach |
| `install.ps1` | Add drawio-skill installation |
| `install.sh` | Add drawio-skill installation |
| `specs/diagram-generation/spec.md` | Remove 1080px hard constraint |

## Risks / Mitigation

| Risk | Mitigation |
|------|-----------|
| draw.io Desktop CLI not available | Pre-1 check + early failure with instructions |
| drawio-skill fails to load | Pre-1 check, early error before Pre-3 |
| Old YAML specs obsoleted | Deprecated; manual conversion if needed |
| Font rendering differences | Document font reqs (Microsoft YaHei) in SKILL.md |
