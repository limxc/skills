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
          note: Mermaid diagram generation via mmdc CLI (local export)
---

# /spec2readme — Generate Markdown Docs from OpenSpec Archives

Converts OpenSpec change archives into Markdown documentation with Mermaid diagrams. Output goes to `spec2readme/{date}-{changeName}.md` and auto-updates the project's `README.md`.

**约定：`<skill-dir>` = 本 SKILL.md 所在目录。**
**交互层级：Step 1.2 / 2 / 3 / 4.1 / 4.2 使用 question 工具；Step 5（草案展示 → 反馈 → 修改 → 定稿）使用直接对话，不得使用 question 工具。**

```
Step 1  环境检查（openspec + mermaid deps）+ position 读取
Step 2  Change 选择
Step 3  标题 + 输出文件名确认
Step 4  素材提取 + mermaid 配图
Step 5  写作 + 草案交互 → 定稿
Step 6  position 更新 + README 追加 + 回复
```

## Step 1: 环境检查

**Input**: OpenSpec project with `openspec/`
**Output**: Ready env + pending change list

**1.1** openspec 结构检查：

```
Test-Path -LiteralPath "openspec/" -PathType Container
```

存在则继续；不存在提示并在 `..` 层级重试一次。仍不存在则输出 "OpenSpec 项目结构未找到。请在已初始化 OpenSpec（含 openspec/changes/ 目录）的项目中运行本 skill。" 后退出。

**1.2** mermaid 依赖检查：

优先使用本地 mmdc，不可用时回退到 Kroki API：

```
$hasMmdc = Get-Command mmdc -ErrorAction SilentlyContinue
$hasCurl = Get-Command curl -ErrorAction SilentlyContinue
$hasChrome = Test-Path (Join-Path $env:USERPROFILE ".cache\puppeteer\chrome-headless-shell\*")
```

记录结果供 Step 4.3 使用。

最终 mmdc 和 Kroki 都不可用时终止，提示安装：
```
npm install -g @mermaid-js/mermaid-cli
npx puppeteer browsers install chrome-headless-shell
```

**1.3** creating-mermaid-diagrams skill 检查（技能 ID：`creating-mermaid-diagrams`）：

```
npx skills ls -g 2>&1 | Select-String -Pattern "creating-mermaid-diagrams"
```

不存在输出中 → 提示安装并终止：
```
npx skills add https://github.com/Agents365-ai/mermaid-skill
```
安装后重新运行本 skill。

**1.4** position 状态：

```
python <skill-dir>/scripts/position.py status
python <skill-dir>/scripts/position.py pending
```

- 无 pending changes → 展示所有 changes（含 processed/skipped 标记），询问是否 `unskip` 恢复。用户无操作则退出。
- 有 pending changes → 展示清单，询问：A) 开始文档 B) 仅查看。

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

```
$changeName = "{first-change-dir-name}"
$date = Get-Date -Format "yyyy-MM-dd"
$OUTPUT_FILE = "spec2readme/$date-$changeName.md"
$TMP_DIR = "spec2readme/$date-$changeName-tmp"
New-Item -ItemType Directory -Path "spec2readme" -Force
New-Item -ItemType Directory -Path $TMP_DIR -Force
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

**🔴 CHECKPOINT — 未经用户确认素材范围，不得进入 Step 4.2。**

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

**4.3** 加载 creating-mermaid-diagrams skill 生成配图。构造提示词时参考以下 mermaid-skill 官方示例（根据 change 内容调整）：

| 配图类型 | 参考提示词（来自 mermaid-skill 官方 README） |
|---------|--------------|
| 架构/系统（flowchart） | "画一个{系统名}架构图,包含 {组件1}/{组件2}/{组件3}...展示它们之间的{调用/依赖}关系"；完整示例：微服务电商架构图（Mobile/Web → API 网关 → User/Order/Product/Payment 服务 → DB + Redis） |
| 时序/协议（sequenceDiagram） | "画一个{场景名}的时序图:{参与方A}把{请求}发给{参与方B},{参与方B}调{服务C},{服务C}查{数据库D}、{操作},然后把{结果}沿路径返回。同时画出{错误分支}"；完整示例：JWT 登录时序图（Client → Gateway → Auth Service → User DB → 返回 JWT） |
| 数据模型（erDiagram） | "画一个{系统名}的 ER 图,包含 {实体1}/{实体2}/{实体3} 等实体,标注它们之间的关系和外键" |
| 状态机（stateDiagram-v2） | "画一个{对象名}的生命周期状态机:初始态→{状态A}→{状态B}→{状态C}→终态,标注转移条件"；完整示例：订单生命周期（Pending→Confirmed→Shipped→Delivered→[*]） |
| 类/领域（classDiagram） | "画一个{领域名}的类图,包含 {类1}/{接口2}/{抽象类3}...,标注它们的继承和关联关系" |
| C4 高层架构 | "画一个{系统名}的 C4 Context 图:用户→{系统}→{外部 API}" |
| 甘特图/时间线 | "画一个{项目名}的甘特图:规划期→开发期→测试期" |

creating-mermaid-diagrams skill 运行完成后，从它的输出报告获取生成的 `.mmd` 和 `.svg` 文件路径，将它们移到 `$TMP_DIR`。对每张 SVG，向用户展示完整绝对路径供预览：
```
已生成配图：{Resolve-Path "$TMP_DIR\{diagram-name}.svg"}
```

读取 `.mmd` 文件内容，以 ` ```mermaid ` 代码块形式嵌入后续 Markdown 文档。所有配图生成后逐张展示确认（≤3 轮修改）。临时文件（`.mmd`、`.svg`）在 Step 6 定稿后统一清理。

## Step 5: 写作 + 草案交互

**Input**: Material summary + diagrams + title
**Output**: Final document at `$OUTPUT_FILE`

**5.1** 整合以下元素生成草案：
1. Step 4.1 的结构化素材
2. Step 4.3 生成的 mermaid 源码，以 ` ```mermaid ` 代码块直接嵌入文档中对应的段落之后
3. Step 3.1 的标题

撰写规范：
- 每个 change 独立成节（H2），按时间/逻辑顺序排列
- 每个 change 的 Why（动机）作为节内引言
- What（变更内容）用列表或表格呈现
- Impact（影响范围）单独标注
- 关键决策与权衡用引用块 `> ` 突出
- 配图嵌入在相关段落之后
- 语言风格：技术文档，清晰简洁

**5.2** 草案交互 — 全对话流程，不得使用 question：

**5.2.1 展示草案**：inline 展示完整文档，标注 `--- 草案 ---` / `--- 草案结束 ---`。

**5.2.2-5.2.3** 收集反馈 → 执行修改 → 展示改动。

**5.2.4 确认定稿**：用户明确同意后写入 `$OUTPUT_FILE`。

## Step 6: 后处理

**Input**: Final document at `$OUTPUT_FILE`
**Output**: Position updated + README.md 项目文档 section appended

**6.1** position 更新：

```
python <skill-dir>/scripts/position.py processed <change-dir-1> ... <change-dir-N>
```

**6.2** 项目 README.md 追加：

```
python <skill-dir>/scripts/append_readme.py <project-root> "<final-title>" $OUTPUT_FILE
```

这会在 `README.md` 的 `## 项目文档` 节追加一条链接。无此节则自动创建。

**6.3** 清理临时文件 — 删除 Step 4.3 产生的 `.mmd` 和 `.svg` 临时文件：

```
if (Test-Path "spec2readme/$date-$changeName-tmp") { Remove-Item -Recurse -Force "spec2readme/$date-$changeName-tmp" }
```

**6.4** 回复用户（汇总）：
- 标题：`{title}`
- 文档路径：`$OUTPUT_FILE`
- 覆盖 N 个 changes：`{dir-1}`, `{dir-2}`
- 配图：N 张（flowchart / sequence / ...）
- ✅ position 已更新
- ✅ README.md 项目文档已追加
- ✅ 临时文件已清理

## 异常与边界处理

| 步骤 | 触发条件 | 一线修复 | 兜底 |
|------|---------|---------|------|
| 1.1 | openspec/changes/ 不存在 | `..` 层级重试 | 提示终止 |
| 1.2 | mmdc + Kroki 均不可用 | 提示安装 mmdc + Chrome | 终止 |
| 1.3 | creating-mermaid-diagrams 不在 `npx skills ls -g` 输出中 | `npx skills add` 安装 | 终止 |
| 1.4 | 无 pending changes | unskip 选项 | 终止 |
| 2 | 缺 proposal.md | 标记 skipped | 跳过继续 |
| 4.3 | mmdc 导出失败 | 回退到 Kroki 导出 SVG | Kroki 也失败则跳过配图 |
| 4.3 | 修改达 3 轮 | 强制接受或跳过 | 二选一 |
| 5.2 | 用户反馈不明确 | 请求具体示例 | 当前版定稿 |
| 5.2 | 调整超 5 轮 | 询问继续或接受 | 用户决定 |
| 5.2 | 写入失败 | 检查权限 | 终端输出内容 |
| 6.1 | position.py 失败 | 检查 JSON 可写 | 告知手动执行 |
| 6.2 | append_readme.py 失败 | 检查 README.md 可写 | 告知手动追加 |

## 反例

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 手动编辑 `.spec2readme-position.json` | 状态不一致 | 只用 `position.py` |
| 2 | 跳过配图确认 | 缺少关键配图 | 架构/流程变更至少一张图 |
| 3 | 将草案写入文件后再修改 | 反复 I/O | inline 展示，确认后再写 |
| 4 | 未获确认即写入 | 文档未定稿 | Step 5.2.4 等待确认 |
| 5 | Step 5 使用 question 工具 | 打断对话流 | 直接对话 |
| 6 | 配图集中在文档首尾 | 图文脱节 | 嵌入相关段落之后 |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | 位置追踪（status/pending/processed/skipped/unskip/list/reset） |
| `scripts/append_readme.py` | 向 README.md 项目文档节追加链接 |

位置文件：`<project-root>/spec2readme/.spec2readme-position.json`

