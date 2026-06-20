---
name: spec2article-wechat
description: >-
    Generate WeChat public account (微信公众号) articles from Comet development
    archives. Use this skill whenever the user says /spec2article-wechat, wants to
    write a WeChat article from completed changes, summarize development work for
    WeChat, or generate a dev blog from Comet archives. Also triggers on Chinese
    phrases like "写一篇公众号文章" or "把最近的变更写成微信推文" when paired
    with Comet workflow context. Delegates to wewrite for writing/SEO/publishing
    and to drawio-skill for architectural and flow diagrams.
license: MIT
metadata:
    version: 1.3.0
    created: 2026-06-19
    dependencies:
        - url: https://github.com/oaker-io/wewrite
          name: WeWrite
          type: skill
          note: Writing/SEO/formatting/publishing pipeline (Step 4-8)
        - url: https://github.com/Agents365-ai/365-skills
          name: drawio-skill
          type: skill
          note: Diagram generation (Pre-3.3) via draw.io CLI export
        - url: https://github.com/anomalyco/opencode
          name: Comet
          type: skill
          note: Prerequisite — produces the archive changes consumed by this skill; install via `npx skills add anomalyco/opencode -g`
---

# /spec2article-wechat — Generate WeChat Articles from Comet Archives

Converts Comet development archives into WeChat public account articles. Three custom pre-steps (replace wewrite's Step 1-3) → wewrite's unmodified Step 4-8 → post-processing.

**重要：本文所有「使用 question 工具」指令均指调用 question 工具函数，而非输出问题 JSON 文本。每次 question 调用只问一项决策，不得合并多项。**
**约定：`<skill-dir>` = 本 SKILL.md 所在目录。**

**Trigger**: `/spec2article-wechat` — select changes, write article

```
Pre-1  环境 + 配置 + 位置读取   →   Position JSON
Pre-2  Change 选择 + 写作讨论   →   Topic + Outline + Image Plan
Pre-3  素材提取 + 生图 + 确认 + 草案调整 → Final Draft + Embedded Images
──────────────────────── 进入 wewrite（强制交互模式）
Step 4-8  wewrite 管道          →   Published Article + history.yaml
Step 9   后处理                 →   Position Updated + User Reply
```

## Pre-1: 环境 + 配置 + 位置读取

**Input**: Comet project with `openspec/changes/` or `archive/`
**Output**: Ready env + pending change list

**1.1** Comet 环境检查 — 检测当前项目是否存在 Comet 工作流结构：
```
Test-Path -LiteralPath "openspec/changes/" -PathType Container 或 Test-Path -LiteralPath "archive/"
```
存在则继续；不存在则输出 "Comet 项目结构未找到。请在已初始化 Comet（含 openspec/changes/ 或 archive/ 目录）的项目中运行本 skill。" 后退出。

**1.2** 依赖检查 — 逐项检测，缺失项一键安装后告知用户重启：

```
~/.agents/skills/wewrite/    → npx skills add oaker-io/wewrite -g
~/.agents/skills/drawio-skill/    → npx skills add Agents365-ai/365-skills -g
"C:\Program Files\draw.io\draw.io.exe" --version    → 下载 https://github.com/jgraph/drawio-desktop/releases
```

发布配置检测 → `~/.agents/skills/wewrite/config.yaml` 有 `wechat.appid` 则就绪；否则 question：A) 仅预览 B) 填写配置后退出。

**1.3** position 状态：`python <skill-dir>/scripts/position.py status`
**1.4** 未处理 changes：`python <skill-dir>/scripts/position.py pending`
- 状态：`processed`=已用、`skipped`=跳过
- 无 pending → 展示清单，执行 `python <skill-dir>/scripts/position.py list` 或 `unskip`，退出

## Pre-2: Change 选择 + 写作讨论

**Input**: Pending change list from Pre-1
**Output**: Selected changes + title + skeleton type + image plan + persona

**🔴 CHECKPOINT — 以下步骤确定文章素材范围。选错的 change 需 unskip 才能重选。**

**2.1** 展示change清单，逐项依次调用 question 工具：

```
1 | 2026-06-19-disk-space-analyzer | full    | 新增磁盘分析工具
2 | 2026-06-19-disk-analyzer-tests | tweak   | 补充测试用例
```

调用 question 工具时，将"略过"列为首选项：

> 选项：
> - 略过 → 下次继续显示
> - 写文章 → 传入后续
> - 不再显示 → `python <skill-dir>/scripts/position.py skipped <dir>`


**2.2** 标题确认 — 生成 3 候选标题，用 question 工具让用户选择或自定义。

**2.3** 骨架确认 — 按以下规则自动匹配（从选中 changes 的 metadata 推断）：

| 判定条件 | 推荐骨架 | 适用场景 |
|---------|---------|---------|
| 只选了 1 个 change | SCQA | 单 feature 技术叙事 |
| 选了 ≥2 个 change，且 change 名含时间/日期序列 | 时间线复盘 | 开发历程回顾 |
| 选中 changes 的 `.comet.yaml` 中任意一个 `workflow: tweak` 或包含架构/重构关键词 | 对比 | 改造类变更 |
| 选中 changes 混合了 full+tweak/hotfix 类型 | 时间线复盘 | 不同类型变更按时间组织 |
| 其余多 change 情况 | 清单 | 多个不相关 feature |

匹配后展示给用户确认，可替换为其他骨架。

**重要：骨架仅决定叙事逻辑和段落组织方式，不得将骨架名称（如"SCQA"、"时间线复盘"）直接用作文章的章节标题。写入 3.5 稿件时，所有标题必须重新拟定为符合公众号风格的自然标题。**

**2.4** 配图计划确认 — 遍历 changes 检查 design.md/proposal.md，按内容类型逐项问（每次 question 只问一种配图类型）：
- 架构变更 → 架构对比图？
- 流程变化 → 流程图？
- 新增/重构 → 目录结构？

**2.5** 写作人格确认 — 从 `style.yaml` 的 `personas` 列表中，按 `topic` 关键词与 changes 描述的文本相似度排序，取前 3 个候选展示给用户。每个候选必须附带一段风格展示文字（从 `style.yaml` 中该 persona 的示例文本摘录），让用户直观感受写作风格。若无 topics 数据，默认推荐最常用的 3 个 persona。

## Pre-3: 素材提取 + 生图 + 确认

**Input**: Selected changes + image plan
**Output**: Structured materials + confirmed images + final draft `.md`

**3.1** 读每个 change 内容 → 结构化素材（兼容 wewrite）：
- `topic` / `framework` / `materials` — 动机、技术要点、架构变化、影响范围

来源：`proposal.md` → Why/What/Impact；`design.md` → Context/Decisions/Trade-offs；`tasks.md` → 完成清单；`.comet.yaml` → 类型/日期

**3.2** 配图 — 按类型选 drawio-skill 预设：

| 内容类型 | 预设 | 输出文件 |
|---------|------|---------|
| 架构变更/系统设计 | Architecture diagram | `{change-name}-architecture.png` |
| 业务流程/工作流 | Flow diagram | `{change-name}-flow.png` |
| ML 模型/训练管线 | ML/Deep Learning diagram | `{change-name}-ml.png` |
| 类/接口变更 | UML class diagram | `{change-name}-uml.png` |
| 协议/交互变更 | Sequence diagram | `{change-name}-sequence.png` |
| 数据模型/模式变更 | ER diagram | `{change-name}-er.png` |

`{slug}` = change 名称的 kebab-case 英文（即 `.comet.yaml` 所在目录名）。

执行：按以下模板构造 drawio 指令 → skill tool 加载 drawio-skill → 委托生成 → 自检修复 ≤2 轮：

```markdown
请为「{change-name}」生成一张 {预设}。
场景：{从 design.md/proposal.md 提取 1-2 句核心要点}
输出路径：{spec2article-wechat-output}/{change-name}-{type}.png
要求：高清画质，Microsoft YaHei 字体，中文标注，简洁美观。
```

目录结构 → `tree`/`Get-ChildItem` → 嵌入代码块。

**🔴 CHECKPOINT — 以下配图将嵌入最终文章。确认前可修改，确认后需重跑才可替换。**

**3.3** 每张图 question 工具（单选）：A) 没问题 B) 修改（≤5 轮）C) 跳过。达 5 轮强制接受或跳过。

**3.4** 草案展示与全文交互调整（展示 → 反馈 → 修改 → 确认，循环直至定稿）

**3.4.1** 展示草案：将 3.1 的结构化素材与 3.3 已确认图片/代码块组合为完整文章草案，inline 展示（不写入文件）。

**3.4.2** 收集反馈 — 用 question 工具收集用户意见：可针对任意段落提出修改要求，也可提全局性修改（如"缩短篇幅"）。

**3.4.3** 执行修改 — 局部意见仅调整对应段落；全局意见一次性应用到全文。修改后重新展示全文，变更处前标注 `📝`。

**3.4.4** 确认定稿：
> A) 确认定稿，写入文件  → 进入 3.5
> B) 继续修改  → 回到 3.4.2

**3.5** 生成最终稿：`spec2article-wechat-output/article-{date}.md` — 含素材 + 已确认图片/代码块。

## Step 4-8: wewrite 管道（零改动，强制交互模式 — 每步必须用户确认，不得自动推进）

**Input**: Final draft from Pre-3
**Output**: Published/previewed article + `history.yaml`

**🔴 CHECKPOINT — 即将进入 wewrite（强制交互模式）。每个决策点必须用 question 工具经用户确认后才能推进。确认前可退出，进入后自动暂停。**

加载 wewrite SKILL.md，prompt 头部追加：

```
[强制交互模式] 你必须用 question 工具在每个决策点暂停并等待用户确认，不得自动跳过。
强制暂停点：Step 4 写作 → Step 5 SEO → Step 6 视觉AI → Step 7 发布 → Step 8 收尾。
用户选择"取消并退出"时终止流程，changes 不标记 processed，下次可重选。
```

**Step 4** 写作 — 维度随机化 → 人格加载 → 范文注入 → 写文章 → 快速自检
**Step 5** SEO + 验证 — 3 标题 + 摘要 + 标签 + 质量验证 + humanness_score
**Step 6** 视觉 AI — 封面（有 key 生图/无 key 出提示词）+ 内文配图（已有 `![alt]` 的跳过）
**Step 7** 排版 + 发布 — converter → Pre-3 PNG 自动上传微信 CDN → publish 或 preview
**Step 8** wewrite 收尾 — 写入 `history.yaml`

## Step 9: 后处理 — position 更新 + 回复

**Input**: Published article + used change list
**Output**: Position JSON updated + user reply

**🔴 CHECKPOINT — 执行后 changes 标记 processed，重新发布需 unskip。确认文章已发布/保存再执行。**

**9.1** position 更新：
```
python <skill-dir>/scripts/position.py processed <change-dir-1> ... <change-dir-N>
```
跳过项已在 Pre-2.1 处理，无需重复。

**9.2** 回复用户：
- 最终标题 + media_id / HTML 路径
- 覆盖 N 个 changes
- 输出位于 `spec2article-wechat-output/`
- 下次运行不再显示已 processed 的 changes

## 异常与边界处理

| 步骤 | 触发条件 | 一线修复 | 仍失败兜底 |
|------|---------|---------|-----------|
| Pre-1.2 | wewrite/drawio-skill 目录不存在 | `npx skills add ... -g` 安装 | 告知重启后重试，终止 |
| Pre-1.2 | drawio CLI 不存在 | 提示下载 | 跳过配图，纯文字输出 |
| Pre-1.4 | 无未处理 changes | 展示已处理清单 | 执行 `position.py list` 查看所有 change，终止 |
| Pre-2.1 | change 缺 proposal.md | 跳过，标记 skipped | 告知用户手动检查，继续其余 |
| Pre-3.2 | drawio 导出失败 | 重试 1 次（简化描述） | 跳过配图，标注"生成失败" |
| Pre-3.3 | 图片修改达 5 轮 | 强制接受或跳过 | 用户二选一 |
| Pre-3.4 | 用户反馈不明确或不可操作 | 用 question 工具请求具体修改示例 | 使用当前版本作为最终稿 |
| Pre-3.4 | 调整循环超过 8 轮 | 用 question 工具询问用户接受当前版本或继续修改 | 用户选择决定 |
| Step 4-8 | wewrite 无响应 >30s | 重载 wewrite SKILL.md | 手动介入或跳过发布 |
| Step 9.1 | position.py 执行失败 | 检查 JSON 文件可写 | 告知手动执行，继续回复 |
| 全局 | 用户中断 | 保存进度到 `spec2article-wechat-output/` 中间文件 | 告知可重跑，已有素材复用 |

## 反例与黑名单

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 在非 Comet 项目中使用 | 无 changes，position.py 报错 | Pre-1.1 目录探测会自动检查并退出，不依赖环境变量 |
| 2 | 手动编辑 `.wechat-article-position.json` | 状态不一致，跳/重写 change | 只用 `position.py` |
| 3 | 跳过 Pre-2 配图决策 | 缺少关键配图 | 架构/流程变更至少生成一张图 |
| 4 | 写非技术类公众号 | 素材提取不匹配 | 非技术类直接用 wewrite |
| 5 | 单 change 用"时间线复盘"骨架 | 内容撑不起 | 单 change 用 SCQA |
| 6 | 图片反复修改 >5 轮 | 边际收益递减 | 5 轮后强制接受或跳过 |
| 7 | 将草案写入文件后再让用户修改 | 反复写文件浪费操作，用户不便逐段评论 | inline 展示全文，收集反馈后再写入 |
| 8 | 修改后不重新展示全文 | 用户不知道改了哪里，失去上下文 | 每次调整后重新展示完整草案 |
| 9 | 未获用户明确确认即写入文件 | 文章未定稿就进入下游管道 | 等待用户选择"确认定稿"后再写入 |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | `status`/`pending`/`processed`/`skipped`/`unskip`/`list`/`reset` |

## 引用参考

- wewrite `SKILL.md` — Step 4-7 原始指令
- wewrite `toolkit/converter.py` — Markdown → 微信 HTML
- wewrite `toolkit/cli.py` — 发布 CLI
- drawio-skill `SKILL.md` — Pre-3.3 委托指令
