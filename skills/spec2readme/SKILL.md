---
name: spec2readme
description: >-
    Generate Markdown documentation (READMEs, technical docs, changelogs)
    from OpenSpec change archives using Mermaid diagrams for illustrations.
    Use this skill whenever the user says /spec2readme, wants to write documentation
    from completed changes, generate a README from OpenSpec artifacts, or summarize
    development work into a readable document. Delegate to creating-mermaid-diagrams
    skill for architecture, flow, sequence, and other diagrams.
metadata:
    version: 1.0.0
    created: 2026-06-21
    dependencies:
        - url: https://github.com/Agents365-ai/mermaid-skill
          name: creating-mermaid-diagrams
          type: skill
          note: Mermaid diagram source generation
---

# /spec2readme — Generate Markdown Docs from OpenSpec Archives

Converts OpenSpec change archives into Markdown documentation with Mermaid diagrams. Output goes to `spec2readme/{date}-{changeName}.md` and auto-updates the project's `README.md`.

**约定：`<skill-dir>` = 本 SKILL.md 所在目录。**
**交互层级：Step 1.4 / 2 / 3 / 4.1 / 4.2 使用 question 工具；Step 5.2 使用直接对话，不得使用 question 工具。**

```
Step 1  环境检查（openspec + mmdc + creating-mermaid-diagrams）+ position 读取
Step 2  Change 选择
Step 3  标题 + 输出文件名确认
Step 4  素材提取 + mermaid 配图
Step 5  写作 → 写入文件 → 确认定稿
Step 6  position 更新 + README 追加 + 回复
```

## Step 1: 环境检查

**Input**: OpenSpec project with `openspec/`
**Output**: Ready env + pending change list

**1.1** openspec 结构检查：

```
Test-Path -LiteralPath "openspec/" -PathType Container
```

存在 → 继续。
不存在 → 提示并在 `..` 层级重试一次。
仍不存在 → 输出 "OpenSpec 项目结构未找到。请在已初始化 OpenSpec（含 openspec/changes/ 目录）的项目中运行本 skill。" 后退出。

**1.2** mmdc 检查（creating-mermaid-diagrams 语法校验所需）：

```
Get-Command mmdc -ErrorAction SilentlyContinue
```

不存在 → 提示安装并终止：
```
npm install -g @mermaid-js/mermaid-cli
```
安装后重新运行本 skill。

**1.3** creating-mermaid-diagrams skill 检查：

```
npx skills ls -g 2>&1 | Select-String -Pattern "creating-mermaid-diagrams"
```

不存在 → 提示安装并终止：
```
npx skills add https://github.com/Agents365-ai/mermaid-skill
```
安装后重新运行本 skill。

**1.4** position 状态：

```
python <skill-dir>/scripts/position.py status
python <skill-dir>/scripts/position.py pending
```

- 有 pending changes → 展示清单。
- 无 pending changes → 展示所有skipped标记的changes，询问是否 `unskip` 恢复。
  - 用户确认 unskip → 恢复后继续。
  - 用户无操作或拒绝 → 退出。

## Step 2: Change 选择

**Input**: Pending change list
**Output**: Selected changes list

展示 pending change 清单，逐项用 question 确认：
- **写文档** → 选中
- **不再显示** → `python <skill-dir>/scripts/position.py skipped <dir>`
- **略过** → 不标记，下次继续显示

pending changes ≥ 5 时先问批量操作：全部写 / 全部略过 / 逐项确认。

如果某个 change 缺少 `proposal.md` → 标记该 change 为 skipped，记录到日志，继续下一个。不要因为一个 change 缺失就中断整个流程。

## Step 3: 标题 + 输出文件名确认

**Input**: Selected changes list
**Output**: Confirmed title + output file path

**3.1** 根据选中 changes 生成 3 个候选标题，用 question 工具：
- A) {候选标题 1}
- B) {候选标题 2}
- C) {候选标题 3}
- D) 自定义

**3.2** 生成输出文件名和临时目录：

```
$changeName = "{first-change-dir-name}"
$date = (git log --follow --diff-filter=A --format=%aI -1 -- "openspec/changes/$changeName" | ForEach-Object { if ($_) { ($_ -split 'T')[0] } })
$projectRoot = (Get-Item ".").FullName
$OUTPUT_FILE = "spec2readme/$date-$changeName.md"
$MMD_DIR = "$projectRoot/spec2readme/$date-$changeName-mmd"
New-Item -ItemType Directory -Path "spec2readme" -Force
New-Item -ItemType Directory -Path $MMD_DIR -Force
```

## Step 4: 素材提取 + mermaid 配图

**Input**: Selected changes + title
**Output**: Material summary + mermaid diagram source code

**4.1** 强制素材提取与讨论（多轮对话，直至用户确认）

遍历每个选中的 change，读取：
- `proposal.md` → Why / What / Impact
- `design.md` → Context / Decisions / Trade-offs
- `tasks.md` → 完成清单

提取后展示结构化摘要（每个 change 1-2 句核心结论、涉及模块、关键决策、配图素材是否充分）。

**必须**用 question 工具询问用户：
- A) 素材足够，继续生成配图
- B) 需要补充素材（请在下一步输入补充内容）

选择 B 时，使用对话收集用户的补充素材，合并到摘要中，然后**再次用 question 工具确认**是否继续。重复此循环直至用户确认素材足够或选择直接跳过配图进入写作。

**4.2** 自动检测适合的配图类型：

| 检测到内容 | 推荐 Mermaid 类型 |
|-----------|------------------|
| 架构变更/系统设计 | flowchart |
| 业务流程/工作流 | flowchart |
| ML 模型/训练管线 | flowchart |
| 类/接口变更 | classDiagram |
| 协议/交互变更 | sequenceDiagram |
| 数据模型变更 | erDiagram |
| 状态机/生命周期 | stateDiagram-v2 |

逐项用 question 确认：A) 生成 B) 跳过。

如果 creating-mermaid-diagrams skill 加载失败 → 重新加载一次。仍失败 → 跳过所有配图，仅生成纯文字文档，在 Step 5.2 告知用户配图缺失原因。

**4.3** 加载 creating-mermaid-diagrams skill，用以下模板构造提示词生成配图源码：

| 配图类型 | 参考提示词 |
|---------|-----------|
| 架构/系统（flowchart） | "画一个{系统名}架构图,包含 {组件1}/{组件2}/{组件3}...展示它们之间的{调用/依赖}关系"；完整示例：微服务电商架构图（Mobile/Web → API 网关 → User/Order/Product/Payment 服务 → DB + Redis） |
| 时序/协议（sequenceDiagram） | "画一个{场景名}的时序图:{参与方A}把{请求}发给{参与方B},{参与方B}调{服务C},{服务C}查{数据库D}、{操作},然后把{结果}沿路径返回。同时画出{错误分支}"；完整示例：JWT 登录时序图（Client → Gateway → Auth Service → User DB → 返回 JWT） |
| 数据模型（erDiagram） | "画一个{系统名}的 ER 图,包含 {实体1}/{实体2}/{实体3} 等实体,标注它们之间的关系和外键" |
| 状态机（stateDiagram-v2） | "画一个{对象名}的生命周期状态机:初始态→{状态A}→{状态B}→{状态C}→终态,标注转移条件"；完整示例：订单生命周期（Pending→Confirmed→Shipped→Delivered→[*]） |
| 类/领域（classDiagram） | "画一个{领域名}的类图,包含 {类1}/{接口2}/{抽象类3}...,标注它们的继承和关联关系" |
| C4 高层架构 | "画一个{系统名}的 C4 Context 图:用户→{系统}→{外部 API}" |
| 甘特图/时间线 | "画一个{项目名}的甘特图:规划期→开发期→测试期" |

在生成配图时，指定输出目录为 `$MMD_DIR`，让 creating-mermaid-diagrams skill 将 `.mmd` 文件写在此目录下。如果该 skill 的输出报告返回了文件路径，则从中读取 `.mmd` 内容；否则直接从 `$MMD_DIR` 下读取生成的 `.mmd` 文件。

以 ` ```mermaid ` 代码块形式将内容嵌入后续 Markdown 文档。配图的修改在 Step 5.2 随文档一起确认。

## Step 5: 写作 → 写入文件 → 确认定稿

**Input**: Material summary + diagrams + title
**Output**: Final document at `$OUTPUT_FILE`

**5.1** 整合以下元素生成完整文档并直接写入 `$OUTPUT_FILE`：
1. Step 4.1 的结构化素材
2. Step 4.3 生成的 mermaid 源码，以 ` ```mermaid ` 代码块嵌入对应段落之后
3. Step 3.1 的标题

文档结构由内容自然决定，但应遵循以下原则：
- **按时间/逻辑组织**：每个 change 独立成节（H2），按发生时间或逻辑依赖排列。文档不是 change 的简单堆砌——每个节应讲清楚"为什么做这事"和"带来了什么变化"。
- **Why 先行**：每个 change 的动机作为节内引言，读者需要先理解背景才能理解具体变更。
- **What 用列表**：变更内容用列表或表格呈现，保持简洁。不需要逐条罗列 tasks.md，而是提炼出有意义的变更点。
- **Impact 单独标注**：影响范围单独标注，让读者一目了然哪些文件或能力被改动。
- **关键决策用引用块**：用 `> ` 突出架构决策和权衡，与普通描述区分开。
- **配图紧跟正文**：配图嵌入在相关段落之后，而不是堆在文档开头或末尾——图文脱节会大幅降低可读性。
- **语言风格**：技术文档风格，清晰简洁，避免营销语气。不写"我们很高兴地宣布"这类废话。

**5.2** 写入后展示绝对路径供用户查看：

```
文档已生成：{Resolve-Path $OUTPUT_FILE}
```

用户阅读后可提出修改请求（直接对话，不得使用 question）。修改后重新展示路径。

## Step 6: 后处理

**Input**: Final document at `$OUTPUT_FILE`
**Output**: Position updated + README.md 项目文档 section appended

**6.1** position 更新：

```
python <skill-dir>/scripts/position.py processed <change-dir-1> ... <change-dir-N>
```

**6.2** 项目 README.md 追加：

```
python <skill-dir>/scripts/append_readme.py <project-root> "<final-title>" $OUTPUT_FILE <change-dir-1>
```

这会在 `README.md` 的 `## 项目文档` 节追加一条带日期的链接（取自 change 目录的文件夹创建时间）。无此节则自动创建。
多 change 场景：只传入第一个 change 目录名，日期取自该文件夹创建时间。

**6.3** 清理临时 `.mmd` 文件（不影响结果，失败可忽略）：

```
Remove-Item -Recurse -Force $MMD_DIR -ErrorAction SilentlyContinue
```

如果 `position.py processed` 失败（JSON 文件不可写）→ 输出失败原因，告知用户手动执行：
```
python <skill-dir>/scripts/position.py processed <dir-1> ... <dir-N>
```

如果 `append_readme.py` 失败（README.md 不可写或不存在）→ 输出失败原因，告知用户手动追加链接到 README.md 的 `## 项目文档` 节。

**6.4** 回复用户（汇总）：
- 标题：`{title}`
- 文档路径：`$OUTPUT_FILE`
- 覆盖 N 个 changes：`{dir-1}`, `{dir-2}`
- Mermaid 图表：N 个（flowchart / sequence / ...）
- ✅ position 已更新（或 ❌ 需手动执行）
- ✅ README.md 项目文档已追加（或 ❌ 需手动追加）

## 异常与边界处理

| 步骤 | 触发条件 | 一线修复 | 兜底 |
|------|---------|---------|------|
| 1.1 | openspec/ 不存在 | `..` 层级重试 | 提示终止 |
| 1.2 | mmdc 未安装 | `npm install -g @mermaid-js/mermaid-cli` | 终止 |
| 1.3 | creating-mermaid-diagrams 不在 `npx skills ls -g` 输出中 | `npx skills add` 安装 | 终止 |
| 1.4 | 无 pending changes | unskip 选项 | 终止 |
| 2 | 缺 proposal.md | 标记 skipped | 跳过继续 |
| 4.3 | creating-mermaid-diagrams 加载失败 | 重新加载 | 跳过配图 |
| 4.3 | mmdc 语法校验失败 | 根据错误信息修正 `.mmd` 后重试 | 重试仍失败则跳过该配图 |
| 5.2 | 写入失败 | 检查目录权限 | 输出内容到终端 |
| 6.1 | position.py 失败 | 检查 JSON 可写 | 告知手动执行 |
| 6.2 | append_readme.py 失败 | 检查 README.md 可写 | 告知手动追加 |

## 反例黑名单

以下行为在执行本 skill 时禁止出现，每条都对应真实踩过的坑或可预见的故障模式。

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | Step 4.1 跳过用户确认直接生成配图 | 素材方向不对，后续配图和文档全部重做，浪费 2-3 轮 | 循环问用户，直到收到"素材足够"或"跳过配图"的明确确认 |
| 2 | Step 5.2 未经用户定稿确认就执行 position 更新和 README 追加 | 用户还没看完文档，position 已标记 processed，change 再也无法选中文档 | 用户必须说出"没问题/可以/定稿"等价关键词才进入 Step 6 |
| 3 | 多 change 场景只配一种图（如只配 flowchart 不配 erDiagram） | 数据变更没有可视化，读者看不懂模型变化 | 按 Step 4.2 检测表逐项判断配图类型，每个 type 单独生成 |
| 4 | 未等 creating-mermaid-diagrams 完成就清理 `$MMD_DIR` | 配图源码丢失，文档里 mermaid 块为空 | Step 6.3 清理必须在配图源码嵌入文档之后执行 |
| 5 | 重复写入同一个 `$OUTPUT_FILE` 且不警告 | 覆盖历史文档，用户无法追溯 | 写入前检查 `Test-Path $OUTPUT_FILE`，存在则加 `-{n}` 后缀或用 question 确认覆盖 |
| 6 | 文档堆砌 tasks.md 逐条列表 | 读者看到的是任务清单而不是技术叙事，可读性差 | 遵循 Step 5.1 原则：Why 先行 + What 用列表提炼 + Impact 单独标注 |
| 7 | 配图堆在文档开头或末尾 | 图文脱节，读者需要来回翻 | 遵循 Step 5.1 原则：配图紧跟相关段落，一处内容一张图 |
| 8 | 用户说"修改"时用 question 工具 | question 弹窗不适合多轮修改对话，用户无法自然表达修改意图 | Step 5.2 明确规定了用直接对话，不得使用 question 工具 |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | 位置追踪（status/pending/processed/skipped/unskip/list/reset） |
| `scripts/append_readme.py` | 向 README.md 项目文档节追加链接 |

位置文件：`<project-root>/spec2readme/.spec2readme-position.json`
