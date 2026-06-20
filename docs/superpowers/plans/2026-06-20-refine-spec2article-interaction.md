---
change: refine-spec2article-interaction
design-doc: docs/superpowers/specs/2026-06-20-refine-spec2article-interaction-design.md
base-ref: 936b7b399d2134ba9d493ced403cb5949e052417
---

# 实施计划: refine-spec2article-interaction

**目标文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`

---

## 1. 修改 SKILL.md — 流程结构调整

### 1.1 流图 + Pre-3 输出更新

#### 步骤

**1.1a 更新全局流图（Pre-3 行）**

- **文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`
- **操作**: 替换 `Pre-3` 行的输出描述
- **oldString**:
  ```
  Pre-3  素材提取 + 生图 + 确认   →   Draft + Embedded Images
  ```
- **newString**:
  ```
  Pre-3  素材提取 + 生图 + 确认 + 草案调整 → Final Draft + Embedded Images
  ```
- **预期**: 全局流图反映新的草案调整步骤。

**1.1b 更新流图 wewrite 入口标注**

- **文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`
- **操作**: 将 `（零改动）` 改为 `（强制交互模式）`
- **oldString**:
  ```
  ──────────────────────── 进入 wewrite（零改动）
  ```
- **newString**:
  ```
  ──────────────────────── 进入 wewrite（强制交互模式）
  ```
- **预期**: 流图中 wewrite 入口标注与设计一致。

**1.1c 更新 Pre-3 节头部输出描述**

- **文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`
- **操作**: 修改 Pre-3 节头部的 `**Output**` 行
- **oldString**:
  ```
  **Output**: Structured materials + confirmed images + draft `.md`
  ```
- **newString**:
  ```
  **Output**: Structured materials + confirmed images + final draft `.md`
  ```
- **预期**: Pre-3 节头部明确产出为 final draft。

**1.1d 将原 3.4 顺延为 3.5**

- **文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`
- **操作**: 将 `**3.4**` 改为 `**3.5**`，描述从"生成草稿"改为"生成最终稿"
- **oldString**:
  ```
  **3.4** 生成草稿：`spec2article-wechat-output/article-{date}.md` — 含素材 + 已确认图片/代码块。
  ```
- **newString**:
  ```
  **3.5** 生成最终稿：`spec2article-wechat-output/article-{date}.md` — 含素材 + 已确认图片/代码块。
  ```
- **预期**: 原草稿生成步骤变为步骤 3.5，名称改为"最终稿"。

---

### 1.2 新增 3.4 步骤（草案展示 + 反馈调整）

#### 步骤

**插入新的 3.4 指令块**

- **文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`
- **操作**: 在 `## Step 4-8` 节标题前插入新的 `**3.4**` 指令块
- **oldString**:
  ```
  **3.5** 生成最终稿：`spec2article-wechat-output/article-{date}.md` — 含素材 + 已确认图片/代码块。

  ## Step 4-8: wewrite 管道（零改动，强制交互模式）
  ```
- **newString**:
  ```
  **3.4** 草案展示与反馈调整

  **3.4.1** 展示草案全文：将 3.1 的结构化素材与 3.3 已确认图片/代码块组合为完整文章草案，逐段 inline 展示（不写入文件），每段后标注 `[用户反馈点]`。

  **3.4.2** 逐段反馈：使用 question 工具逐段询问：
  - A) 没问题，继续下一段
  - B) 需要修改（请说明修改要求）
  - C) 整体意见（可多段合并反馈）

  **3.4.3** 调整循环：收到 B 或 C 后，按用户要求修改对应段落，重新展示修改后的全文。重复 3.4.1–3.4.2 直至用户对所有段落认可。

  **3.4.4** 确认定稿：用户对全文认可后，使用 question 工具确认：
  > A) 确认定稿，写入文件  B) 继续修改

  用户选择 A 后进入 3.5。

  **3.5** 生成最终稿：`spec2article-wechat-output/article-{date}.md` — 含素材 + 已确认图片/代码块。

  ## Step 4-8: wewrite 管道（零改动，强制交互模式）
  ```
- **预期**: Pre-3 变为四步：素材提取(3.1) → 生图(3.2) → 确认图片(3.3) → 草案展示与反馈(3.4) → 生成最终稿(3.5)。

---

### 1.3 更新异常处理表

#### 步骤

**在异常表末尾新增草案调整相关行**

- **文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`
- **操作**: 在 `| Pre-3.3 | 图片修改达 5 轮 | ...` 行之后、`| Step 4-8 | wewrite 无响应 >30s | ...` 行之前插入新行
- **oldString**:
  ```
  | Pre-3.3 | 图片修改达 5 轮 | 强制接受或跳过 | 用户二选一 |
  | Step 4-8 | wewrite 无响应 >30s | 重载 wewrite SKILL.md | 手动介入或跳过发布 |
  ```
- **newString**:
  ```
  | Pre-3.3 | 图片修改达 5 轮 | 强制接受或跳过 | 用户二选一 |
  | Pre-3.4 | 用户反馈不明确或不可操作 | 用 question 工具请求具体修改示例 | 使用当前版本作为最终稿 |
  | Pre-3.4 | 调整循环超过 8 轮 | 建议用户接受当前版本 | 用户决定继续或停止 |
  | Step 4-8 | wewrite 无响应 >30s | 重载 wewrite SKILL.md | 手动介入或跳过发布 |
  ```
- **预期**: 异常表覆盖草案调整阶段的两种异常场景。

---

### 1.4 更新反例与黑名单

#### 步骤

**在反例表末尾新增草案调整相关反模式**

- **文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`
- **操作**: 在反例表最后一行之后追加新行
- **oldString**:
  ```
  | 6 | 图片反复修改 >5 轮 | 边际收益递减 | 5 轮后强制接受或跳过 |
  ```
- **newString**:
  ```
  | 6 | 图片反复修改 >5 轮 | 边际收益递减 | 5 轮后强制接受或跳过 |
  | 7 | 将草案写入文件后再让用户修改 | 反复写文件浪费操作，用户不便逐段评论 | inline 展示全文，收集反馈后再写入 |
  | 8 | 修改后不重新展示全文 | 用户不知道改了哪里，失去上下文 | 每次调整后重新展示完整草案 |
  | 9 | 未获用户明确确认即写入文件 | 文章未定稿就进入下游管道 | 等待用户选择"确认定稿"后再写入 |
  ```
- **预期**: 反例表补齐草案调整阶段的三种反模式。

---

## 2. 强化 wewrite 交互模式约束

### 2.1 Step 4-8 入口描述中明确要求强制交互模式

#### 步骤

**更新 Step 4-8 节标题及内嵌 prompt**

- **文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`
- **操作**: 修改 `## Step 4-8` 节标题，增强交互模式描述
- **oldString**:
  ```
  ## Step 4-8: wewrite 管道（零改动，强制交互模式）

  **Input**: Draft from Pre-3
  ```
- **newString**:
  ```
  ## Step 4-8: wewrite 管道（零改动，强制交互模式 — 每步必须用户确认，不得自动推进）

  **Input**: Final draft from Pre-3
  ```
- **预期**: 标题明确"每步必须用户确认，不得自动推进"，输入源改为 Final draft。

---

### 2.2 更新 CHECKPOINT 提示语

#### 步骤

**强化 CHECKPOINT 中的交互模式暂停点描述**

- **文件**: `C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md`
- **操作**: 替换 CHECKPOINT 文本，强调具体决策暂停点
- **oldString**:
  ```
  **🔴 CHECKPOINT — 即将进入 wewrite。确认前可退出，进入后不可撤回。**

  加载 wewrite SKILL.md，prompt 头部追加：

  ```
  [交互模式] 必须用 question 工具在每个决策点暂停确认，不得自动推进。
  需暂停：标题选择、骨架选择、配图决策、文章预览确认、发布确认。
  ```
  ```
- **newString**:
  ```
  **🔴 CHECKPOINT — 即将进入 wewrite（强制交互模式）。以下决策点必须逐个用 question 工具经用户确认后才能推进：标题选择 → 骨架选择 → 配图决策 → 预览确认 → 发布确认。确认前可退出，进入后每个决策点自动暂停等待确认。**

  加载 wewrite SKILL.md，prompt 头部追加：

  ```
  [强制交互模式] 你必须用 question 工具在每个决策点暂停并等待用户确认，不得自动跳过或推进任何步骤。
  强制暂停点：标题选择 → 骨架选择 → 配图决策 → 文章预览确认 → 发布确认。
  任何阶段用户都可以选择"取消并退出"，此时标记 processed 并终止流程。
  ```
  ```
- **预期**: CHECKPOINT 和 prompt 头部都明确列出完整的决策链，强调强制暂停。

---

## 3. 验证

### 3.1 格式验证

- **命令**: `npx skills validate "C:\Users\limxc\.agents\skills\spec2article-wechat\SKILL.md"`
- **预期**: 输出 `SKILL.md is valid` 或类似成功消息，无格式错误。

### 3.2 全局安装确认

- **步骤**:
  1. 确认 `npx skills list -g` 中 spec2article-wechat 指向的路径已更新
  2. 在任意 Comet 项目中执行 `/spec2article-wechat` 确认技能加载正常，Pre-3 显示为 5 步（含草案调整）
- **预期**: 技能加载无报错，流程结构正确。

---

## 变更一览

| 编辑点 | 文件位置（行号参考） | 修改类型 |
|--------|---------------------|---------|
| 全局流图 Pre-3 行 | ~L38 | 替换 |
| 流图 wewrite 入口 | ~L39 | 替换 |
| Pre-3 头部 Output | ~L107 | 替换 |
| 原 3.4 → 3.5 | ~L133 | 替换 |
| 插入新 3.4 | ~L133–135 之间 | 插入 |
| 异常表 | ~L183 | 插入 2 行 |
| 反例表 | ~L197 | 追加 3 行 |
| Step 4-8 节标题 | ~L135 | 替换 |
| CHECKPOINT | ~L140–146 | 替换 |
