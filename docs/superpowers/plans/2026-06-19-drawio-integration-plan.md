---
change: migrate-to-drawio-skill
design-doc: docs/superpowers/specs/2026-06-19-drawio-integration-design.md
base-ref: 46a29f68fc4b227b7c864460ac522bc00f59ee83
---

# Drawio-skill Integration for wechat-article-skill 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 将 wechat-article-skill Pre-3 的图片生成从 Python `diagrams` 库 + `diagram.py` 方案替换为 drawio-skill + draw.io CLI 方案，实现品牌图标、自检修复和迭代反馈能力。

**Architecture:** Pre-3 阶段直接委托 drawio-skill 生成配图（与 Step 4-7 委托 wewrite 相同模式），无桥接脚本。drawio-skill 负责 .drawio XML 生成、draw.io CLI 导出 PNG、自检 + 自动修复（≤2 轮），以及用户迭代反馈（≤5 轮）。

**Tech Stack:** drawio-skill (Agents365-ai), draw.io Desktop CLI, npx skills

## Global Constraints

- draw.io Desktop CLI 必须可用（`drawio --version`），不满足则在 Pre-1 提前失败
- drawio-skill 必须通过 `npx skills add Agents365-ai/365-skills -g` 安装
- 图片导出使用 drawio-skill 的默认预设设置
- 字体要求 Microsoft YaHei（微软雅黑）确保中文渲染
- 不修改 wewrite 管道（Step 4-8 零改动）
- 不修改图片嵌入/上传逻辑
- 不修改其他绘图技能（excalidraw, mermaid, plantuml）

---

## 文件结构

| 文件 | 操作 | 说明 |
|------|------|------|
| `skills/wechat-article-skill/SKILL.md` | 修改 | description 元数据、Pre-1.2 依赖检查、Pre-3.3 生图流程、Pre-3.4 确认流程、图片规则、脚本表 |
| `skills/wechat-article-skill/scripts/diagram.py` | 删除 | 不再需要 |
| `skills/wechat-article-skill/references/complete-flow.md` | 修改 | Pre-1/Pre-3 流程更新 |
| `skills/wechat-article-skill/AGENTS.md` | 修改 | Pipeline 表、Key Scripts、WeChat Image Rule |
| `skills/wechat-article-skill/install.ps1` | 修改 | 新增 drawio-skill 安装 + draw.io CLI 检测 |
| `skills/wechat-article-skill/install.sh` | 修改 | 新增 drawio-skill 安装 + draw.io CLI 检测 |

---

### Task 1: 安装 drawio-skill 外部依赖

**Files:**
- Execute: `npx skills add Agents365-ai/365-skills -g`
- Verify: `drawio --version` 和 drawio-skill 可加载

**Interfaces:**
- Consumes: 无
- Produces: drawio-skill 已安装至全局 agents 目录，draw.io CLI 可用

- [x] **Step 1: 安装 drawio-skill**

```bash
npx skills add Agents365-ai/365-skills -g
```

- [x] **Step 2: 验证 draw.io CLI 可用**

```bash
drawio --version
```
Expected: 输出版本号（如 `24.x.x`）。未找到则提示用户安装 draw.io Desktop。

- [x] **Step 3: 验证 drawio-skill 可加载**

确认 `~/.agents/skills/drawio-skill/SKILL.md` 存在，且包含 `/drawio` 触发指令和 6 种预设类型。

- [x] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: install drawio-skill as dependency for diagram generation"
```

---

### Task 2: 更新 SKILL.md — Pre-1 依赖检查 + 元数据

**Files:**
- Modify: `skills/wechat-article-skill/SKILL.md`

**Interfaces:**
- Consumes: Task 1 (drawio-skill 已安装)
- Produces: 更新后的 SKILL.md Pre-1 段 + 元数据

- [x] **Step 1: 更新 description 元数据 — 将 `diagrams library` 改为 `drawio-skill`**

Edit `skills/wechat-article-skill/SKILL.md` lines 3-8:

旧内容：
```
description: >-
  Generate WeChat public account articles from Comet archives. Reads completed
  Comet change archives, summarizes them with user guidance, generates diagrams
  using the diagrams library, and delegates to wewrite for writing, SEO, visual
  AI, formatting, and publishing. Activates on: /wechat-article, write a WeChat
  article from archives, summarize completed changes for WeChat, generate dev
  blog from Comet archives.
```

新内容：
```
description: >-
  Generate WeChat public account articles from Comet archives. Reads completed
  Comet change archives, summarizes them with user guidance, generates diagrams
  using drawio-skill, and delegates to wewrite for writing, SEO, visual AI,
  formatting, and publishing. Activates on: /wechat-article, write a WeChat
  article from archives, summarize completed changes for WeChat, generate dev
  blog from Comet archives.
```

- [x] **Step 2: 更新 metadata 添加 drawio-skill 依赖声明**

Edit `skills/wechat-article-skill/SKILL.md` lines 14-18 — 在 dependencies 中添加 drawio-skill：

旧内容：
```yaml
  dependencies:
    - url: https://github.com/oaker-io/wewrite
      name: WeWrite
      type: tool
      note: Referenced for writing/SEO/formatting/publishing pipeline
```

新内容：
```yaml
  dependencies:
    - url: https://github.com/oaker-io/wewrite
      name: WeWrite
      type: tool
      note: Referenced for writing/SEO/formatting/publishing pipeline
    - url: https://github.com/Agents365-ai/365-skills
      name: drawio-skill
      type: skill
      note: Used for generating article diagrams via draw.io CLI export
```

- [x] **Step 3: 更新 Pre-1.2 依赖检测 — 移除 `diagrams`，新增 wewrite + drawio-skill + draw.io CLI 检测**

Edit `skills/wechat-article-skill/SKILL.md` line 56：

旧内容：
```
**1.2** 检测 Python 依赖：`requests`, `pyyaml`, `diagrams`, `markdown`, `beautifulsoup4`。

检测 wewrite 发布配置：
- `config.yaml` 存在且有 `wechat.appid`/`secret` → 发布就绪
- 不存在或未配 → 设 `skip_publish = true`，走本地预览
```

新内容：
```
**1.2** 检测 Python 依赖：`requests`, `pyyaml`, `markdown`, `beautifulsoup4`。

检测外部 skill 依赖：

- **wewrite**（用于 Step 4-7 写作/SEO/发布管道）：
  ```bash
  if [ ! -d "$HOME/.agents/skills/wewrite" ]; then
    echo "错误：wewrite 未安装。请执行：npx skills add oaker-io/wewrite -g"
    exit 1
  fi
  ```

- **drawio-skill**（用于 Pre-3 图表生成）：
  ```bash
  if [ ! -d "$HOME/.agents/skills/drawio-skill" ]; then
    echo "错误：drawio-skill 未安装。请执行：npx skills add Agents365-ai/365-skills -g"
    exit 1
  fi
  ```

- **draw.io CLI**：
  ```bash
  drawio --version || { echo "错误：draw.io CLI 未安装。请先安装 draw.io Desktop：https://github.com/jgraph/drawio-desktop/releases"; exit 1; }
  ```

检测 wewrite 发布配置：
- `config.yaml` 存在且有 `wechat.appid`/`secret` → 发布就绪
- 不存在或未配 → 设 `skip_publish = true`，走本地预览
```

- [x] **Step 4: 更新 WeChat Image Rule 规则**

Edit `skills/wechat-article-skill/SKILL.md` lines 118-120：

旧内容：
```
> **微信公众号图片规则（重要）**：输出图片应生成高清大图供公众号缩放。
> `diagram.py` 默认 DPI=300 产出约 2250px（3.5x 视网膜），公众号自动缩放至 ~640px 后文字清晰锐利。
> 优先使用 `direction: LR` 以确保图片宽度充足；复杂架构图可调整 `graph_attr.dpi` 微调。
```

新内容：
```
> **微信公众号图片规则（重要）**：输出图片应使用 drawio-skill 默认预设设置，画质满足高清缩放需求。
> 字体使用 Microsoft YaHei（微软雅黑）以确保中文渲染清晰。
```

- [x] **Step 5: Commit**

```bash
git add skills/wechat-article-skill/SKILL.md
git commit -m "feat: update SKILL.md metadata, deps check, and image rules for drawio-skill"
```

---

### Task 3: 更新 SKILL.md — Pre-3 生图流程和确认流程

**Files:**
- Modify: `skills/wechat-article-skill/SKILL.md` lines 116-153

**Interfaces:**
- Consumes: Task 2 (Pre-1 依赖检查已更新)
- Produces: Pre-3.3 委托 drawio-skill 生图逻辑、Pre-3.4 迭代确认流程

- [x] **Step 1: 替换 Pre-3.3 配图执行内容**

Edit `skills/wechat-article-skill/SKILL.md` lines 116-142 — 替换整个配图决策执行段落：

旧内容（lines 116-142）：
```
**3.3** 执行配图决策：

> **微信公众号图片规则（重要）**：输出图片应生成高清大图供公众号缩放。
> `diagram.py` 默认 DPI=300 产出约 2250px（3.5x 视网膜），公众号自动缩放至 ~640px 后文字清晰锐利。
> 优先使用 `direction: LR` 以确保图片宽度充足；复杂架构图可调整 `graph_attr.dpi` 微调。

有架构图/流程图 →
```bash
cat > output/{slug}-spec.yaml <<YAML
title: "Diagram Title"
direction: LR
graph_attr:
  dpi: "300"       # HD source for WeChat downscaling (~640px)
  ranksep: "0.4"   # tighter spacing for compact layout
  splines: ortho   # right-angle edges for architecture diagrams
clusters:
  - label: "Cluster A"
    nodes:
      - id: node1
        label: "Node 1"
        type: generic
      - id: node2
        label: "Node 2"
        type: generic
YAML
python3 <skill-dir>/scripts/diagram.py output/{slug}-spec.yaml -o output/{slug}-arch.png
```

有目录结构 → 用 `tree` / `Get-ChildItem` 输出 → 嵌入代码块。
```

新内容：
```
**3.3** 执行配图决策：

根据配图决策中的类型确定 drawio-skill 预设：

| 内容类型 | drawio-skill 预设 |
|---------|-------------------|
| 架构变更、系统设计 | Architecture diagram |
| 业务流程变化、工作流 | Flow diagram |
| ML 模型变更、训练管线 | ML/Deep Learning diagram |
| 类/接口变更 | UML class diagram |
| 协议/交互变更 | Sequence diagram |
| 数据模型/模式变更 | ER diagram |

对于每张需要生成的图：

1. **构建自然语言描述**：综合 archive 内容生成图片描述，包含关键组件、连接关系、布局要求
2. **加载 drawio-skill**：使用 Skill tool 加载 drawio-skill 的 SKILL.md
3. **委托 drawio-skill 生成**：传递以下参数——
   - 自然语言描述（如 "微服务电商架构图，包含 API Gateway、Auth/User/Order 微服务、Kafka 消息队列"）
   - 预设类型（从上方映射选择）
    - 导出要求："高清画质，Microsoft YaHei 字体"
4. drawio-skill 执行：生成 `.drawio` XML → drawio CLI 导出 PNG → 自检 + 自动修复（≤2 轮）→ 展示图片

有目录结构 → 用 `tree` / `Get-ChildItem` 输出 → 嵌入代码块。
```

- [x] **Step 2: 替换 Pre-3.4 确认流程 — 改为 drawio-skill 迭代反馈模式**

Edit `skills/wechat-article-skill/SKILL.md` lines 146-153：

旧内容：
```
**3.4** 交互确认生图结果：

对每张图，展示并让用户选择：
- **A) 没问题，继续** → 保留并嵌入 markdown：`![alt](output/{slug}-arch.png)`
- **B) 重新生成** → 修改 YAML spec → 重新生图 → 回到确认
- **C) 跳过这张图，纯文字段落无图** → 删除该图行，纯文字前进

目录结构代码块同样走此确认循环。全部确认无误后固定到文章。
```

新内容：
```
**3.4** 交互确认生图结果：

drawio-skill 生成图片后将 PNG 展示给用户。对每张图，让用户选择：
- **A) 没问题，继续** → 保留并嵌入 markdown：`![alt](output/{slug}.png)`
- **B) 修改** → 用户在已有图片基础上描述修改需求（如"将数据库节点左移，并添加缓存层"）→ drawio-skill 重新修改 `.drawio` XML → 重新导出 → 重新展示 → 回到确认（最多 5 轮迭代）
- **C) 跳过这张图，纯文字段落无图** → 删除该图行，纯文字前进

达到 5 轮迭代限制后，提示用户接受当前版本或跳过。

目录结构代码块同样走此确认循环。全部确认无误后固定到文章。
```

- [x] **Step 3: 更新脚本表 — 移除/标记 diagram.py**

Edit `skills/wechat-article-skill/SKILL.md` 脚本表（lines 186-191）：

旧内容：
```
| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | 跟踪/查询/更新 archive 处理位置 |
| `scripts/diagram.py` | 用 diagrams 库生成架构/流程/组件图，输出白底 PNG |
| `scripts/publish.py` | dry-run markdown → HTML 转换（发布委托 wewrite） |
```

新内容：
```
| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | 跟踪/查询/更新 archive 处理位置 |
| `scripts/publish.py` | dry-run markdown → HTML 转换（发布委托 wewrite） |
```

- [x] **Step 4: 更新引用参考 — 添加 drawio-skill 引用**

Edit `skills/wechat-article-skill/SKILL.md` 引用参考段（lines 193-198）：

旧内容：
```
## 引用参考

- `references/writing-guide.md` — WeChat 文章写作风格指南
- `references/wechat-publish.md` — 微信发布配置和排错
- wewrite `SKILL.md` — Step 4-7 的原始指令（位于 wewrite 安装目录）
- wewrite `toolkit/converter.py` — Markdown → 微信 HTML 转换
- wewrite `toolkit/cli.py` — 发布 CLI
```

新内容：
```
## 引用参考

- `references/writing-guide.md` — WeChat 文章写作风格指南
- `references/wechat-publish.md` — 微信发布配置和排错
- wewrite `SKILL.md` — Step 4-7 的原始指令（位于 wewrite 安装目录）
- wewrite `toolkit/converter.py` — Markdown → 微信 HTML 转换
- wewrite `toolkit/cli.py` — 发布 CLI
- drawio-skill `SKILL.md` — Pre-3.3 委托的原始指令（位于 drawio-skill 安装目录）
```

- [x] **Step 5: Commit**

```bash
git add skills/wechat-article-skill/SKILL.md
git commit -m "feat: replace Pre-3 diagram generation with drawio-skill delegation"
```

---

### Task 4: 删除旧代码

**Files:**
- Delete: `skills/wechat-article-skill/scripts/diagram.py`

**Interfaces:**
- Consumes: Task 3 (SKILL.md 已不再引用 diagram.py)
- Produces: 清理后的 scripts 目录

- [x] **Step 1: 删除 diagram.py**

```bash
git rm skills/wechat-article-skill/scripts/diagram.py
```

- [x] **Step 2: Commit**

```bash
git commit -m "feat: remove scripts/diagram.py (replaced by drawio-skill)"
```

---

### Task 5: 更新安装脚本

**Files:**
- Modify: `skills/wechat-article-skill/install.ps1`
- Modify: `skills/wechat-article-skill/install.sh`

**Interfaces:**
- Consumes: Task 1 (drawio-skill 外部依赖)
- Produces: 安装脚本在执行完 skill 安装后自动安装 drawio-skill + 验证 draw.io CLI

- [x] **Step 1: 更新 install.ps1 — 在文件末尾添加 drawio-skill 安装和 draw.io CLI 检测**

Edit `skills/wechat-article-skill/install.ps1` — 在最后一行前插入（即在 `Write-Host "To use it, type: /wechat-article" -ForegroundColor Cyan` 之前）：

旧内容（lines 53-55）：
```
Write-Host ""
Write-Host "Skill installed successfully at: $Target" -ForegroundColor Green
Write-Host ""
Write-Host "To use it, type: /wechat-article" -ForegroundColor Cyan
```

新内容：
```
Write-Host ""
Write-Host "Skill installed successfully at: $Target" -ForegroundColor Green

# Install drawio-skill dependency
Write-Host ""
Write-Host "Installing drawio-skill dependency..." -ForegroundColor Yellow
npx skills add Agents365-ai/365-skills -g 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Failed to install drawio-skill. Install manually:" -ForegroundColor Yellow
    Write-Host "  npx skills add Agents365-ai/365-skills -g" -ForegroundColor Yellow
}

# Check draw.io CLI
$drawioCheck = Get-Command drawio -ErrorAction SilentlyContinue
if (-not $drawioCheck) {
    Write-Host "Warning: draw.io CLI not found. Diagram generation requires draw.io Desktop CLI." -ForegroundColor Yellow
    Write-Host "  Download from: https://github.com/jgraph/drawio-desktop/releases" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "To use it, type: /wechat-article" -ForegroundColor Cyan
```

- [x] **Step 2: 更新 install.sh — 在文件末尾添加 drawio-skill 安装和 draw.io CLI 检测**

Edit `skills/wechat-article-skill/install.sh` — 在结尾 `fi` 之前（第 85 行）的 pip install 块之后添加：

旧内容（lines 79-85）：
```
# Install Python dependencies
if command -v pip3 &>/dev/null; then
  if [ -f "$TARGET/scripts/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r "$TARGET/scripts/requirements.txt" 2>/dev/null || true
  fi
fi
```

新内容：
```
# Install Python dependencies
if command -v pip3 &>/dev/null; then
  if [ -f "$TARGET/scripts/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r "$TARGET/scripts/requirements.txt" 2>/dev/null || true
  fi
fi

# Install drawio-skill dependency
echo ""
echo "Installing drawio-skill dependency..."
npx skills add Agents365-ai/365-skills -g 2>/dev/null || echo "Warning: Failed to install drawio-skill. Install manually: npx skills add Agents365-ai/365-skills -g"

# Check draw.io CLI
if ! command -v drawio &>/dev/null; then
  echo "Warning: draw.io CLI not found. Diagram generation requires draw.io Desktop CLI."
  echo "  Download from: https://github.com/jgraph/drawio-desktop/releases"
fi
```

- [x] **Step 3: Commit**

```bash
git add skills/wechat-article-skill/install.ps1 skills/wechat-article-skill/install.sh
git commit -m "feat: add drawio-skill installation to install scripts"
```

---

### Task 6: 更新文档

**Files:**
- Modify: `skills/wechat-article-skill/references/complete-flow.md`
- Modify: `skills/wechat-article-skill/AGENTS.md`

**Interfaces:**
- Consumes: Task 3 (SKILL.md Pre-3 流程已更新)
- Produces: 所有文档与新的 drawio-skill 流程一致

- [x] **Step 1: 更新 references/complete-flow.md — Pre-1 依赖行**

Edit `skills/wechat-article-skill/references/complete-flow.md` line 19：

旧内容：
```
  1.2  检测 Python 依赖：requests, pyyaml, diagrams, markdown, beautifulsoup4
```

新内容：
```
  1.2  检测 Python 依赖：requests, pyyaml, markdown, beautifulsoup4
       检测 drawio-skill 和 draw.io CLI
```

- [x] **Step 2: 更新 references/complete-flow.md — Pre-3.3 配图执行**

Edit `skills/wechat-article-skill/references/complete-flow.md` lines 88-111：

旧内容（lines 88-111）：
```
   3.3  执行配图决策：

        有架构图 →
          cat > output/{slug}-spec.yaml <<YAML
          title: "磁盘分析工具架构"
          direction: LR
          clusters:
            - label: "扫描层"
              nodes:
                - id: scanner
                  label: "RecursiveScanner"
                  type: generic
                - id: classifier
                  label: "ContentClassifier"
                  type: generic
            - label: "输出层"
              nodes:
                - id: report
                  label: "ReportGenerator"
                  type: generic
          YAML
          python3 <skill>/scripts/diagram.py \
            output/{slug}-spec.yaml \
            -o output/{slug}-arch.png

        有目录结构 →
```

新内容：
```
   3.3  执行配图决策：

        根据内容类型映射 drawio-skill 预设：
          - 架构变更 → Architecture diagram
          - 流程变化 → Flow diagram
          - ML 变更   → ML/Deep Learning diagram
          - 类/接口   → UML class diagram
          - 协议/交互 → Sequence diagram
          - 数据模型  → ER diagram

        对于每张需要生成的图：
          1. 构建自然语言描述（含关键组件和连接关系）
          2. 用 Skill tool 加载 drawio-skill SKILL.md
          3. 委托 drawio-skill：自然语言描述 + 预设类型
          4. drawio-skill 执行：.drawio XML → drawio CLI 导出 PNG → 自检修复 → 展示

        有目录结构 →
```

- [x] **Step 3: 更新 references/complete-flow.md — Pre-3.4 确认流程**

Edit `skills/wechat-article-skill/references/complete-flow.md` lines 121-146：

旧内容（lines 121-146）：
```
   3.4  交互确认生图结果
        ┌────────────────────────────────────────────┐
        │  "这张架构图效果可以吗？                    │
        │                                            │
        │  [output/{slug}-arch.png]                  │
        │                                            │
        │  A) 没问题，继续                           │
        │  B) 重新生成（调整 YAML 再渲）              │
        │  C) 跳过这张图，纯文字段落无图             │
        └─────────┬──────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │         │         │
        A         B         C
        │         │         │
        │   修改 YAML spec  │
        │   重新生图        │
        │   回到确认        │
        │                  │
        ▼                  ▼
       保留并嵌入          删除该图行，
       markdown：         纯文字前进
       ![...](...png)

       目录结构代码块同样走此确认循环
       确认无误后固定到文章
```

新内容：
```
   3.4  交互确认生图结果
        ┌────────────────────────────────────────────┐
        │  "这张架构图效果可以吗？                    │
        │                                            │
        │  [output/{slug}.png]                       │
        │                                            │
        │  A) 没问题，继续                           │
        │  B) 修改（描述修改需求，≤5轮迭代）          │
        │  C) 跳过这张图，纯文字段落无图             │
        └─────────┬──────────────────────────────────┘
                  │
        ┌─────────┴──────────────┐
        │           │            │
        A           B            C
        │           │            │
        │    用户在已有图片       │
        │    基础上描述修改       │
        │    drawio-skill 重渲    │
        │    回到确认（≤5轮）     │
        │                        │
        ▼                        ▼
       保留并嵌入                 删除该图行，
       markdown：                纯文字前进
       ![...](...png)

       达到 5 轮后：接受当前版本或跳过
       目录结构代码块同样走此确认循环
       确认无误后固定到文章
```

- [x] **Step 4: 更新 AGENTS.md — Pipeline 表**

Edit `skills/wechat-article-skill/AGENTS.md` line 15：

旧内容：
```
| Pre-3 | Read archive content, run diagram.py, interactive confirmation |
```

新内容：
```
| Pre-3 | Read archive content, delegate to drawio-skill, interactive confirmation |
```

- [x] **Step 5: 更新 AGENTS.md — WeChat Image Rule**

Edit `skills/wechat-article-skill/AGENTS.md` lines 22-24：

旧内容：
```
## WeChat Image Rule

All generated images must be **high-resolution for downscaling** (WeChat article content area ~640px). Default DPI=300 produces ~2250px (3.5x retina); WeChat scales down to 640px, delivering crisp text via oversampling. Use `direction: LR` for wider output.
```

新内容：
```
## WeChat Image Rule

All generated images should use drawio-skill's default export quality. Ensure Microsoft YaHei (微软雅黑) font is available for Chinese text rendering.
```

- [x] **Step 6: 更新 AGENTS.md — Key Scripts**

Edit `skills/wechat-article-skill/AGENTS.md` lines 26-29：

旧内容：
```
## Key Scripts
- `scripts/position.py` — `status`, `pending`, `set`
- `scripts/diagram.py` — `spec.yaml → white-bg PNG`
- `scripts/publish.py` — dry-run conversion (publish via wewrite CLI)
```

新内容：
```
## Key Scripts
- `scripts/position.py` — `status`, `pending`, `set`
- `scripts/publish.py` — dry-run conversion (publish via wewrite CLI)
```

- [x] **Step 7: Commit**

```bash
git add skills/wechat-article-skill/references/complete-flow.md skills/wechat-article-skill/AGENTS.md
git commit -m "docs: update documentation for drawio-skill integration"
```

---

## Self-Review

### 1. Spec Coverage

| Spec 要求 | 对应 Task |
|-----------|----------|
| LLM generates .drawio XML from natural language description | Task 3 (Pre-3.3) |
| Export PNG using drawio-skill default high-quality settings | Task 3 (Pre-3.3 WeChat Image Rule) |
| Self-check and auto-fix exported images (≤2 rounds) | Task 3 (Pre-3.3 delegating to drawio-skill) |
| Iterative feedback loop (≤5 rounds) | Task 3 (Pre-3.4 feedback loop) |
| Use brand icons and official shape library | Task 3 (Pre-3.3 delegating to drawio-skill) |
| Add drawio-skill as dependency in Pre-1 | Task 2 (Pre-1.2) |
| Remove diagrams from deps | Task 2 (Pre-1.2) |
| Remove scripts/diagram.py | Task 4 |
| Update install scripts | Task 5 |
| Update documentation | Task 6 |

### 2. Placeholder Scan

无 "TBD", "TODO", "implement later", "add appropriate error handling" 等占位符。所有代码块均为完整内容。

### 3. Type Consistency

- Pre-1.2 的 drawio-skill 路径检查与 Task 5 安装脚本的安装路径一致（`~/.agents/skills/drawio-skill`）
- Pre-3.3 的预设类型映射与设计文档完全一致（6 种类型）
- drawio CLI 导出命令在所有涉及处保持一致
- 文件名路径使用 `output/{slug}.png` 替代旧的 `output/{slug}-arch.png` 保持一致
