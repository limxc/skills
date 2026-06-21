---
name: spec2md
description: >-
    Generate Markdown articles from OpenSpec change archives.
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
          note: Comet workflow creates the OpenSpec change archives consumed by this skill
---

# /spec2md — Generate Markdown Articles from OpenSpec Archives

Converts OpenSpec change archives into Markdown articles with diagrams. Four-step workflow: environment check → change selection + writing discussion → material extraction + diagram + writing → post-processing.

**交互层级：Step 1.4 / 2.1 / 2.2 / 2.3 / 2.4 / 2.5 / 3.2 / 3.3 使用 question 工具；Step 3.5（草案展示 → 反馈 → 修改 → 定稿）使用直接对话，不得使用 question 工具。**

**约定：`<skill-dir>` = 本 SKILL.md 所在目录。**

```
Step 1  环境检查（openspec + drawio）+ position 读取
Step 2  Change 选择 + 写作讨论（标题/骨架/配图/人格）
Step 3  素材提取 + drawio 配图 + 框架 + 写作 + 草案交互 → 定稿
Step 4  position 更新 + README 时间线追加 + 回复
```

## Step 1: 环境检查

**Input**: OpenSpec project with `openspec/`
**Output**: Ready env + pending change list

**1.1** openspec 结构检查：

```
Test-Path -LiteralPath "openspec/" -PathType Container
```

存在则继续；不存在提示并在 `..` 层级重试一次。仍不存在则输出 "OpenSpec 项目结构未找到。请在已初始化 OpenSpec（含 openspec/changes/ 目录）的项目中运行本 skill。" 后退出。

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

**1.3** position 状态：

```
python <skill-dir>/scripts/position.py status
```

**1.4** 未处理 changes：

```
python <skill-dir>/scripts/position.py pending
```

- 无 pending changes → 展示所有 changes 清单（含已 processed/skipped 标记），询问是否执行 `unskip` 恢复。用户无操作则退出。
- 有 pending changes → 展示清单，询问：A) 开始写作 B) 仅查看，不继续。

**🔴 CHECKPOINT — 以下步骤确定文章素材范围。选错的 change 需 unskip 才能重选。**

## Step 2: Change 选择 + 写作讨论

**Input**: Pending change list from Step 1
**Output**: Selected changes + confirmed title + skeleton type + image plan + persona

**2.1** 展示 pending change 清单（`position.py pending` 输出的裸目录名列表）：

```
1 | 2026-06-20-migrate-to-drawio-skill
2 | 2026-06-21-refactor-spec2md
```

如需查看 change 详情（类型、描述），读取对应目录下的 `proposal.md` 后展示。

清单展示后自动进入逐项选择，用 question 工具（每次一项）：

选项：
- **写文章** → 传入后续步骤
- **不再显示** → `python <skill-dir>/scripts/position.py skipped <dir>`
- **略过** → 不标记，下次继续显示

pending changes ≥ 5 时，在开始前先问一次「批量操作」：
- **全部写文章** — 自动选中所有，跳过逐项确认
- **全部略过** — 自动跳过所有，退出
- **逐项确认** — 回退到逐项询问

所有 change 处理完毕后，收集选中的 changes 列表传入 Step 2.2。

**2.2** 标题确认 — 根据选中 changes 内容生成 3 个候选标题，用 question 工具：

```
选项：
A) {候选标题 1}
B) {候选标题 2}
C) {候选标题 3}
D) 自定义
```

选择 D 时，提示用户输入自定义标题。

标题确认后，创建输出目录并保存为变量 `$OUTPUT_DIR`：

```
$changeName = "{change-name}"
$date = Get-Date -Format "yyyy-MM-dd"
$OUTPUT_DIR = "spec2md/$date-$changeName"
New-Item -ItemType Directory -Path $OUTPUT_DIR -Force
```

后续所有输出（配图、文章）直接写入 `$OUTPUT_DIR`。

**2.3** 骨架匹配

**Input**: Selected changes list
**Output**: Confirmed skeleton type

按以下规则自动推荐，用 question 工具让用户选择：

| 判定条件 | 推荐骨架 | 适用场景 |
|---------|---------|---------|
| 只选了 1 个 change | SCQA | 单 feature 技术叙事 |
| 选了 ≥2 个 change，且名含时间/日期序列 | 时间线复盘 | 开发历程回顾 |
| change 名含 tweak/refactor/cleanup/优化 关键词 | 对比 | 改造类变更 |
| 混合了 full+tweak/hotfix 类型 | 时间线复盘 | 不同类型变更按时间组织 |
| 其余多 change 情况 | 清单 | 多个不相关 feature |

选项：
A) `{推荐骨架}`（推荐）
B) `{备选骨架}`
C) 自定义

用户选择后，骨架仅决定叙事逻辑和段落组织方式，**不得将骨架名称直接用作章节标题**。写入 article.md 时所有标题须重新拟定为自然标题。

**🔴 CHECKPOINT — 骨架确认后，以下步骤确定配图和写作风格。**

**2.4** 配图计划

**Input**: Selected changes with proposal.md、design.md
**Output**: Confirmed image type list

遍历选中的 changes，检查 `design.md` / `proposal.md`，自动检测所有匹配类型。逐项用 question 工具确认：

| 检测到内容 | 推荐配图 | 说明 |
|-----------|---------|------|
| 架构变更/系统设计 | Architecture diagram | 组件关系、层级结构 |
| 业务流程/工作流 | Flow diagram | 状态流转、决策路径 |
| ML 模型/训练管线 | ML/Deep Learning diagram | 模型结构、数据管线 |
| 类/接口变更 | UML class diagram | 类层次、接口依赖 |
| 协议/交互变更 | Sequence diagram | 调用顺序、消息交换 |
| 数据模型变更 | ER diagram | 实体关系、数据设计 |

每项选项：A) 生成 B) 跳过。

**2.5** 写作人格选择

**Input**: Selected changes content features
**Output**: Selected persona name

读取 `references/persona-selection.md`，按匹配表规则推荐 top 3，用 question 工具展示推荐理由和示例文字，让用户三选一。用户也可选择不使用人格或自定义人格。

## Step 3: 素材提取 + 配图 + 框架 + 写作

**Input**: Selected changes + confirmed title + skeleton + image plan + persona
**Output**: Final article at `$OUTPUT_DIR/article.md`

**3.1** 素材提取 — 遍历每个选中的 change，读取：
- `proposal.md` → Why（动机）/ What（内容）/ Impact（影响范围）
- `design.md` → Context（背景）/ Decisions（决策与权衡）/ Trade-offs
- `tasks.md` → 完成清单（checklist）

**3.2** 配图生成 — 按 Step 2.4 确认的配图计划，对每种类型用以下模板构造提示词，然后加载 drawio-skill 委托生成：

| 配图类型 | drawio 提示词模板 | 所需素材 |
|---------|------------------|---------|
| Architecture | 画一张「{title}」架构图。包含以下组件：{列出 change 涉及的所有模块/服务/组件}。展示它们之间的{调用/依赖/层级}关系。 | design.md 的架构决策、模块清单 |
| Flow | 画一张「{title}」流程图。状态/步骤：{列出关键步骤或状态}。流转路径：{描述分支或决策条件}。 | design.md 的业务流程描述 |
| ML/Deep Learning | 画一张「{title}」{ML/模型结构/训练管线}图。包含：{列出模型组件、数据管线阶段}。数据流向：{从 INPUT 到 OUTPUT 的路径}。 | design.md 的模型/数据管线描述 |
| UML class | 画一张「{title}」UML 类图。类：{列出核心类/接口，每个标注关键字段和方法}。关系：{继承/实现/关联关系}。 | proposal.md/design.md 的接口和类型描述 |
| Sequence | 画一张「{title}」时序图。参与者：{列出交互方}。关键交互：{按时间顺序列出消息/调用序列}。 | design.md 的交互/协议描述 |
| ER | 画一张「{title}」ER 图。实体：{列出数据实体}。关系：{实体间的联系，外键关键字段}。 | design.md/change 的数据模型描述 |

对每种确认的配图，先用当前 change 的素材填充模板，给出一段完整的自然语言描述，再加载 drawio-skill，指定输出到 `$OUTPUT_DIR`：

```
加载 drawio-skill，让它画如下图表，输出到 $OUTPUT_DIR：{填充后的提示词}
```

drawio-skill 会自动产出 `.drawio` 源文件和 `{name}.drawio.png` 到 `$OUTPUT_DIR` 下，显示完整路径。

所有配图生成后，逐张用 question 工具确认（单选）：A) 没问题 B) 修改（≤3 轮）C) 跳过。达 3 轮强制接受或跳过。

**🔴 CHECKPOINT — 配图已确认。**

**3.3** 写作框架选择：

读取 `references/frameworks.md`。根据选中 changes 的内容特征和 Step 2.3 的骨架类型，推荐最匹配的 3 个框架（含示例文字），用 question 工具让用户四选一。选项：A) 框架A（推荐）B) 框架B C) 框架C D) 不使用框架，文章仅按骨架结构和 persona 风格组织。

**3.4** 写作 — 整合以下元素生成文章：

1. Step 3.1 的结构化素材
2. Step 3.2 已确认的配图路径（`$OUTPUT_DIR/{change-name}-{type}.drawio.png`）
3. Step 2.2 的标题
4. Step 3.3 确认的写作框架
5. Step 2.5 选中 persona 的完整 yaml 内容（作为写作风格硬约束注入）
6. `references/writing-guide.md` — 写作规范（反 AI 检测底线规则）
7. `references/exemplar-seeds.yaml` — 范文种子（人类写作结构示范，作为 few-shot 注入）

输出格式为完整 Markdown，配图使用 `![alt]($OUTPUT_DIR/{change-name}-{type}.drawio.png)`。

**写作自检**：每完成约 500 字（或每个 H2）执行 `references/realtime-check.md` 的 5 项检查，当场修复。

**3.5** 草案交互 — 全对话流程，不得使用 question 工具：

**3.5.1 展示草案**：将生成的完整文章 inline 展示（不写入文件）。文章前标注 `--- 草案 ---`，后标注 `--- 草案结束 ---`。

**3.5.2 收集反馈**：使用对话收集用户意见。用户可针对任意段落提出修改要求，也可提全局性修改（如"缩短篇幅"、"换一种语气"）。

**3.5.3 执行修改**：局部意见仅调整对应段落；全局意见一次性应用到全文。首次修改后展示变更段落（标注 `📝` + 前后各 1 句上下文），询问"需要看完整版还是只看改动？" 用户选"完整版"时展示全文，选"只看改动"时继续段落级展示。

**3.5.4 确认定稿**：
- 用户说"确认"、"定稿"、"可以"、"就这样"或明确表示同意 → 进入 3.6
- 用户提出新修改意见 → 回到 3.5.2

**🔴 CHECKPOINT — 定稿确认后将写入文件，后续修改需手动编辑。**

**3.6** 写入最终文件：

```
spec2md/{date}-{change-name}/
├── article.md
├── {change-name}-architecture.drawio.png
├── {change-name}-flow.drawio.png
├── {change-name}-sequence.drawio.png
├── {change-name}-uml.drawio.png
├── {change-name}-er.drawio.png
└── {change-name}-ml.drawio.png
```

仅包含 Step 3.2 实际生成的配图文件（drawio-skill 直接输出到 `$OUTPUT_DIR`）。

`{change-name}` = 选中 changes 中第一个的目录名，`{date}` = 当天日期（YYYY-MM-DD）。

写入 `$OUTPUT_DIR/article.md`，含完整 Markdown 内容和配图引用。

## Step 4: 后处理

**Input**: Final article written to `$OUTPUT_DIR/`
**Output**: Position updated + user reply

**🔴 CHECKPOINT — 执行后 changes 标记 processed，需 unskip 才可重新纳入。确认文章已写入再执行。**

**4.1** position 更新：

```
python <skill-dir>/scripts/position.py processed <change-dir-1> ... <change-dir-N>
```

**4.2** README 需求时间线追加：

```
python <skill-dir>/scripts/append_readme.py <project-root> "<final-title>" <article-dir>
```

**4.3** 回复用户（汇总）：

- 最终标题：`{title}`
- 文章路径：`$OUTPUT_DIR/article.md`
- 覆盖 N 个 changes：`{dir-1}`, `{dir-2}`
- 配图：N 张（architecture / flow / ...）
- 写作框架：`{framework-name}`
- 写作人格：`{persona-name}`
- ✅ position 已更新
- ✅ 需求时间线已追加
- 下次运行不再显示已 processed 的 changes

## 异常与边界处理

| 步骤 | 触发条件 | 一线修复 | 仍失败兜底 |
|------|---------|---------|-----------|
| 1.1 | openspec/changes/ 不存在 | 在 `..` 层级重试 | 提示非 OpenSpec 项目，终止 |
| 1.2 | drawio-skill 目录不存在 | `npx skills add ... -g` 安装 | 告知重启后重试，终止 |
| 1.2 | drawio CLI 不存在 | 提示下载 | 跳过配图，纯文字输出 |
| 1.4 | 无 pending changes | 展示所有 changes + unskip 选项 | 用户无操作则终止 |
| 2.1 | change 缺 proposal.md | 标记 skipped 跳过 | 告知手动检查，继续其余 |
| 2.2 | 标题候选描述不佳 | 用户自定义 | 直接使用 change 名称 |
| 2.3 | 推荐骨架不满足 | 用户自定义 | 默认 SCQA |
| 3.2 | drawio 导出失败 | 重试 1 次（简化描述） | 跳过配图，标注"生成失败" |
| 3.2 | drawio-skill 加载失败 | 重新加载 drawio-skill | 跳过配图，纯文字输出 |
| 3.2 | 图片修改达 3 轮 | 强制接受或跳过 | 用户二选一 |
| 3.5 | 用户反馈不明确 | 请求具体修改示例 | 使用当前版本作为最终稿 |
| 3.5 | 调整循环超过 5 轮 | 询问是否接受当前版本或继续 | 用户选择决定 |
| 3.6 | 写入失败 | 检查目录权限 | 输出文件内容到终端，告知手动保存 |
| 4.1 | position.py 执行失败 | 检查 JSON 文件可写 | 告知手动执行，继续回复 |
| 4.2 | append_readme.py 执行失败 | 检查 README.md 是否存在及可写 | 告知用户手动追加，继续回复 |
| 全局 | 用户中断 | 输出当前进度提示 | 告知可用 `/spec2md` 重跑 |

## 反例与黑名单

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 在非 OpenSpec 项目中使用 | 无 changes，position.py 报错 | Step 1.1 目录探测自动检查并退出 |
| 2 | 手动编辑 `.spec2md-position.json` | 状态不一致 | 只用 `position.py` |
| 3 | 跳过 Step 2.4 配图决策 | 缺少关键配图 | 架构/流程变更至少生成一张图 |
| 4 | 用户选了不合适的骨架 | 内容撑不起 | 在 question 选项中提供推荐理由辅助判断 |
| 5 | 图片反复修改 >5 轮 | 边际收益递减 | 5 轮后强制接受或跳过 |
| 6 | 将草案写入文件后再让用户修改 | 反复写文件浪费操作 | inline 展示全文，收集反馈后再写入 |
| 7 | 修改后不重新展示全文 | 用户不知道改了哪里 | 每次调整后重新展示完整草案 |
| 8 | 未获用户明确确认即写入文件 | 文章未定稿 | 等待用户确认后再写入 |
| 9 | Step 3.5 使用 question 工具 | 交互僵化、打断对话流 | 使用直接对话收集反馈 |
| 10 | 调用 wewrite 或检查 WeChat 配置 | 加载不必要的依赖 | spec2md 仅输出 Markdown，不涉及发布 |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | `status` / `pending` / `processed` / `skipped` / `unskip` / `list` / `reset` |
| `scripts/append_readme.py` | 向 README.md 需求时间线追加文章链接 |

位置文件：`<project-root>/.spec2md-position.json`
环境变量：`$env:SPEC2MD_PROJECT_ROOT` — 显式设置项目根路径

## 引用参考

- drawio-skill `SKILL.md` — Step 3.2 委托指令
- `personas/*.yaml` — 写作人格定义（YAML 格式，含 voice_density / uncertainty_rate / emotional_arc 等参数）
- `references/persona-selection.md` — 人格选择指南与匹配表
- `references/writing-guide.md` — 反 AI 检测写作规范
- `references/realtime-check.md` — 分段自检规则
- `references/exemplar-seeds.yaml` — 范文种子
- `references/frameworks.md` — 写作框架库
