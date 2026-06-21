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
