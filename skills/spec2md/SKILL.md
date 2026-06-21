---
name: spec2md
description: >-
    Generate Markdown articles from Comet development archives.
    Use this skill whenever the user says /spec2md, wants to write an article
    from completed changes, or summarize development work.
    Delegates to drawio-skill for architectural and flow diagrams.
metadata:
    version: 2.0.0
    created: 2026-06-20
    dependencies:
        - url: https://github.com/Agents365-ai/365-skills
          name: drawio-skill
          type: skill
          note: Diagram generation (Step 3.2) via draw.io CLI export
        - url: https://github.com/anomalyco/opencode
          name: Comet
          type: skill
          note: Prerequisite — produces the archive changes consumed by this skill
---

# /spec2md — Generate Markdown Articles from Comet Archives

Converts Comet development archives into Markdown articles with diagrams. Four-step workflow: environment check → change selection + writing discussion → material extraction + diagram + writing → post-processing.

**约定：`<skill-dir>` = 本 SKILL.md 所在目录。**
**交互层级：Step 2.1 / 2.3 使用 question 工具；Step 3.4.x（草案展示 → 反馈 → 修改 → 定稿）使用直接对话，不得使用 question 工具。**

```
Step 1  环境检查（openspec + drawio）+ position 读取
Step 2  Change 选择 + 写作讨论（标题/骨架/配图/人格+记忆注入）
Step 3  素材提取 + drawio 配图 + 写作 + 草案交互 → 定稿
Step 4  position 更新 + 记忆写入 + 回复
```

## Step 1: 环境检查

**Input**: Comet project with `openspec/changes/` or `archive/`
**Output**: Ready env + pending change list

**1.1** openspec 结构检查：

```
Test-Path -LiteralPath "openspec/changes/" -PathType Container
```

存在则继续；不存在提示并在 `..` 层级重试一次。仍不存在则输出 "Comet 项目结构未找到。请在已初始化 Comet（含 openspec/changes/ 目录）的项目中运行本 skill。" 后退出。

**1.2** drawio-skill 依赖检查：

```
Test-Path -LiteralPath "$env:USERPROFILE\.agents\skills\drawio-skill\"
```

不存在 → `npx skills add Agents365-ai/365-skills -g` 安装后告知用户重启。

draw.io CLI 检查：

```
& "C:\Program Files\draw.io\draw.io.exe" --version
```

不存在 → question 工具询问：A) 跳过配图，纯文字输出 B) 下载后重启。

**不检查 wewrite。不检查 WeChat 发布配置。**

**1.3** position 状态：

```
python <skill-dir>/scripts/position.py status
```

**1.4** 未处理 changes：

```
python <skill-dir>/scripts/position.py pending
```

- 无 pending changes → 展示所有 changes 清单（含已 processed/skipped 标记），询问是否执行 `unskip` 恢复。用户无操作则退出。

## Step 2: Change 选择 + 写作讨论

**Input**: Pending change list from Step 1
**Output**: Selected changes + confirmed title + skeleton type + image plan + persona (+ optional memory)

**2.1** 展示 pending change 清单，逐项用 question 工具（每次一项）：

```
1 | 2026-06-19-disk-space-analyzer | full    | 新增磁盘分析工具
2 | 2026-06-19-disk-analyzer-tests | tweak   | 补充测试用例
```

选项：
- **写文章** → 传入后续步骤
- **不再显示** → `python <skill-dir>/scripts/position.py skipped <dir>`
- **略过** → 不标记，下次继续显示

所有 change 处理完毕后，收集选中的 changes 列表传入 Step 2.2。

**🔴 CHECKPOINT — 以下步骤确定文章素材范围。选错的 change 需 unskip 才能重选。**

**2.2** 标题确认 — 根据选中 changes 内容生成 3 个候选标题，用 question 工具：

```
选项：
A) {候选标题 1}
B) {候选标题 2}
C) {候选标题 3}
D) 自定义
```

选择 D 时，提示用户输入自定义标题。

**2.3** 骨架匹配 — 按以下规则自动匹配，用 question 工具确认：

| 判定条件 | 推荐骨架 | 适用场景 |
|---------|---------|---------|
| 只选了 1 个 change | SCQA | 单 feature 技术叙事 |
| 选了 ≥2 个 change，且名含时间/日期序列 | 时间线复盘 | 开发历程回顾 |
| 任意 change 的 `.comet.yaml` 中 `workflow: tweak` 或含架构/重构关键词 | 对比 | 改造类变更 |
| 混合了 full+tweak/hotfix 类型 | 时间线复盘 | 不同类型变更按时间组织 |
| 其余多 change 情况 | 清单 | 多个不相关 feature |

展示匹配骨架 + 原因，用户可替换为其他骨架类型。骨架仅决定叙事逻辑和段落组织方式，**不得将骨架名称直接用作章节标题**。写入 article.md 时所有标题须重新拟定为自然标题。

**🔴 CHECKPOINT — 骨架确认后，以下步骤确定配图和写作风格。**

**2.4** 配图计划 — 遍历选中的 changes，检查 `design.md` / `proposal.md`，按内容类型逐项用 question 工具（每次只问一种配图类型）：

| 检测到内容 | 推荐配图 | 说明 |
|-----------|---------|------|
| 架构变更/系统设计 | Architecture diagram | 组件关系、层级结构 |
| 业务流程/工作流 | Flow diagram | 状态流转、决策路径 |
| ML 模型/训练管线 | ML/Deep Learning diagram | 模型结构、数据管线 |
| 类/接口变更 | UML class diagram | 类层次、接口依赖 |
| 协议/交互变更 | Sequence diagram | 调用顺序、消息交换 |
| 数据模型变更 | ER diagram | 实体关系、字段设计 |

每项用户确认：A) 生成此图 B) 不需要 C) 暂不确定（留空）

**2.5** 写作人格选择：

**2.5.1** 读取 `<skill-dir>/personas/` 下所有 `*.yaml` 文件，提取每人的 `name` / `description` / `topics`（如存在）字段。

**2.5.2** 按 topic 关键词与选中 changes 描述的文本相似度排序，取前 3 个候选。若无 topic 字段，默认推荐最常用的 3 个 persona（`tech-coder`, `industry-observer`, `midnight-friend`）。

**2.5.3** 每个候选附带一段风格展示文字（从 yaml 的 `data_intro_pattern` 示例摘录），用 question 工具让用户选择。

**2.5.4** 记忆注入 — 检查 `<skill-dir>/personas/<name>.memory.json` 是否存在。存在则读取内容，作为额外上下文注入 Step 3.3 写作 prompt。

## Step 3: 素材提取 + 配图 + 写作

**Input**: Selected changes + confirmed title + skeleton + image plan + persona
**Output**: Final article at `docs/{change-name}-{date}/article.md`

**3.1** 素材提取 — 遍历每个选中的 change，读取：
- `proposal.md` → Why（动机）/ What（内容）/ Impact（影响范围）
- `design.md` → Context（背景）/ Decisions（决策与权衡）/ Trade-offs
- `tasks.md` → 完成清单（checklist）
- `.comet.yaml` → type（change 类型）/ date（日期）

整理为结构化素材摘要，inline 展示给用户快速确认。

**3.2** 配图生成 — 按 Step 2.4 确认的配图计划，逐项调用 drawio-skill：

按以下模板构造 drawio 指令 → skill tool 加载 drawio-skill → 委托生成 → 自检修复 ≤2 轮：

```markdown
请为「{change-name}」生成一张 {预设类型}。
场景：{从 design.md/proposal.md 提取 1-2 句核心要点}
输出路径：{output-dir}/{change-name}-{type}.png
要求：高清画质，Microsoft YaHei 字体，中文标注，简洁美观。
```

输出目录：`docs/{change-name}-{date}/`

每张图生成后，用 question 工具（单选）：A) 没问题 B) 修改（≤5 轮）C) 跳过。达 5 轮强制接受或跳过。

保留 drawio 源文件到 `docs/{change-name}-{date}/{change-name}-{type}.drawio`。

**🔴 CHECKPOINT — 以下配图将嵌入最终文章。确认前可修改，确认后需重跑才可替换。**

**3.3** 写作 — 整合以下元素生成文章：

1. Step 3.1 的结构化素材
2. Step 3.2 已确认的配图路径（相对路径 `{change-name}-{type}.png`）
3. Step 2.2 的标题
4. Step 2.3 的骨架结构
5. Step 2.5 选中 persona 的完整 yaml 内容（作为写作风格指南注入）
6. Step 2.5.4 的 memory 内容（如存在，偏好/历史偏好补充）

输出格式为完整 Markdown，配图使用 `![alt]({change-name}-{type}.png)`。

**3.4** 草案交互 — 全对话流程，不得使用 question 工具：

**3.4.1 展示草案**：将生成的完整文章 inline 展示（不写入文件）。文章前标注 `--- 草案 ---`，后标注 `--- 草案结束 ---`。

**3.4.2 收集反馈**：使用对话收集用户意见。用户可针对任意段落提出修改要求，也可提全局性修改（如"缩短篇幅"、"换一种语气"）。

**3.4.3 执行修改**：局部意见仅调整对应段落；全局意见一次性应用到全文。修改后重新展示全文，变更处前标注 `📝`。

**3.4.4 确认定稿**：
- 用户说"确认"、"定稿"、"可以"、"就这样"或明确表示同意 → 进入 3.5
- 用户提出新修改意见 → 回到 3.4.2

**🔴 CHECKPOINT — 定稿确认后将写入文件，后续修改需手动编辑。**

**3.5** 写入最终文件：

```
docs/{change-name}-{date}/
├── article.md
├── {change-name}-architecture.png   (如生成)
├── {change-name}-flow.png          (如生成)
├── {change-name}-sequence.png      (如生成)
├── {change-name}-uml.png           (如生成)
├── {change-name}-er.png            (如生成)
└── {change-name}-ml.png            (如生成)
```

`{change-name}` = 选中 changes 中第一个的目录名，`{date}` = 当天日期（YYYY-MM-DD）。

创建目录：

```
New-Item -ItemType Directory -Path "docs/{change-name}-{date}" -Force
```

写入 `docs/{change-name}-{date}/article.md`，含完整 Markdown 内容和配图引用。

如选中多个 change，在 article.md 文件名前加上 `-multi` 后缀（`article-multi.md`）。

## Step 4: 后处理

**Input**: Final article written to `docs/{change-name}-{date}/`
**Output**: Position updated + memory saved + user reply

**🔴 CHECKPOINT — 执行后 changes 标记 processed，需 unskip 才可重新纳入。确认文章已写入再执行。**

**4.1** position 更新：

```
python <skill-dir>/scripts/position.py processed <change-dir-1> ... <change-dir-N>
```

**4.2** 记忆写入 — 从本次对话中提取用户偏好，写入 `<skill-dir>/personas/<name>.memory.json`：

```json
{
    "persona": "<selected-persona-name>",
    "sessions": [
        {
            "date": "<YYYY-MM-DD>",
            "changes": ["<dir-1>", "<dir-2>"],
            "title": "<final-title>",
            "skeleton": "<selected-skeleton>",
            "image_types": ["architecture", "flow"],
            "preferences": {
                "title_style": "从对话中归纳的标题偏好",
                "tone_feedback": "用户对语气的调整要求",
                "structure_notes": "用户对结构的偏好"
            }
        }
    ]
}
```

如文件已存在，追加 session 到 `sessions` 列表，合并 `preferences`。

**4.3** 回复用户：

- 最终标题：`{title}`
- 文章路径：`docs/{change-name}-{date}/article.md`
- 覆盖 N 个 changes：`{dir-1}`, `{dir-2}`
- 配图：N 张（architecture / flow / ...）
- 写作人格：`{persona-name}`
- 下次运行不再显示已 processed 的 changes

## 异常与边界处理

| 步骤 | 触发条件 | 一线修复 | 仍失败兜底 |
|------|---------|---------|-----------|
| 1.1 | openspec/changes/ 不存在 | 在 `..` 层级重试 | 提示非 Comet 项目，终止 |
| 1.2 | drawio-skill 目录不存在 | `npx skills add ... -g` 安装 | 告知重启后重试，终止 |
| 1.2 | drawio CLI 不存在 | 提示下载 | 跳过配图，纯文字输出 |
| 1.4 | 无 pending changes | 展示所有 changes + unskip 选项 | 用户无操作则终止 |
| 2.1 | change 缺 proposal.md | 标记 skipped 跳过 | 告知手动检查，继续其余 |
| 2.2 | 标题候选描述不佳 | 用户自定义 | 直接使用 change 名称 |
| 2.3 | 骨架自动匹配不合理 | 用户手动选择 | 默认 SCQA |
| 3.2 | drawio 导出失败 | 重试 1 次（简化描述） | 跳过配图，标注"生成失败" |
| 3.2 | 图片修改达 5 轮 | 强制接受或跳过 | 用户二选一 |
| 3.4 | 用户反馈不明确 | 请求具体修改示例 | 使用当前版本作为最终稿 |
| 3.4 | 调整循环超过 8 轮 | 询问是否接受当前版本或继续 | 用户选择决定 |
| 3.5 | 写入失败 | 检查目录权限 | 输出文件内容到终端，告知手动保存 |
| 4.1 | position.py 执行失败 | 检查 JSON 文件可写 | 告知手动执行，继续回复 |
| 4.2 | memory 写入失败 | 检查 personas 目录权限 | 跳过记忆，继续回复 |
| 全局 | 用户中断 | 输出当前进度提示 | 告知可用 `/spec2md` 重跑 |

## 反例与黑名单

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 在非 Comet 项目中使用 | 无 changes，position.py 报错 | Step 1.1 目录探测自动检查并退出 |
| 2 | 手动编辑 `.wechat-article-position.json` | 状态不一致 | 只用 `position.py` |
| 3 | 跳过 Step 2.4 配图决策 | 缺少关键配图 | 架构/流程变更至少生成一张图 |
| 4 | 单 change 用"时间线复盘"骨架 | 内容撑不起 | 单 change 用 SCQA |
| 5 | 图片反复修改 >5 轮 | 边际收益递减 | 5 轮后强制接受或跳过 |
| 6 | 将草案写入文件后再让用户修改 | 反复写文件浪费操作 | inline 展示全文，收集反馈后再写入 |
| 7 | 修改后不重新展示全文 | 用户不知道改了哪里 | 每次调整后重新展示完整草案 |
| 8 | 未获用户明确确认即写入文件 | 文章未定稿 | 等待用户确认后再写入 |
| 9 | Step 3.4 使用 question 工具 | 交互僵化、打断对话流 | 使用直接对话收集反馈 |
| 10 | 调用 wewrite 或检查 WeChat 配置 | 加载不必要的依赖 | spec2md 仅输出 Markdown，不涉及发布 |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | `status` / `pending` / `processed` / `skipped` / `unskip` / `list` / `reset` |

位置文件：`<project-root>/.wechat-article-position.json`
环境变量：`$env:SPEC2MD_PROJECT_ROOT` — 显式设置项目根路径

## 引用参考

- drawio-skill `SKILL.md` — Step 3.2 委托指令
- Comet `.comet.yaml` — change 元数据格式
- `personas/*.yaml` — 写作人格定义（YAML 格式，含 voice_density / uncertainty_rate / emotional_arc 等参数）
- `personas/*.memory.json` — 用户写作偏好记忆（可选，每次 Step 4.2 写入/更新）
