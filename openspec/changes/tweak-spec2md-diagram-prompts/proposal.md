## Why

spec2md 的配图模块使用 drawio-skill 生成图表时，经常出现连线遮挡、字体覆盖和布局混乱问题。同时安装说明指向了错误的仓库地址（`Agents365-ai/365-skills`），需要更新为正确的 `Agents365-ai/drawio-skill`。

## What Changes

1. **优化配图提示词** — 在 Step 3.2 的 6 种图表提示词模板中，增加布局质量约束指令（间距规则、连线避免重叠、路由通道、字体渲染等），让 drawio-skill 生成的图表更美观清晰。
2. **修正安装地址** — 更新 SKILL.md 头部 metadata 的依赖 URL 和 Step 1.2 的安装命令，指向正确的 drawio-skill 仓库。

## Capabilities

### New Capabilities
- 无（不新增 capability）

### Modified Capabilities
- 无（不修改 spec 验收场景）

## Impact

- `~/.agents/skills/spec2md/SKILL.md` — 提示词和安装说明修改
