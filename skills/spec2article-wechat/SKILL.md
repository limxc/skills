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
    version: 1.1.0
    created: 2026-06-19
    dependencies:
        - url: https://github.com/oaker-io/wewrite
          name: WeWrite
          type: skill
          note: Writing/SEO/formatting/publishing pipeline (Step 4-7)
        - url: https://github.com/Agents365-ai/365-skills
          name: drawio-skill
          type: skill
          note: Diagram generation (Pre-3.3) via draw.io CLI export
        - name: Comet
          type: skill
          note: Prerequisite — produces the archive changes consumed by this skill
---

# /spec2article-wechat — Generate WeChat Articles from Comet Archives

You are a writing assistant that converts Comet development archives into WeChat public account (微信公众号) articles. Your workflow has three custom pre-steps that replace wewrite's Step 2-3, followed by wewrite's unmodified Step 4-8 pipeline.

## Trigger

- `/spec2article-wechat` — 选择 changes，写文章
- `/spec2article-wechat 写一篇关于最近变更的文章` — 同上

## Pipeline Overview

```
Pre-1  环境 + 配置 + 位置读取
Pre-2  Change 选择 + 写作讨论
Pre-3  素材提取 + 生图 + 确认
──────────────────────── 进入 wewrite（零改动）
Step 4  写作
Step 5  SEO + 验证
Step 6  视觉 AI
Step 7  排版 + 发布
Step 8  wewrite 收尾
Step 9  后处理：position + 回复
```

## Pre-1: 环境 + 配置 + 位置读取

**1.1** Comet 环境检查 — Comet 是本技能的前置依赖，运行时 `$COMET_GUARD` 等变量应已就绪。若 `$COMET_GUARD` 为空，提示 "Comet not found. This skill requires Comet workflow." 后退出。

**1.2** 检测外部依赖，一键安装所有缺失项：

```
missing = []
  ~/.agents/skills/wewrite/ 不存在?      → missing += "npx skills add oaker-io/wewrite -g"
  ~/.agents/skills/drawio-skill/ 不存在?  → missing += "npx skills add Agents365-ai/365-skills -g"
  drawio --version 失败?                  → missing += "下载 draw.io Desktop (https://github.com/jgraph/drawio-desktop/releases)"

if missing 非空:
  顺序执行所有安装命令
  告知用户: "以下依赖已安装，请重启 agent 后重试：{missing}" 后退出
```

检测 wewrite 发布配置：

- `~/.agents/skills/wewrite/config.yaml` 有 `wechat.appid` → 发布就绪
- 否则用 question 工具询问用户（单选）：
  - **A) 跳过发布，仅本地预览**
  - **B) 填写配置** → 告知路径后退出等待

**1.3** 读取 position 状态：`python <skill-dir>/scripts/position.py status`

**1.4** 查找未处理 changes（遍历 `openspec/changes/` 及 `archive/`，过滤已标记的）：`python <skill-dir>/scripts/position.py pending`

状态含义：`processed`=已用、`skipped`=跳过。若无未处理项 → 告知用户，建议运行 `position.py list` 或 `unskip`。

## Pre-2: Change 选择 + 写作讨论

**🔴 CHECKPOINT — 以下步骤将确定文章素材范围。选错的 change 需等 unskip 才能重选。**

**2.1** 展示未处理 changes 编号清单，然后用 **question 工具（多选）** 让用户勾选：

展示格式：
```
 1 | 2026-06-19-disk-space-analyzer | full    | 新增磁盘分析工具
 2 | 2026-06-19-disk-analyzer-tests | tweak   | 补充测试用例
 3 | 2026-06-20-migrate-to-drawio   | full    | 迁移到 drawio
```

多选选项示例：
- `☐ 1 — 写文章` / `☐ 1 — 跳过（不再提示）`
- 每项独立勾选，避免文本解析歧义

确认后：
- 跳跃项 → `python <skill-dir>/scripts/position.py skipped <dir>`
- 写文章项 → 传入后续流程
- 未选中项 → 下次继续显示

**2.2** 写作讨论：

a) **标题讨论** — 生成 3 个候选标题，用户选择或自定义。

b) **骨架推荐** — 根据 change 类型推荐，用户确认：
- SCQA（单 feature 技术叙事）
- 时间线复盘（多 change 合写）
- 对比（before/after 改造）
- 清单（多个独立功能点）

c) **配图决策** — 遍历选中 changes，检查 design.md/proposal.md，对每项用 question 工具逐项确认：
- 有架构变更 → 架构对比图？
- 有流程变化 → 流程图？
- 有新增/重构 → 目录结构？

**2.3** 写作人格 — 检查 wewrite 的 `style.yaml` 中 `writing_persona`；无则推荐 top 2 让用户选。

## Pre-3: 素材提取 + 生图 + 确认

**3.1** 读取每个选中 change 的内容：
- `proposal.md` → Why、What Changes、Impact
- `design.md` → Context、Decisions、Trade-offs（如有）
- `tasks.md` → 完成的任务清单
- `.comet.yaml` → workflow 类型、日期

**3.2** 输出结构化素材（兼容 wewrite 格式）：
- `topic` / `framework` / `materials` — 变更动机、技术要点、架构变化、影响范围

**3.3** 执行配图决策：

根据类型确定 drawio-skill 预设：

| 内容类型              | drawio-skill 预设        |
| --------------------- | ------------------------ |
| 架构变更、系统设计    | Architecture diagram     |
| 业务流程变化、工作流  | Flow diagram             |
| ML 模型变更、训练管线 | ML/Deep Learning diagram |
| 类/接口变更           | UML class diagram        |
| 协议/交互变更         | Sequence diagram         |
| 数据模型/模式变更     | ER diagram               |

对每张图：
1. 构建自然语言描述（含关键组件、连接关系、布局）
2. 用 skill tool 加载 drawio-skill
3. 委托生成：传递自然语言描述 + 预设类型 + 导出要求 "高清画质，Microsoft YaHei 字体"
4. drawio-skill 自检修复（≤2 轮）

有目录结构 → 用 `tree`/`Get-ChildItem` → 嵌入代码块。

**🔴 CHECKPOINT — 以下配图将嵌入最终文章。确认前可修改，确认后需重跑才可替换。**

**3.4** 交互确认生图结果：

对每张图用 question 工具（单选）让用户选择：
- **A) 没问题** → 嵌入 `![alt](spec2article-wechat-output/{slug}.png)`
- **B) 修改** → 用户描述修改需求 → drawio-skill 重新修改 → 重新导出（≤5 轮）
- **C) 跳过** → 纯文字段落下掉

达到 5 轮后强制接受或跳过。目录结构代码块同此循环。

**3.5** 生成草稿 `spec2article-wechat-output/article-{date}.md`，含素材和已确认图片/代码块。

## Step 4-7: wewrite 管道（零改动，强制交互模式）

**🔴 CHECKPOINT — 即将进入 wewrite 管道，后续步骤由 wewrite 驱动。确认前可退出，进入后不可撤回。**

完全使用 wewrite 原始 SKILL.md + toolkit/。加载 wewrite SKILL.md 后，在 prompt 头部追加：

```
[交互模式] 必须用 question 工具在每个决策点暂停等待确认，不得自动推进。
需暂停：标题选择、骨架选择、配图决策、文章预览确认、发布确认。
```

**Step 4** 写作 — 维度随机化 → 人格加载 → 范文注入 → 写文章 → 快速自检。

**Step 5** SEO + 验证 — 3 标题 + 摘要 + 标签 + 质量验证 + humanness_score。

**Step 6** 视觉 AI — 封面（有 key 生图/无 key 出提示词）+ 内文配图（已有 `![alt]` 的跳过）。

**Step 7** 排版 + 发布 — converter → Pre-3 PNG 自动上传微信 CDN → publish 或 preview。

## Step 8: wewrite 收尾

**8.1** wewrite 写入 `history.yaml`。

## Step 9: 后处理 — position 更新 + 回复

**🔴 CHECKPOINT — 执行后 changes 标记为 processed，重新发布需 unskip。确认文章已发布/保存再执行。**

**9.1** 更新 position：
```
python <skill-dir>/scripts/position.py processed <change-dir-1> ... <change-dir-N>
```
跳过项已在 Pre-2 处理，无需重复。

**9.2** 回复用户：
- 最终标题 + media_id / HTML 路径
- 覆盖 N 个 changes
- 输出位于 `spec2article-wechat-output/`
- 下次运行不再显示已 processed 的 changes

## 反例与黑名单

以下操作不做或慎做，否则结果不符合预期：

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 在非 Comet 项目中使用 `/spec2article-wechat` | 无 changes 可读，position.py 报错 | 仅在有 `openspec/changes/` 或 `archive/` 的 Comet 项目中使用 |
| 2 | 手动编辑 `.wechat-article-position.json` | position 状态不一致，跳/重写 change | 只用 `position.py` 命令管理状态 |
| 3 | 跳过 Pre-2 配图决策 | 文章缺少关键架构/流程配图 | 至少为架构变更和流程变化生成配图 |
| 4 | 用本技能写非技术类公众号（行业观点/产品推广） | 素材提取逻辑不匹配，输出质量差 | 使用 wewrite 直接写非技术类文章 |
| 5 | 单 change 选"时间线复盘"骨架 | 内容撑不起多段落叙事 | 单 change 用 SCQA，多 change 用时间线复盘 |
| 6 | 图片反复修改超过 5 轮 | 产出延迟，边际收益递减 | 5 轮后强制接受或跳过 |

## 脚本

| 脚本                  | 用途                           |
| --------------------- | ------------------------------ |
| `scripts/position.py` | 跟踪/查询/更新 change 处理位置 |

## 引用参考

- wewrite `SKILL.md` — Step 4-7 原始指令
- wewrite `toolkit/converter.py` — Markdown → 微信 HTML
- wewrite `toolkit/cli.py` — 发布 CLI
- drawio-skill `SKILL.md` — Pre-3.3 委托指令
