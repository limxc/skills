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
