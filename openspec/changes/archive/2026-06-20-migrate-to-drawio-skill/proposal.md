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
