# Comet Design Handoff

- Change: refine-spec2article-interaction
- Phase: design
- Mode: compact
- Context hash: fdb56ab9d865a822a56af1a1aedc44449e529c7e3567b3a8743001b77d5a4bec

Generated-by: comet-handoff.sh

OpenSpec remains the canonical capability spec. This handoff is a deterministic, source-traceable context pack, not an agent-authored summary.

## openspec/changes/refine-spec2article-interaction/proposal.md

- Source: openspec/changes/refine-spec2article-interaction/proposal.md
- Lines: 1-23
- SHA256: fcd316237c3e4c6e35bc37eef47e05dee009cb614b9cf67457cdbdf60a783147

```md
## Why

spec2article-wechat 的 Pre-3（素材提取 + 生图）完成后直接进入 wewrite 管道，缺少让用户审视全文草案并反馈调整的环节。当前流程只有配图粒度的确认（Pre-3.3）和进入 wewrite 前的二进制确认，用户无法在最终落笔前对文章内容提出修改意见，导致文章发布后不满意需重跑整个流程。

## What Changes

- 在 Pre-3.3（配图确认）后新增「展示草稿全文 + 用户反馈 + 调整」步骤
- 原 Pre-3.4（生成草稿文件）顺延为 Pre-3.5
- 强化 wewrite 管道强制交互模式约束（默认全自动，必须改为交互模式

## Capabilities

### New Capabilities

- `draft-review`: 在生成最终草稿前，提供完整的草案展示、用户反馈收集与内容调整能力

### Modified Capabilities

（无 — 该修改不涉及 openspec/specs/ 中已定义的 capability，仅修改 agent skill 的 SKILL.md 文件）

## Impact

- 修改 `~/.agents/skills/spec2article-wechat/SKILL.md`：Pre-3 步骤结构调整
```

## openspec/changes/refine-spec2article-interaction/design.md

- Source: openspec/changes/refine-spec2article-interaction/design.md
- Lines: 1-26
- SHA256: 12e6e4551a412533563e85702c6bf2861e00de951ba03066928aa1b3baa82d28

```md
## Context

spec2article-wechat 是一个 Comet 技能，将开发归档转换微信公众号文章。当前 Pre-3 流程为：读change → 生图 → 配图确认 → 生成草稿 → 进入 wewrite。缺少用户在草稿落地前审视全文、反馈修改的环节。

## Goals / Non-Goals

**Goals:**
- 在配图确认后增加草案展示 + 用户反馈 + 调整循环
- 确保 agent 执行 wewrite 管道时强制交互模式
- 调整后草稿稳定后才写入 `.md` 文件

**Non-Goals:**
- 不改变 wewrite 本身的逻辑
- 不改变 Pre-1/Pre-2 流程
- 不改配图生成逻辑

## Decisions

- **草案展示方式**：在 Pre-3.4 中，agent 用 question 工具展示草案全文供用户逐段审阅，而非直接输出到文件。用户可提出修改要求，agent 调整后再次展示，循环直到用户满意
- **调整循环上限**：不设硬上限（防止 agent 自行截断），但每次调整后 agent 需确认用户是否有进一步修改需求
- **wewrite 交互模式**：在 Step 4-8 入口前，prompt 头部追加 `[交互模式]` 指令，明确要求在每个决策点（标题、骨架、配图、预览、发布）用 question 工具暂停确认

## Risks / Trade-offs

- 增加步骤导致单次流程延长 → 但避免发布后不满意需重跑，整体效率反而提升
- 无上限循环可能导致无限修改 → 由用户自然决定何时满意，而非 agent 单方面截断
```

## openspec/changes/refine-spec2article-interaction/tasks.md

- Source: openspec/changes/refine-spec2article-interaction/tasks.md
- Lines: 1-16
- SHA256: c553d4979746662d54789cbc52c3dca5c6c545fb26d22b7e01f493d710741a51

```md
## 1. 修改 SKILL.md — 流程结构调整

- [ ] 1.1 在 Pre-3 中，将原 3.4 顺延为 3.5，插入新的 3.4（草案展示 + 反馈调整）
- [ ] 1.2 新增 3.4 步骤的详细指令：展示草案全文、收集用户反馈、调整循环、确认定稿
- [ ] 1.3 更新异常处理表，补充草案调整环节的异常场景
- [ ] 1.4 更新反例与黑名单，覆盖与草案调整相关的反模式

## 2. 强化 wewrite 交互模式约束

- [ ] 2.1 在 Step 4-8 入口描述中，明确要求强制交互模式（不得自动推进）
- [ ] 2.2 更新 CHECKPOINT 提示语，强调交互模式的具体暂停点

## 3. 验证

- [ ] 3.1 运行 `npx skills validate` 验证 SKILL.md 格式
- [ ] 3.2 全局安装更新后的 skill 并确认加载正常
```

## openspec/changes/refine-spec2article-interaction/specs/draft-review/spec.md

- Source: openspec/changes/refine-spec2article-interaction/specs/draft-review/spec.md
- Lines: 1-34
- SHA256: c25025c3a5f06aad7f4cb53dfdafb14ee0f0053577a7728145402dcac39674b0

```md
## ADDED Requirements

### Requirement: Draft review before final generation

The system SHALL present the full draft to the user for review before writing the final article file. The agent SHALL collect user feedback, apply adjustments, and repeat until the user confirms satisfaction.

#### Scenario: User reviews draft and requests changes

- **WHEN** agent presents the full draft text to the user
- **THEN** user can provide specific feedback, and agent adjusts the draft accordingly

#### Scenario: User confirms draft is ready

- **WHEN** user confirms the draft meets expectations
- **THEN** agent writes the final `.md` file to `spec2article-wechat-output/article-{date}.md`

#### Scenario: Multiple adjustment rounds

- **WHEN** user requests further changes after an adjustment
- **THEN** agent continues to present updated drafts and collect feedback until user confirms

### Requirement: wewrite interactive mode enforcement

The system SHALL enforce interactive mode when entering the wewrite pipeline (Step 4-8). The agent MUST pause at every decision point (title selection, skeleton choice, image decisions, preview confirmation, publish confirmation) using the question tool.

#### Scenario: Interactive mode activation

- **WHEN** agent loads wewrite SKILL.md
- **THEN** agent prepends `[交互模式]` directive requiring question tool pauses at all decision points

#### Scenario: Decision point pause

- **WHEN** wewrite reaches a decision point (title, skeleton, image, preview, publish)
- **THEN** agent MUST use the question tool to get user confirmation before proceeding
```

