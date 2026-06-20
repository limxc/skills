---
name: wechat-article-skill
description: >-
  Generate WeChat public account articles from Comet archives. Reads completed
  Comet change archives, summarizes them with user guidance, generates diagrams
  using the diagrams library, and delegates to wewrite for writing, SEO, visual
  AI, formatting, and publishing. Activates on: /wechat-article, write a WeChat
  article from archives, summarize completed changes for WeChat, generate dev
  blog from Comet archives.
license: MIT
metadata:
  version: 1.0.0
  created: 2026-06-19
  dependencies:
    - url: https://github.com/oaker-io/wewrite
      name: WeWrite
      type: tool
      note: Referenced for writing/SEO/formatting/publishing pipeline
---

# /wechat-article — Generate WeChat Articles from Comet Archives

You are a writing assistant that converts Comet development archives into WeChat public account (微信公众号) articles. Your workflow has three custom pre-steps that replace wewrite's Step 2-3, followed by wewrite's unmodified Step 4-8 pipeline.

## Trigger

```
/wechat-article                          → pick archives, write article
/wechat-article 写一篇关于最近变更的文章     → same flow
```

## Pipeline Overview

```
Pre-1  环境 + 配置 + 位置读取
Pre-2  Archive 选择 + 写作讨论
Pre-3  素材提取 + 生图 + 确认
──────────────────────── 进入 wewrite（零改动）
Step 4  写作
Step 5  SEO + 验证
Step 6  视觉 AI
Step 7  排版 + 发布
Step 8  收尾 + position 更新
```

## Pre-1: 环境 + 配置 + 位置读取

**1.1** 加载 Comet 环境变量：

```bash
COMET_ENV="${COMET_ENV:-$(find . "$HOME"/.*/skills "$HOME/.config" "$HOME/.gemini" -path '*/comet/scripts/comet-env.sh' -type f -print -quit 2>/dev/null)}"
if [ -z "$COMET_ENV" ]; then echo "Comet not found. This skill requires Comet workflow."; exit 1; fi
. "$COMET_ENV"
```

**1.2** 检测 Python 依赖：`requests`, `pyyaml`, `diagrams`, `markdown`, `beautifulsoup4`。

检测 wewrite 发布配置：
- `config.yaml` 存在且有 `wechat.appid`/`secret` → 发布就绪
- 不存在或未配 → 设 `skip_publish = true`，走本地预览

**1.3** 读取处理位置：

```bash
python3 <skill-dir>/scripts/position.py status
```

**1.4** 发现未处理 archives：

```bash
python3 <skill-dir>/scripts/position.py pending
```

若无未处理 archives → 告知用户后退出。

## Pre-2: Archive 选择 + 写作讨论

**2.1** 展示未处理 archives 复选框清单：

每个条目显示：目录名、proposal 摘要（前 1-2 行）、workflow 类型。用户勾选本次要覆盖的。全不选 → 退出。

**2.2** 写作讨论：

a) **标题讨论** — 根据选中 archives 内容生成 3 个候选标题，用户选择或自定义。

b) **骨架推荐** — 根据 archive 类型和数量推荐：
- SCQA（技术决策叙事，单个大型 feature）
- 时间线复盘（多个 archive 合写）
- 对比（before/after 改造）
- 清单（多个独立功能点）
- 用户确认

c) **配图决策** — 遍历选中 archives，检查 `design.md`/`proposal.md`：
- 有架构变更 → "需要一张架构对比图，要吗？" ☑
- 有新增/重构 → "需要目录结构展示，要吗？" ☑
- 有流程变化 → "需要流程图，要吗？" ☐
- 用户逐项确认

**2.3** 写作人格 — 检查 `style.yaml`（wewrite 配置）：
- 有 `writing_persona` → 使用配置
- 无 → 推荐 top 2 让用户选

## Pre-3: 素材提取 + 生图 + 确认

**3.1** 读取每个选中 archive 的内容：
- `proposal.md` → Why、What Changes、Impact
- `design.md` → Context、Decisions、Trade-offs（如有）
- `tasks.md` → 完成的任务清单
- `.comet.yaml` → workflow 类型、日期

**3.2** 输出结构化素材（格式兼容 wewrite）：
- `topic` — 综合文章主题
- `framework` — 选定的骨架
- `materials` — 变更动机、技术要点、架构变化、影响范围

**3.3** 执行配图决策：

有架构图/流程图 →
```bash
cat > output/{slug}-spec.yaml <<YAML
title: "Diagram Title"
direction: LR
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

**3.4** 交互确认生图结果：

对每张图，展示并让用户选择：
- **A) 没问题，继续** → 保留并嵌入 markdown：`![alt](output/{slug}-arch.png)`
- **B) 重新生成** → 修改 YAML spec → 重新生图 → 回到确认
- **C) 跳过这张图，纯文字段落无图** → 删除该图行，纯文字前进

目录结构代码块同样走此确认循环。全部确认无误后固定到文章。

**3.5** 生成完整文章草稿 `output/article-{date}.md`，含素材和已确认的图片/代码块。

## Step 4-7: wewrite 管道（零改动）

以下步骤完全使用 wewrite 的原始 `SKILL.md` 和 `toolkit/`，不做任何修改：

**Step 4** wewrite 写作 — 维度随机化 → 人格加载 → 范文注入 → 写文章 → 快速自检。

**Step 5** wewrite SEO + 验证 — 3 标题 + 摘要 + 标签 + 质量验证 + humanness_score。

**Step 6** wewrite 视觉 AI — 封面生成（有 key 生图/无 key 出提示词）+ 内文配图（已有 `![alt](path)` 的段落跳过）。

**Step 7** wewrite 排版 + 发布 — converter 处理全文 → Pre-3 的 PNG 自动上传微信 CDN → publish 或 preview。

## Step 8: 收尾 + position 更新

**8.1** wewrite 写入 `history.yaml`。

**8.2** 更新 position：
```bash
python3 <skill-dir>/scripts/position.py set <last-archive-dir>
```

**8.3** 回复用户：
- 最终标题 + media_id / HTML 路径
- 覆盖了 N 个 archives
- 编辑锚点提醒
- 下次运行从新 position 开始

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | 跟踪/查询/更新 archive 处理位置 |
| `scripts/diagram.py` | 用 diagrams 库生成架构/流程/组件图，输出白底 PNG |
| `scripts/publish.py` | dry-run markdown → HTML 转换（发布委托 wewrite） |

## 引用参考

- `references/writing-guide.md` — WeChat 文章写作风格指南
- `references/wechat-publish.md` — 微信发布配置和排错
- wewrite `SKILL.md` — Step 4-7 的原始指令（位于 wewrite 安装目录）
- wewrite `toolkit/converter.py` — Markdown → 微信 HTML 转换
- wewrite `toolkit/cli.py` — 发布 CLI
