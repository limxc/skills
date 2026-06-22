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
python <skill-dir>/scripts/check_openspec.py
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
- `creating-mermaid-diagrams` 缺失 → 安装后重跑 `env_check.py`：
  ```
  npx skills add https://github.com/Agents365-ai/mermaid-skill
  python <skill-dir>/scripts/env_check.py
  ```
  - 重跑后仍 `ready: false` → 告知用户跳过配图，进入纯文字模式（Step 4 直接跳过，Step 5 不嵌入 mermaid 块）。
- `mmdc` 缺失 → 安装后重跑 `env_check.py`：
  ```
  npm install -g @mermaid-js/mermaid-cli
  python <skill-dir>/scripts/env_check.py
  ```
  - 重跑后仍 `ready: false` → 告知用户跳过配图，进入纯文字模式。

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

如果某个 change 缺少 `proposal.md`，提示用户该 change 缺少关键素材，询问是否继续（可能素材不足）或跳过。

**🔴 CHECKPOINT — 选择"不再显示"会写入 `skipped` 状态，确认后该 change 不会再出现在 pending 列表中。**

## Step 3: 标题 + 输出文件名确认

**Input**: Selected changes list
**Output**: Confirmed title + output file path

**3.1** 根据选中 changes 生成 3 个候选标题，用 question 工具：
- A) {候选标题 1}
- B) {候选标题 2}
- C) {候选标题 3}
- D) 自定义

**3.2** 确定主 change 并生成输出路径：

多个 change 时，以 **`created` 日期最新** 的 change 作为主 change——文件名和日期均取自主 change，其余 change 内容在 Step 5 中作为子节合并到同一篇文档。单个 change 时，该 change 即为主 change。

先对每个选中的 change 运行日期查询，比较选出最新的：
```
python <skill-dir>/scripts/get_change_date.py <change-dir-1>
python <skill-dir>/scripts/get_change_date.py <change-dir-2>
...
```

选出日期最新的 change 作为主 change，对其运行：
```
python <skill-dir>/scripts/prepare_output.py <主-change-name>
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

**🔴 CHECKPOINT — 标题和输出路径已确认。进入 Step 4 后，如果返回修改标题需重新运行 prepare_output.py。**

## Step 4: 素材提取 + mermaid 配图

**Input**: Selected changes + title
**Output**: Material summary + mermaid diagram source code

**4.1** 素材提取与讨论（多轮对话，直至用户确认）

遍历每个选中的 change，读取：
- `proposal.md` → Why / What / Impact
- `design.md` → Context / Decisions / Trade-offs
- `tasks.md` → 完成清单

提取后展示结构化摘要（每个 change 1-2 句核心结论、涉及模块、关键决策、配图素材是否充分）。

**必须**用 question 工具询问用户：
- A) 素材足够，继续生成配图
- B) 需要补充素材（请在下一步输入补充内容）

选择 B 时，使用对话收集用户的补充素材，合并到摘要中，然后**再次用 question 工具确认**是否继续。重复此循环直至用户确认素材足够。

用户确认素材足够后，将所有选中 change 的完整素材合并为一份 `change_material_summary`：每个 change 作为一段，标注 change 名称、Why/What/Impact（来自 proposal.md）及 Context/Decisions/Trade-offs（来自 design.md），用 `---` 分隔。这是后续 4.2 推荐和 5.1 写作的唯一素材来源。

**🔴 CHECKPOINT — 素材范围已确认，后续配图和写作将基于当前素材。进入 Step 4.2 前不得再修改素材范围。**

**4.2** 确定配图类型

**4.2.1** 获取支持的图表类型（动态，不再硬编码猜测）：

```
python <skill-dir>/scripts/get_mermaid_types.py
```

该脚本自动读取 `creating-mermaid-diagrams` skill 的 SKILL.md，提取当前支持的所有图表类型（Flowchart / Sequence / Class / ER / State / Gantt / Pie / Git Graph / C4 Context / Mind Map 等），按 `type` / `keyword` / `use_for` 三字段输出 JSON。如果脚本失败（skill 未安装等），使用兜底列表：`flowchart, sequenceDiagram, erDiagram, classDiagram, stateDiagram-v2, gantt, C4Context, mindmap`。

**4.2.2** 强制映射检查（不得跳过，不得凭感觉猜）：

基于 Step 4.1 的 `change_material_summary`，使用以下内容-类型映射框架**逐项输出命中结果**。

```
内容类别 → 图表类型（命中则必选，不得跳过核心类别）

架构/组件/模块/服务间关系
  → 必选: C4Context（宏观架构全景）
  → 当 change 涉及 ≥2 个独立组件/服务/端点时命中

API/接口/消息传递/请求响应
  → 必选: sequenceDiagram（消息顺序和参与者交互）
  → 当 change 涉及"A 把请求发给 B，B 调 C"这类跨组件交互时命中
  → 重要：此方向与"架构/组件"方向不互斥，两者经常同时命中，必须同时保留

数据模型/实体/字段/外键
  → 必选: erDiagram
  → 当 change 涉及数据库/模型层变更时命中

工作流/流程/多步骤/管道
  → 必选: flowchart（流程走向和决策分支）
  → 当 change 涉及 CI/CD/部署流程/业务步骤时命中

状态/生命周期/转换
  → 必选: stateDiagram-v2
  → 当 change 涉及订单/任务/工单状态机时命中

里程碑/发布/时间线
  → 必选: gantt
  → 当 change 涉及版本发布/迁移计划时命中
```

对每个 change 输出**强制映射检查表**：

| 内容类别 | 是否命中 | 命中证据（引用 change 中的具体组件/接口/实体名） | 必选图表类型 |
|---|:---:|:---|:---|
| 架构/组件 | 是/否 | ... | C4Context |
| API/消息传递 | 是/否 | ... | sequenceDiagram |
| 数据模型 | 是/否 | ... | erDiagram |
| 工作流/流程 | 是/否 | ... | flowchart |
| 状态/生命周期 | 是/否 | ... | stateDiagram-v2 |
| 里程碑/时间线 | 是/否 | ... | gantt |

**规则**：
- 命中类别 ≥1 → 为每个命中类别生成一个配图方向
- **命中"架构/组件"和"API/消息传递"两者时，必须同时保留，不能因"flowchart 也能表达流向"而跳过 sequenceDiagram**
- 命中类别 > 5 时，按 change 核心目标优先级排序，只保留前 5 个
- 未命中任何类别 → 直接进入 Step 5（纯文字）

**4.2.3** 展示并确认：

根据 4.2.2 的检查表生成推荐列表。每个命中类别作为一个独立方向展示，格式：

```
方向：系统架构（涉及 护士 Web 端、服务器、音频网关、电视屏）
图表：C4Context —— 内容：展示护士 Web 端、服务器、音频网关、电视屏的系统级关系 —— 理由：change 涉及多端交互，C4Context 展示宏观架构
选项：A) 保留  B) 跳过（不推荐）

方向：消息交互（涉及 患者→护士→医生→服务器→音频网关→电视屏）
图表：sequenceDiagram —— 内容：展示"呼叫下一位"事件中医生端、服务器、音频网关、电视屏的消息时序 —— 理由：change 涉及服务器同时推送音频和更新屏幕，必须用时序图展示并发消息
选项：A) 保留  B) 跳过（不推荐）
```

对每个方向用 question 确认用户选择。默认推荐：**核心变更相关的方向不得跳过**（4.2.2 中标注"必选"的类别）。如果用户坚持跳过核心方向，需说明理由并记录。

如果没有命中任何方向，不向用户展示任何方向，直接进入 Step 5。

**🔴 CHECKPOINT — 配图方向和类型已确认。进入 Step 4.3 后将按当前选择生成 mermaid 源码，返回修改需重新确认。**

**4.3** 加载 creating-mermaid-diagrams skill 生成配图源码

通过 skill 工具加载 `creating-mermaid-diagrams`，然后对 4.2 中用户确认的每个配图项逐一构造 prompt 请求生成。

用户在 4.2.3 中确认的每个配图项都包含 `content` 字段（如 "微服务电商架构：Mobile/Web → API Gateway → User/Order/Product/Payment 服务 → DB + Redis"），这是**内容描述**，不是完整 prompt。4.3 需要将其**嵌入对应类型的 prompt 模板**（如下表），形成完整 prompt 后再发给 `creating-mermaid-diagrams`。关键是**具体描述组件/实体名称、流向/关系、边界/分支**。

| 配图类型 | 构造方式 / 示例 |
|---------|---------------|
| 架构/系统（flowchart） | "画一个{系统描述}架构图，包含 {组件A}/{组件B}/{组件C}，展示它们之间的{调用/依赖/数据流}关系" 如："画一个微服务电商架构图，包含 Mobile/Web 客户端、API 网关、User/Order/Product/Payment 服务，以及 User DB / Order DB / Product DB / Redis Cache" |
| 时序/协议（sequenceDiagram） | "画一个{场景描述}的时序图：{参与方A}把{请求}发给{参与方B}，{参与方B}调{服务C}，{服务C}查{数据库D}进行{操作}，然后把{结果}沿路径返回。同时画出{错误/异常分支}" 如："画一个 JWT 登录的时序图：Client 把账号密码发给 API Gateway，Gateway 调 Auth Service，Auth Service 查 User DB 校验密码哈希，然后把签名 JWT 沿路径返回 Client。同时画出密码错误的失败分支" |
| 数据模型（erDiagram） | "画一个{系统描述}的 ER 图，包含 {实体A}/{实体B}/{实体C} 等实体，标注它们之间的{关系和外键}" 如："画一个电商系统的 ER 图，包含 User/Order/OrderItem/Product 等实体，标注它们之间的一对多/多对多关系和外键" |
| 状态机（stateDiagram-v2） | "画一个{对象描述}的生命周期状态机：初始态 → {状态A} → {状态B} → {状态C} → 终态，标注各转移的{触发条件}" 如："画一个订单的生命周期状态机：Pending → 支付成功 → Confirmed → 发货 → Shipped → 签收 → Delivered → [*]。同时画出 Pending 超时取消和 Confirmed 退款的分支" |
| 类/领域（classDiagram） | "画一个{领域描述}的类图，包含 {类A}/{类B}/{接口C}，标注它们的{继承、实现和关联关系}" 如："画一个权限系统的类图，包含 User/Role/Permission/UserRole 关联表，标注它们的多对多关联和外键约束" |
| C4 高层架构（C4Context） | "画一个{系统描述}的 C4 Context 图：{用户角色} → {核心系统} → {外部依赖/API}" 如："画一个在线商城系统的 C4 Context 图：顾客/管理员 → 商城系统 → 支付网关/物流系统/短信通知服务" |
| 甘特图/时间线（gantt） | "画一个{项目/迭代描述}的甘特图：{阶段A}（{日期或工期}）→ {阶段B} → {阶段C}，标注{里程碑}" 如："画一个 v2.0 版本的甘特图：需求评审（week1-2）→ 开发（week3-6）→ 测试（week7-8）→ 上线（week9），标注 MVP 交付和全量发布两个里程碑" |
| 其他类型（如 mindmap / pie / gitGraph 等） | 直接用 content 字段作为 prompt，例如类型为 mindmap 时："画一个关于 {content} 的思维导图" |

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

文档结构遵循以下原则：
- **按时间/逻辑组织**：每个 change 独立成节（H2），按发生时间或逻辑依赖排列。文档不是 change 的简单堆砌——每个节应讲清楚"为什么做这事"和"带来了什么变化"。
- **Why 先行**：每个 change 的动机作为节内引言，读者需要先理解背景才能理解具体变更。
- **What 用列表**：变更内容用列表或表格呈现，保持简洁。不需要逐条罗列 tasks.md，而是提炼出有意义的变更点。
- **Impact 单独标注**：影响范围单独标注，让读者一目了然哪些文件或能力被改动。
- **关键决策用引用块**：用 `> ` 突出架构决策和权衡，与普通描述区分开。
- **配图紧跟正文**：配图嵌入在相关段落之后，而不是堆在文档开头或末尾——图文脱节会大幅降低可读性。
- **语言风格**：技术文档风格，清晰简洁，避免营销语气。不写"我们很高兴地宣布"这类废话。

**5.2** 写入后展示绝对路径供用户查看：

```
python -c "from pathlib import Path; print(Path('$OUTPUT_FILE').resolve())"
```

用户阅读后可提出修改请求（直接对话，不得使用 question）。修改后重新展示路径。

用户说出"没问题"/"可以"/"定稿"/"就这样"等明确同意表达后，才进入 Step 6 执行 position 更新和 README 追加。在此之前只修改文档内容，不标记 change 为 processed。

**🔴 CHECKPOINT — 以下步骤会将选中的 changes 标记为 processed 并追加到 README.md。一旦执行，这些 change 需 unskip 才能重新纳入文档生成。**

## Step 6: 后处理

**6.1** 标记 processed：

```
python <skill-dir>/scripts/position.py processed <change-name-1> ... <change-name-N>
```

`<change-name>` = 目录名（如 `prepare_output.py` 输出的 `changeName`）。

**6.2** 追加 README.md 链接：

```
python <skill-dir>/scripts/append_readme.py <project-root> "<final-title>" $OUTPUT_FILE <main-change-name>
```

- `$OUTPUT_FILE`：相对/绝对路径均可，脚本自动转为相对于 README.md 的链接。
- `<main-change-name>`：主 change 目录名（Step 3.2 选出的最新 change）。

无 `## 项目文档` 节则自动创建。

**6.3** 清理临时 `.mmd` 文件（失败可忽略）：

```
python <skill-dir>/scripts/cleanup_mmd.py $MMD_DIR
```

**6.4** 回复用户（汇总）：
- 标题：`{title}`
- 文档路径：`$OUTPUT_FILE`
- 覆盖 N 个 changes：`{change-name-1}`, `{change-name-2}`
- Mermaid 图表：N 个（flowchart / sequence / ...）
- ✅ position 已更新（或 ❌ position 更新更新失败）
- ✅ README.md 项目文档已追加（或 ❌ README.md 项目文档追加失败）

## 异常与边界处理

> 下表是**失败后的修复路径**。执行前要规避的反模式见"反例黑名单"。

| 步骤 | 触发条件 | 一线修复 | 兜底 |
|------|---------|---------|------|
| Step 1 | openspec/ 不存在 / 依赖未安装 / Chrome 缺失 | 运行 `check_openspec.py` / `env_check.py` 检查并按提示安装 | 提示终止或跳过配图 |
| Step 2 | 无 pending changes / 缺 proposal.md | 提供 unskip 选项 / 询问用户是否跳过 | 终止或跳过继续 |
| Step 3 | change 目录结构不完整 | 检查 `.openspec.yaml` 和 `created:` 字段 | 终止 |
| Step 4 | mmdc 校验/渲染失败 / 推荐返回非 JSON 或格式异常 | 修正 `.mmd` / 重试生成 / 重发推荐请求 | 跳过全部配图，进入纯文字写作 |
| Step 5 | 输出文件已存在 / 写入失败 | 确认覆盖或加 `-{n}` 后缀 / 检查目录权限 | 输出内容到终端 |
| Step 6 | position / append_readme 写入失败 | 检查 JSON / README.md 可写 | 告知手动执行 |

## 反例黑名单

以下行为在执行本 skill 时禁止出现，每条都对应真实踩过的坑或可预见的故障模式。

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | Step 4.1 跳过用户确认直接生成配图 | 素材方向不对，后续配图和文档全部重做，浪费 2-3 轮 | 循环问用户，直到收到"素材足够"或"跳过配图"的明确确认 |
| 2 | Step 5.2 未经用户定稿确认就执行 position 更新和 README 追加 | 用户还没看完文档，position 已标记 processed，change 再也无法选中文档 | 用户必须说出"没问题/可以/定稿"等价关键词才进入 Step 6 |
| 3 | 合并素材后忽略部分推荐方向 / 不经用户确认直接采用全部推荐 | 重要配图被遗漏，或次要方向占篇幅导致文档臃肿 | 遵循 Step 4.2 逐项确认，用户选中的才生成，不要漏掉也不要擅自全选 |
| 4 | 未等 creating-mermaid-diagrams 完成就清理 `$MMD_DIR` | 配图源码丢失，文档里 mermaid 块为空 | Step 6.3 清理必须在配图源码嵌入文档之后执行 |
| 5 | 重复写入同一个 `$OUTPUT_FILE` 且不警告 | 覆盖历史文档，用户无法追溯 | 写入前用 python 检查文件是否存在，存在则加 `-{n}` 后缀或用 question 确认覆盖 |
| 6 | 文档堆砌 tasks.md 逐条列表 | 读者看到的是任务清单而不是技术叙事，可读性差 | 遵循 Step 5.1 原则：Why 先行 + What 用列表提炼 + Impact 单独标注 |
| 7 | 配图堆在文档开头或末尾 | 图文脱节，读者需要来回翻 | 遵循 Step 5.1 原则：配图紧跟相关段落，一处内容一张图 |
| 8 | 用户说"修改"时用 question 工具 | question 弹窗不适合多轮修改对话，用户无法自然表达修改意图 | Step 5.2 明确规定了用直接对话，不得使用 question 工具 |
| 9 | 4.3 将 content 字段不经模板包装直接作为 prompt 发送 | creating-mermaid-diagrams 收到残缺指令（如只有组件列表没有"画一个..."），生成无关或空图表 | 必须将 content 嵌入对应类型的 prompt 模板（如"画一个...架构图，包含..."），形成完整 prompt 后再发送 |
| 10 | 多个 change 不合并素材，逐 change 分别推荐给 creating-mermaid-diagrams | 同一模块在不同 change 中出现矛盾配图（如 change A 用 MySQL、change B 改为 PostgreSQL，分别生成两套冲突的 ER 图） | 4.1 必须将所有 change 合并为一份 `change_material_summary`，让模型看到完整叙事和最终态 |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | 位置追踪（status/pending/processed/skipped/unskip/list/reset） |
| `scripts/append_readme.py` | 向 README.md 项目文档节追加链接 |
| `scripts/check_openspec.py` | 检查当前目录是否为 OpenSpec 项目 |
| `scripts/env_check.py` | 依赖环境检查（creating-mermaid-diagrams / mmdc / Chrome） |
| `scripts/prepare_output.py` | 生成输出文件路径和临时目录 |
| `scripts/get_change_date.py` | 从 change 目录的 `.openspec.yaml` 读取 `created:` 日期 |
| `scripts/get_mermaid_types.py` | 读取 creating-mermaid-diagrams 支持的图表类型列表 |
| `scripts/cleanup_mmd.py` | 清理临时 `.mmd` 目录 |
| `scripts/utils.py` | `find_project_root()` / `resolve_change_path()` 共享工具函数 |

位置文件：`<project-root>/spec2readme/.spec2readme-position.json`
