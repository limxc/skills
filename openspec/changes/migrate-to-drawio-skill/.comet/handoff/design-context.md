# Comet Design Handoff

- Change: migrate-to-drawio-skill
- Phase: design
- Mode: compact
- Context hash: da732a6d3464efbb466236a9ff882a6919281c9fb25edd370c30305e4ff436c7

Generated-by: comet-handoff.sh

OpenSpec remains the canonical capability spec. This handoff is a deterministic, source-traceable context pack, not an agent-authored summary.

## openspec/changes/migrate-to-drawio-skill/proposal.md

- Source: openspec/changes/migrate-to-drawio-skill/proposal.md
- Lines: 1-31
- SHA256: 1d6c63b140a73a683266fdd6c261bd0fe3b9944c2ee4cb2a203a4269a4ddcadf

```md
## Why

当前 wechat-article-skill 使用 Python `diagrams` 库生成文章配图，存在节点类型有限、无法使用品牌图标、无自检修复、依赖 Graphviz 等问题，图片质量难以满足微信公众号要求。drawio-skill 方案基于 draw.io 桌面 CLI 导出，支持 10,000+ 形状库、AI/LLM 品牌图标、自检修复和迭代优化，能显著提升配图质量和生成效率。

## What Changes

- 将 wechat-article-skill Pre-3 阶段的图片生成方式从 Python `diagrams` 库 + YAML spec 方案完全替换为 drawio-skill 方案
- 安装 drawio-skill 作为外部依赖（`npx skills add`）
- Pre-3 直接委托 drawio-skill 生成图片（类似 Step 4-7 委托 wewrite），无桥接脚本
- 移除 `scripts/diagram.py`（不再需要）
- 更新 `SKILL.md` 中 Pre-3 阶段指令，反映新的图片生成流程
- 更新 `references/complete-flow.md` 流程文档
- 图片输出规格：宽度 1080px，支持微信公众号 Retina 缩放
- 移除 `diagrams` Python 包依赖

## Capabilities

### New Capabilities
- `diagram-generation`: 基于 drawio-skill 的公众号文章配图生成能力，支持 .drawio XML 生成、CLI 导出、自检修复和迭代反馈优化

### Modified Capabilities

<!-- 无现有 spec 受影响 -->

## Impact

- **脚本**：`scripts/diagram.py` 重写
- **文档**：`SKILL.md` Pre-3 阶段指令更新，`references/complete-flow.md` 更新
- **依赖**：新增 drawio-skill 外部依赖 + draw.io 桌面版 CLI；移除 `diagrams` Python 包
- **安装脚本**：`install.sh` / `install.ps1` 增加 draw.io 桌面版检测和 drawio-skill 安装步骤
- **无 API 变更**，无 breaking changes
```

## openspec/changes/migrate-to-drawio-skill/design.md

- Source: openspec/changes/migrate-to-drawio-skill/design.md
- Lines: 1-60
- SHA256: 72faca1266db77ceb8146eb60ef9f1fe3cb8d676ca6f2caa0fa008d37f990898

```md
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
```

## openspec/changes/migrate-to-drawio-skill/tasks.md

- Source: openspec/changes/migrate-to-drawio-skill/tasks.md
- Lines: 1-34
- SHA256: b7ec6092c93f8fe77f6c10ab6b20eeb629bf1119eeb690aa1afa9be2b39e0bfb

```md
## 1. Dependency Installation

- [ ] 1.1 Install drawio-skill via `npx skills add Agents365-ai/365-skills -g`
- [ ] 1.2 Verify draw.io Desktop CLI is operational (`drawio --version`)
- [ ] 1.3 Verify drawio-skill loads correctly (`/drawio` trigger available)
- [ ] 1.4 Remove `diagrams` from Pre-1 Python dependency check in SKILL.md

## 2. Update SKILL.md Pre-3 Phase

- [ ] 2.1 Update Pre-3.3 instruction to use drawio-skill for diagram generation instead of YAML spec + diagram.py flow
- [ ] 2.2 Add drawing-type selection logic matching drawio-skill's 6 presets (architecture, ML, flow, UML, sequence, ER)
- [ ] 2.3 Add 1080px width export requirement to WeChat Image Rule section
- [ ] 2.4 Add drawio-skill as a dependency in the Pre-1 dependency check
- [ ] 2.5 Update the scripts table to reflect new diagram.py role
- [ ] 2.6 Update the skill description metadata to indicate drawio-skill integration

## 3. Pre-3 Delegation to drawio-skill

- [ ] 3.1 Update Pre-3.3 instructions to load drawio-skill SKILL.md and delegate diagram generation (same pattern as Step 4-7 delegating to wewrite)
- [ ] 3.2 Add natural language description template for drawio-skill invocation, including 1080px width and WeChat quality requirements
- [ ] 3.3 Remove `scripts/diagram.py` (no longer needed) and the `diagrams` Python package dependency
- [ ] 3.4 Remove YAML spec generation from Pre-3 flow

## 4. Update Install Scripts

- [ ] 4.1 Update `install.ps1` to install drawio-skill after wechat-article-skill
- [ ] 4.2 Update `install.sh` to install drawio-skill after wechat-article-skill
- [ ] 4.3 Verify draw.io CLI presence during installation
- [ ] 4.4 Update requirements.txt to remove `diagrams` package

## 5. Update Documentation

- [ ] 5.1 Update `references/complete-flow.md` to reflect new drawio-skill flow in Pre-3
- [ ] 5.2 Update `AGENTS.md` to reflect new diagram generation approach
```

## openspec/changes/migrate-to-drawio-skill/specs/diagram-generation/spec.md

- Source: openspec/changes/migrate-to-drawio-skill/specs/diagram-generation/spec.md
- Lines: 1-60
- SHA256: bf23ecd57a446e80f8b7fd571b1f2c7a33a417ecab2b9c9acc33f5f9dac01303

```md
## ADDED Requirements

### Requirement: LLM generates .drawio XML from natural language description
The system SHALL use drawio-skill to transform a natural language description (e.g., "微服务电商架构图，包含 API Gateway、Auth/User/Order 微服务、Kafka 消息队列") into a `.drawio` XML file conforming to the draw.io format specification.

#### Scenario: Generate architecture diagram
- **WHEN** user describes an architecture scenario in natural language
- **THEN** the system SHALL produce a valid `.drawio` XML file with the appropriate shapes, edges, and layout

#### Scenario: Generate flow diagram
- **WHEN** user describes a business process or workflow
- **THEN** the system SHALL produce a `.drawio` XML file with semantic flow shapes (parallelogram I/O, diamond decisions)

#### Scenario: Generate ML/deep learning diagram
- **WHEN** user describes a neural network architecture
- **THEN** the system SHALL produce a `.drawio` XML file with tensor shape annotations and layer-type color coding

### Requirement: Export PNG using drawio-skill default high-quality settings
The system SHALL use draw.io desktop CLI (`drawio --export`) to export the `.drawio` file to PNG format using drawio-skill's default export settings. The output image SHALL be of sufficient quality for WeChat article use (high-DPI for Retina downscaling).

#### Scenario: Standard export
- **WHEN** draw.io CLI exports a `.drawio` file to PNG
- **THEN** the output PNG SHALL be valid and render correctly

#### Scenario: Custom dimension override
- **WHEN** user specifies custom dimensions in the description
- **THEN** the system SHALL use the user-specified dimensions

### Requirement: Self-check and auto-fix exported images
The system SHALL perform a self-check on the exported PNG by reading pixel data to detect label overlap, text truncation, and line stacking. If issues are detected, the system SHALL automatically fix them (up to 2 rounds) before presenting to the user.

#### Scenario: Auto-fix overlapping labels
- **WHEN** the exported PNG contains overlapping labels
- **THEN** the system SHALL detect the overlap and adjust the layout, then re-export

#### Scenario: No issues found
- **WHEN** the exported PNG passes all self-checks
- **THEN** the system SHALL present the image to the user without modification

### Requirement: Iterative feedback loop (up to 5 rounds)
The system SHALL support user feedback and iterative refinement. After presenting a generated image, the user MAY describe modifications, and the system SHALL adjust the `.drawio` XML and re-export accordingly, for up to 5 rounds.

#### Scenario: User requests modification
- **WHEN** user says "move the database node to the left and add a cache layer"
- **THEN** the system SHALL modify the `.drawio` XML, re-export, show the updated image, and wait for further feedback

#### Scenario: Max iteration reached
- **WHEN** 5 feedback rounds are exhausted
- **THEN** the system SHALL present the current version and ask the user to accept or restart

### Requirement: Use brand icons and official shape library
The system SHALL support searching and using 10,000+ official draw.io shapes (AWS, Azure, GCP, Cisco, Kubernetes, UML, BPMN, ER) via drawio-skill's shapesearch mechanism, and 321 AI/LLM brand icons (OpenAI, Claude, Gemini, etc.) via the aiicons mechanism.

#### Scenario: Use AWS Lambda shape
- **WHEN** user requests "add an AWS Lambda function"
- **THEN** the system SHALL use the exact official draw.io style for AWS Lambda shape

#### Scenario: Use AI brand icon
- **WHEN** user requests "add Claude AI icon"
- **THEN** the system SHALL use the Claude brand icon from drawio-skill's aiicons library
```

