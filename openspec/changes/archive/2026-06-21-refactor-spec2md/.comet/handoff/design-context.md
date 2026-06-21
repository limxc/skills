# Comet Design Handoff

- Change: refactor-spec2md
- Phase: design
- Mode: compact
- Context hash: 1d73dc99e3ea6f190c86c52c028ff1c72f624e99fe41f36545bd8a8853ae8336

Generated-by: comet-handoff.sh

OpenSpec remains the canonical capability spec. This handoff is a deterministic, source-traceable context pack, not an agent-authored summary.

## openspec/changes/refactor-spec2md/proposal.md

- Source: openspec/changes/refactor-spec2md/proposal.md
- Lines: 1-35
- SHA256: 36001237ba0dff6600509418931683fcd362373de5c513dd564f36093529a659

```md
## Why

spec2article-wechat 当前强依赖 wewrite 作为写作、SEO、发布管道，但实际使用中发现：

1. wewrite 的发布和 SEO 功能对仅需输出 Markdown 稿件的场景过于冗余
2. 频繁的 question 工具调用导致交互繁琐
3. 技能名称和输出路径与微信公众号绑定，限制了通用性

现需重构为通用 Markdown 文章生成工具，移除 wewrite 依赖，自建写作人格系统。

## What Changes

- **重命名**: `spec2article-wechat` → `spec2md`，触发命令改为 `/spec2md`
- **移除 wewrite 依赖**: 删除 Step 4-8 wewrite 管道，取消 wewrite 和发布配置检查
- **自建写作人格**: 从 wewrite 移植 `style.yaml` 人格系统到技能自身
- **依赖精简**: 仅保留 openspec + drawio-skill 依赖检查
- **输出目录变更**: `spec2article-wechat-output/article-{date}.md` → `docs/{change-name}-{date}/`（内含 `.md` + 配图 `.png` + `.drawio` 源文件）
- **交互层级规则**: x.x 层使用 `question` 工具，x.x.x 层（草案展示、修改、定稿）直接对话
- **流程精简**: Pre 1-3 + 写作 + 后处理（去掉 Step 4-9）

## Capabilities

### New Capabilities
- `writing-persona`: 写作人格选择和加载，从 style.yaml 匹配人格并注入写作流程
- `spec2md-pipeline`: 核心管线，包括 change 选择、素材提取、drawio 配图、草案交互、Markdown 输出

### Modified Capabilities
- 无（新技能，不修改已有 specs）

## Impact

- **移除依赖**: wewrite、微信发布配置
- **保留依赖**: drawio-skill（用于配图）、openspec（作为数据源）
- **文件变动**: `SKILL.md` 全新重写，`scripts/position.py` 修改输出目录逻辑，新增 `<skill-dir>/style.yaml`
- **产物路径变更**: 从独立输出目录改为项目 `docs/` 下
```

## openspec/changes/refactor-spec2md/design.md

- Source: openspec/changes/refactor-spec2md/design.md
- Lines: 1-56
- SHA256: 27f208a606cf2ffff3a3b9aeca6c7e665ed744507c7f921f163d1adba985b90b

```md
## Context

当前 spec2article-wechat 是一个 Comet → 微信公众号文章的转换工具，包含 9 个步骤：

- Pre 1-3：环境检查、Change 选择、素材提取、drawio 配图
- Step 4-8：委托 wewrite 完成写作、SEO、视觉 AI、排版发布
- Step 9：后处理

实际使用发现 wewrite 的发布能力与仅需 Markdown 输出的需求不匹配，且大量 question 工具调用降低了交互效率。需要重构为通用 Markdown 输出工具。

## Goals / Non-Goals

**Goals:**
- 移除 wewrite 依赖（写作人格文件移植到自身）
- 重命名为 spec2md，输出到 `docs/{change-name}-{date}/`
- 交互层级规则：x.x 用 question，x.x.x 直接对话
- 最终产物为 Markdown 稿件 + drawio 配图

**Non-Goals:**
- 不实现 SEO/发布/封面图功能
- 不改动 drawio-skill 的逻辑
- 不改变 `position.py` 核心逻辑（仅改输出路径）

## Decisions

**1. 写作人格移植方案**
- 从 wewrite 的 `style.yaml` 复制 persona 配置到 `<skill-dir>/style.yaml`
- 人格匹配逻辑自建：按 topic 关键词与 changes 描述的文本相似度排序取 top 3
- 写作流程：选人格 → 结构化素材 → 人格注入 prompt → 生成文章 → 展示 → 修改 → 定稿

**2. 交互层级设计**
- x.x 层（2.1 Change 选择、2.3 骨架匹配）：使用 question 工具，需用户明确选择
- x.x.x 层（3.4.x 草案展示/修改/定稿）：直接对话，不用 question 工具

**3. 输出目录结构**
```
docs/{change-name}-{date}/
├── article.md
├── {change-name}-architecture.png
├── {change-name}-architecture.drawio
└── ...
```

**4. 流程结构（精简后）**
```
Pre-1  环境检查（openspec + drawio）+ 位置读取
Pre-2  Change 选择 + 写作讨论（标题/骨架/配图/人格）
Pre-3  素材提取 + 生图 + 写作 + 草案确认 → Final Draft
后处理   position 更新 + 回复
```

## Risks / Trade-offs

- [R1] 写作质量下降：移除 wewrite 后失去范文注入和自检逻辑 → 在 prompt 中保留写作质量要求，用写作人格弥补
- [R2] style.yaml 可能与 wewrite 未来版本不同步 → 明确标注移植版本号，后续独立维护
- [R3] 用户习惯变更：命令从 `/spec2article-wechat` 改为 `/spec2md` → SKILL.md 中标注别名提示
```

## openspec/changes/refactor-spec2md/tasks.md

- Source: openspec/changes/refactor-spec2md/tasks.md
- Lines: 1-37
- SHA256: c8927ec62d0c8d44b45e58a62b7140fc4d045bef8d4c322a693025392508d814

```md
## 1. SKILL.md 重构

- [ ] 1.1 重写 SKILL.md：流程精简为 Pre-1 + Pre-2 + Pre-3 + 后处理，移除 Step 4-9
- [ ] 1.2 更新触发命令：`/spec2article-wechat` → `/spec2md`
- [ ] 1.3 更新描述和 metadata（版本、依赖、名称）
- [ ] 1.4 添加交互层级规则说明（x.x 用 question，x.x.x 直接对话）

## 2. 写作人格移植

- [ ] 2.1 从 wewrite 复制 `style.yaml` 到 `<skill-dir>/style.yaml`
- [ ] 2.2 实现人格匹配逻辑：按 topic 关键词排序取 top 3
- [ ] 2.3 实现人格注入：选中人格写入 prompt 指导写作
- [ ] 2.4 在 Pre-2.5 中加载本地 `style.yaml` 而非 wewrite 路径

## 3. 依赖检查精简

- [ ] 3.1 移除 wewrite 依赖检测
- [ ] 3.2 移除微信发布配置检测
- [ ] 3.3 保留 openspec 项目结构检测和 drawio 检测
- [ ] 3.4 更新异常处理表

## 4. 输出目录迁移

- [ ] 4.1 输出目录从 `spec2article-wechat-output/` 改为 `docs/{change-name}-{date}/`
- [ ] 4.2 更新 position.py：输出目录引用改为 `SPEC2MD_PROJECT_ROOT` 而非 `SPEC2ARTICLE_PROJECT_ROOT`
- [ ] 4.3 确认输出包含：`article.md` + `*.png` + `*.drawio`

## 5. 交互层改造

- [ ] 5.1 Pre-2.1（change 选择）、Pre-2.3（骨架确认）保留 question 工具
- [ ] 5.2 3.4.x（草案展示、收集反馈、修改、定稿）改为直接对话
- [ ] 5.3 移除 3.3 图片确认中的 question 工具（改为直接对话）

## 6. 最终验证

- [ ] 6.1 运行完整 `/spec2md` 流程确认无报错
- [ ] 6.2 验证产物输出到 `docs/{change-name}-{date}/`
```

## openspec/changes/refactor-spec2md/specs/spec2md-pipeline/spec.md

- Source: openspec/changes/refactor-spec2md/specs/spec2md-pipeline/spec.md
- Lines: 1-55
- SHA256: a1e7d65a87c568337ef5143b855db97529666a5f122d76e6fdc01fafbcfecb2d

```md
## ADDED Requirements

### Requirement: Change selection with question tool
The system SHALL display pending changes and ask the user for each change whether to include it, skip it, or hide it permanently, using the `question` tool at the x.x hierarchy level.

#### Scenario: Single change selection
- **WHEN** user runs `/spec2md` and pending changes exist
- **THEN** system uses `question` tool to ask per-change: write article / hide / skip

### Requirement: Skeleton matching and confirmation
The system SHALL automatically match a writing skeleton based on change metadata and use `question` tool for user confirmation at the x.x layer.

#### Scenario: Single change skeleton
- **WHEN** exactly 1 change is selected
- **THEN** system recommends SCQA skeleton and uses `question` tool for confirmation

### Requirement: drawio diagram generation
The system SHALL load drawio-skill to generate diagrams based on change content, with auto-retry (≤2 rounds).

#### Scenario: Architecture diagram generation
- **WHEN** the change involves architecture changes
- **THEN** system generates architecture diagram via drawio-skill

### Requirement: Draft display and modification via direct chat
The system SHALL display the full draft inline and collect modification feedback through direct conversation (not `question` tool) at the x.x.x hierarchy level.

#### Scenario: Draft inline display
- **WHEN** draft is ready
- **THEN** system shows full article inline (not written to file yet)

#### Scenario: Modification cycles
- **WHEN** user requests a change via direct chat
- **THEN** system applies the change and re-displays the full article with `📝` markers on changed sections

### Requirement: Final draft output to docs/
The system SHALL write the confirmed final draft to `docs/{change-name}-{date}/article.md`, along with diagram images and drawio source files.

#### Scenario: Output structure
- **WHEN** user confirms final draft
- **THEN** system creates `docs/{change-name}-{date}/article.md` + `*.png` + `*.drawio`

### Requirement: Dependency check — openspec only
The system SHALL only check for openspec project structure. wewrite and WeChat publish config checks SHALL be removed.

#### Scenario: openspec check
- **WHEN** Pre-1 runs
- **THEN** system checks `openspec/changes/` directory exists
- **THEN** system does NOT check for wewrite or WeChat publish config

### Requirement: Position tracking after publication
The system SHALL mark selected changes as processed via `position.py processed` after the article is finalized.

#### Scenario: Post-write position update
- **WHEN** article is finalized and output files are written
- **THEN** system runs `position.py processed <change-dir-1> ...`
```

## openspec/changes/refactor-spec2md/specs/writing-persona/spec.md

- Source: openspec/changes/refactor-spec2md/specs/writing-persona/spec.md
- Lines: 1-26
- SHA256: 26b2a8598e93e808064a59791e71829c99abfdc5ac2da95e85c41a9123f87702

```md
## ADDED Requirements

### Requirement: Persona selection from style.yaml
The system SHALL load writing personas from `<skill-dir>/style.yaml` and offer the user top 3 candidates based on topic keyword matching with selected changes.

#### Scenario: Persona matched by topic
- **WHEN** user has selected changes with descriptions containing topic keywords
- **THEN** system sorts personas by topic similarity and presents top 3

#### Scenario: No matching topic
- **WHEN** no topic keywords match any persona
- **THEN** system defaults to the 3 most recently used personas

### Requirement: Persona display with style sample
Each persona candidate SHALL include a style excerpt from `style.yaml` so the user can judge the writing tone before selecting.

#### Scenario: Persona selection with sample
- **WHEN** system presents persona options
- **THEN** each option includes a sample text excerpt from the persona's example field

### Requirement: Persona injection into writing prompt
The selected persona's style description SHALL be injected into the writing prompt to guide article generation.

#### Scenario: Article generated with persona
- **WHEN** user confirms a persona
- **THEN** the writing prompt includes the persona's style description, tone, and vocabulary preferences
```

