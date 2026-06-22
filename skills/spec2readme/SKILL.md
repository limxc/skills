---
name: spec2readme
description: >-
    Generate Markdown documentation (READMEs, technical docs, changelogs)
    from OpenSpec change archives using Mermaid diagrams for illustrations.
    Use this skill whenever the user says /spec2readme, asks for README/技术文档/
    文档化/changelog/变更总结, or wants to write documentation from completed
    OpenSpec changes, generate a README from OpenSpec artifacts, or summarize
    development work into a readable Markdown document. Always delegate diagram
    generation to the creating-mermaid-diagrams skill.
metadata:
    version: 1.0.0
    created: 2026-06-21
    dependencies:
        - url: https://github.com/Agents365-ai/mermaid-skill
          name: creating-mermaid-diagrams
          type: skill
          note: Mermaid diagram generation (installed as creating-mermaid-diagrams from the mermaid-skill repo)
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

运行：
```
python <skill-dir>/scripts/check_openspec.py --try-parent
```

- exit 0 → 继续。
- exit 1 → 输出 "OpenSpec 项目结构未找到。请在已初始化 OpenSpec（含 openspec/changes/ 目录）的项目中运行本 skill。" 后退出。

**1.2** 依赖环境检查（提前验证，避免进入交互后因缺少依赖而失败）：

运行：
```
python <skill-dir>/scripts/env_check.py
```

脚本会检查并自动修复：
- `creating-mermaid-diagrams` skill 是否已安装
- `mmdc` CLI 是否可用
- Puppeteer / Chrome headless shell 是否已安装（缺失则自动安装）

根据返回状态处理：
- `ready: true` → 继续。
- `creating-mermaid-diagrams` 缺失 → 安装后重跑：
  ```
  npx skills add https://github.com/Agents365-ai/mermaid-skill
  ```
- `mmdc` 缺失 → 安装后重跑：
  ```
  npm install -g @mermaid-js/mermaid-cli
  ```

**1.3** Chrome 运行时检查（mmdc 依赖 puppeteer/Chrome）：

由 `env_check.py` 自动检测并安装，无需额外手动操作。若自动安装失败，会提示跳过配图或使用纯文字输出。

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

## Step 3: 标题 + 输出文件名确认

**Input**: Selected changes list
**Output**: Confirmed title + output file path

**3.1** 根据选中 changes 生成 3 个候选标题，用 question 工具：
- A) {候选标题 1}
- B) {候选标题 2}
- C) {候选标题 3}
- D) 自定义

**3.2** 生成输出文件名和临时目录：

运行：
```
python <skill-dir>/scripts/prepare_output.py <change-name>
```

该脚本会：
- 定位 `openspec/changes/<change-name>` 或 `openspec/changes/archive/<change-name>`
- 从 `.openspec.yaml` 读取 `created:` 日期
- 创建 `spec2readme/` 和临时 `spec2readme/<date>-<change-name>-mmd/` 目录
- 输出 JSON：
  ```json
  {
    "changeName": "<change-name>",
    "changeDir": "<absolute-path-to-change>",
    "projectRoot": "<absolute-path-to-project-root>",
    "date": "<created-date>",
    "outputFile": "spec2readme/<date>-<change-name>.md",
    "mmdDir": "spec2readme/<date>-<change-name>-mmd"
  }
  ```

读取脚本输出后设置变量 `$OUTPUT_FILE` 和 `$MMD_DIR`。

如果 `<change-name>` 对应目录不存在，脚本会输出错误并退出。

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

**4.2** 确定配图类型

把 Step 4.1 提取到的素材（每个 change 的 `proposal.md` + `design.md` 摘要）加载给 `creating-mermaid-diagrams` skill，让它根据自身的 Diagram Types 表推荐最适合的 1-2 种配图类型。

推荐 prompt 模板：

```
请根据以下 OpenSpec change 的内容，从 creating-mermaid-diagrams 支持的图表类型中，
推荐最适合的 1-2 种配图类型：

可用的类型及适用场景：
- flowchart：processes, pipelines, decisions
- sequenceDiagram：API calls, message passing
- classDiagram：OOP models, data structures
- erDiagram：database schemas
- stateDiagram-v2：state machines, lifecycle
- gantt：project timelines
- mindmap：topic breakdowns
- C4Context：high-level architecture

只返回推荐的类型列表，例如 ["flowchart"] 或 ["sequenceDiagram", "erDiagram"]。
如果没有合适的配图类型，返回 []。

change 内容摘要如下：
{change_material_summary}
```

得到推荐列表后：
- 列表为空 → 询问用户是否手动指定配图类型，或跳过配图直接写作。
- 列表非空 → 逐项用 question 确认：A) 生成 B) 跳过。

如果 `creating-mermaid-diagrams` skill 加载失败 → 重新加载一次。仍失败 → 跳过所有配图，仅生成纯文字文档，在 Step 5.2 告知用户配图缺失原因。

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

写入前检查文件是否已存在：
```
python -c "import sys; from pathlib import Path; sys.exit(0 if Path('$OUTPUT_FILE').exists() else 1)"
```
- exit 0 → 文件已存在，用 question 确认覆盖或加 `-{n}` 后缀另存。
- exit 1 → 文件不存在，直接写入。
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

用户说出"没问题"/"可以"/"定稿"/"就这样"等明确同意表达后，才进入 Step 6 执行 position 更新和 README 追加。在此之前只修改文档内容，不标记 change 为 processed。

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

这会在 `README.md` 的 `## 项目文档` 节追加一条带日期的链接（日期取自 change 目录 `.openspec.yaml` 的 `created:` 字段）。无此节则自动创建。
多 change 场景：只传入第一个 change 目录名，日期取自该 change 的 `created:` 字段。

**6.3** 清理临时 `.mmd` 文件（不影响结果，失败可忽略）：

```
python <skill-dir>/scripts/cleanup_mmd.py $MMD_DIR
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
| 1.2 | mmdc 或 creating-mermaid-diagrams 未安装 | 对应 `npm install` / `npx skills add` | 终止 |
| 1.3 | puppeteer Chrome 未安装 | `npx puppeteer browsers install chrome-headless-shell` | 自动安装，不终止 |
| 1.4 | 无 pending changes | unskip 选项 | 终止 |
| 3.2 | change 目录缺 `.openspec.yaml` 或 `created:` 字段 | 检查 change 目录结构 | 终止（change 结构不完整） |
| 2 | 缺 proposal.md | 提示用户该 change 缺少关键素材，询问是否继续或跳过 | 用户选择跳过则继续下一个 change |
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
| 3 | 多 change 场景只配一种图 / 忽略 creating-mermaid-diagrams 的推荐 | 数据变更没有可视化，读者看不懂模型变化 | 遵循 Step 4.2 推荐结果，逐项确认生成或跳过，不要漏掉推荐类型，也不要擅自跳过 |
| 4 | 未等 creating-mermaid-diagrams 完成就清理 `$MMD_DIR` | 配图源码丢失，文档里 mermaid 块为空 | Step 6.3 清理必须在配图源码嵌入文档之后执行 |
| 5 | 重复写入同一个 `$OUTPUT_FILE` 且不警告 | 覆盖历史文档，用户无法追溯 | 写入前用 python 检查文件是否存在，存在则加 `-{n}` 后缀或用 question 确认覆盖 |
| 6 | 文档堆砌 tasks.md 逐条列表 | 读者看到的是任务清单而不是技术叙事，可读性差 | 遵循 Step 5.1 原则：Why 先行 + What 用列表提炼 + Impact 单独标注 |
| 7 | 配图堆在文档开头或末尾 | 图文脱节，读者需要来回翻 | 遵循 Step 5.1 原则：配图紧跟相关段落，一处内容一张图 |
| 8 | 用户说"修改"时用 question 工具 | question 弹窗不适合多轮修改对话，用户无法自然表达修改意图 | Step 5.2 明确规定了用直接对话，不得使用 question 工具 |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | 位置追踪（status/pending/processed/skipped/unskip/list/reset） |
| `scripts/append_readme.py` | 向 README.md 项目文档节追加链接 |
| `scripts/check_openspec.py` | 检查当前目录是否为 OpenSpec 项目 |
| `scripts/env_check.py` | 依赖环境检查（creating-mermaid-diagrams / mmdc / Chrome） |
| `scripts/prepare_output.py` | 生成输出文件路径和临时目录 |
| `scripts/get_change_date.py` | 从 change 目录的 `.openspec.yaml` 读取 `created:` 日期 |
| `scripts/cleanup_mmd.py` | 清理临时 `.mmd` 目录 |
| `scripts/utils.py` | `find_project_root()` / `resolve_change_path()` 共享工具函数 |

位置文件：`<project-root>/spec2readme/.spec2readme-position.json`
