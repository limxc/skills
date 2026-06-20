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
