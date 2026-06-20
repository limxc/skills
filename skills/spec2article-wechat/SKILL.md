---
name: spec2article-wechat
description: >-
    Generate WeChat public account articles from Comet archives. Reads completed
    Comet change archives, summarizes them with user guidance, generates diagrams
    using drawio-skill, and delegates to wewrite for writing, SEO, visual AI,
    formatting, and publishing. Activates on: /spec2article-wechat, write a WeChat
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
        - url: https://github.com/Agents365-ai/365-skills
          name: drawio-skill
          type: skill
          note: Used for generating article diagrams via draw.io CLI export
---

# /spec2article-wechat — Generate WeChat Articles from Comet Archives

You are a writing assistant that converts Comet development archives into WeChat public account (微信公众号) articles. Your workflow has three custom pre-steps that replace wewrite's Step 2-3, followed by wewrite's unmodified Step 4-8 pipeline.

**路径约定**：本文档中 `<skill-dir>` 指本 SKILL.md 文件所在的目录（即 `spec2article-wechat` 根目录）。

## Trigger

```
/spec2article-wechat                     → pick changes, write article
/spec2article-wechat 写一篇关于最近变更的文章 → same flow
```

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
Step 8  收尾 + position 更新
```

## Pre-1: 环境 + 配置 + 位置读取

**1.1** 加载 Comet 环境变量：

Comet 随 skill 包分发 `.sh` 脚本。在所有平台上查找 `comet/scripts/comet-env.sh` 位置：

- **PowerShell**：若 `bash` 可用，执行 `bash -c "source $(Resolve-Path <path>/comet-env.sh) && env"` 提取环境变量；否则读取脚本内容手动设置 `$COMET_GUARD`/`$COMET_STATE`/`$COMET_HANDOFF`/`$COMET_ARCHIVE` 变量
- **bash/zsh**：`source <path>/comet-env.sh`

若 `$COMET_GUARD` 等变量仍为空，提示"Comet not found. This skill requires Comet workflow."后退出。

**1.2** 检测外部依赖，一次性安装所有缺失项，要求重启即全量重启：

```
missing = []
if not exists ~/.agents/skills/wewrite/:      missing += ["npx skills add oaker-io/wewrite -g"]
if not exists ~/.agents/skills/drawio-skill/:  missing += ["npx skills add Agents365-ai/365-skills -g"]
if drawio --version 失败:                       missing += ["下载 draw.io Desktop"]

if missing 非空:
  执行所有安装命令 (一次性)
  告知用户: "以下依赖已安装，请重启 agent 后重新执行 /spec2article-wechat：{missing}"
  退出

if missing 为空: 继续
```

检测 wewrite 发布配置：

- `~/.agents/skills/wewrite/config.yaml` 存在且有 `wechat.appid`/`secret` → 发布就绪
- 不存在或未配 → 使用单选框询问用户：
    - **A) 跳过发布，仅本地预览** → 设 `skip_publish = true`
    - **B) 填写配置** → 告知路径 `~/.agents/skills/wewrite/config.yaml`，提示填写 AppID 和 AppSecret，退出等待用户配置后重试

**1.3** 读取处理位置：

```bash
python <skill-dir>/scripts/position.py status
```

**1.4** 查找未处理 changes（搜索所有活跃和已归档 change，过滤已标记为 processed 或 skipped 的）：

```bash
python <skill-dir>/scripts/position.py pending
```

- `processed` — 已用于生成文章的 change（下次不再显示）
- `skipped` — 用户明确"跳过"的 change（下次不再显示）

若无未处理 changes → 告知用户"没有未处理的 Comet changes。请先通过 Comet 工作流完成一些变更，或检查 position 状态"。建议运行：

- `python <skill-dir>/scripts/position.py list` — 查看所有 change 及标记状态
- `python <skill-dir>/scripts/position.py unskip <dir>` — 恢复某个被跳过的 change

## Pre-2: Change 选择 + 写作讨论

**2.1** 展示未处理 changes 编号清单，等待用户在对话中直接输入：

展示格式：

```
序号 | 目录名                           | 类型    | 摘要
─────┼──────────────────────────────────┼─────────┼──────────────────────
 1   | 2026-06-19-disk-space-analyzer   | full    | 新增磁盘分析工具
 2   | 2026-06-19-disk-analyzer-tests   | tweak   | 补充测试用例
 3   | 2026-06-20-migrate-to-drawio     | full    | 迁移到 drawio
```

**不调用 question 工具**，直接输出格式提示后等待用户下一句文本回复。用户输入格式：

| 输入            | 含义                             |
| --------------- | -------------------------------- |
| `1 3`           | 选中 1 和 3 写文章，其余下次继续 |
| `s2`            | 标记 2 为"以后不再提示"          |
| `1 s2 3`        | 混输：1 和 3 写文章，s2 不再提示 |
| `1,3,s2`        | 同上，逗号分隔也可               |
| 空 / 取消       | 等待重新输入                     |

支持空格、逗号、中文逗号等任意分隔符。每段以 `s` 开头的视为"不再提示"，纯数字视为"写文章"。

**解析后确认**：解析用户输入后，先汇总展示确认清单，然后调用 question 工具（单选 Yes/No）让用户确认：

```
确认:
  → 写文章: 1(disk-space-analyzer) + 3(migrate-to-drawio)
  → 不再提示: 2(disk-analyzer-tests)
  → 下次继续显示: 4,5
```

用户选 Yes 后：

- 对 s 标记项执行 `python <skill-dir>/scripts/position.py skipped <dir>`
- 写文章项传入后续流程
- 未输入的数字下次继续显示

**2.2** 写作讨论：

a) **标题讨论** — 根据选中 changes 内容生成 3 个候选标题，用户选择或自定义。

b) **骨架推荐** — 根据 change 类型和数量推荐：

- SCQA（技术决策叙事，单个大型 feature）
- 时间线复盘（多个 changes 合写）
- 对比（before/after 改造）
- 清单（多个独立功能点）
- 用户确认

c) **配图决策** — 遍历选中 changes，检查 `design.md`/`proposal.md`：

- 有架构变更 → "需要一张架构对比图，要吗？" ☑
- 有新增/重构 → "需要目录结构展示，要吗？" ☑
- 有流程变化 → "需要流程图，要吗？" ☐
- 用户逐项确认

**2.3** 写作人格 — 检查 `style.yaml`（wewrite 配置）：

- 有 `writing_persona` → 使用配置
- 无 → 推荐 top 2 让用户选

## Pre-3: 素材提取 + 生图 + 确认

**3.1** 读取每个选中 change 的内容：

- `proposal.md` → Why、What Changes、Impact
- `design.md` → Context、Decisions、Trade-offs（如有）
- `tasks.md` → 完成的任务清单
- `.comet.yaml` → workflow 类型、日期

**3.2** 输出结构化素材（格式兼容 wewrite）：

- `topic` — 综合文章主题
- `framework` — 选定的骨架
- `materials` — 变更动机、技术要点、架构变化、影响范围

**3.3** 执行配图决策：

根据配图决策中的类型确定 drawio-skill 预设：

| 内容类型              | drawio-skill 预设        |
| --------------------- | ------------------------ |
| 架构变更、系统设计    | Architecture diagram     |
| 业务流程变化、工作流  | Flow diagram             |
| ML 模型变更、训练管线 | ML/Deep Learning diagram |
| 类/接口变更           | UML class diagram        |
| 协议/交互变更         | Sequence diagram         |
| 数据模型/模式变更     | ER diagram               |

对于每张需要生成的图：

1. **构建自然语言描述**：综合 change 内容生成图片描述，包含关键组件、连接关系、布局要求
2. **加载 drawio-skill**：使用 Skill tool 加载 drawio-skill 的 SKILL.md
3. **委托 drawio-skill 生成**：传递以下参数——
    - 自然语言描述（如 "微服务电商架构图，包含 API Gateway、Auth/User/Order 微服务、Kafka 消息队列"）
    - 预设类型（从上方映射选择）
    - 导出要求："高清画质，Microsoft YaHei 字体"
4. drawio-skill 执行：生成 `.drawio` XML → drawio CLI 导出 PNG → 自检 + 自动修复（≤2 轮）→ 展示图片

有目录结构 → 用 `tree` / `Get-ChildItem` 输出 → 嵌入代码块。

**3.4** 交互确认生图结果：

drawio-skill 生成图片后将 PNG 展示给用户。对每张图，让用户选择：

- **A) 没问题，继续** → 保留并嵌入 markdown：`![alt](spec2article-wechat-output/{slug}.png)`
- **B) 修改** → 用户在已有图片基础上描述修改需求（如"将数据库节点左移，并添加缓存层"）→ drawio-skill 重新修改 `.drawio` XML → 重新导出 → 重新展示 → 回到确认（最多 5 轮迭代）
- **C) 跳过这张图，纯文字段落无图** → 删除该图行，纯文字前进

达到 5 轮迭代限制后，提示用户接受当前版本或跳过。

目录结构代码块同样走此确认循环。全部确认无误后固定到文章。

**3.5** 生成完整文章草稿 `spec2article-wechat-output/article-{date}.md`，含素材和已确认的图片/代码块。所有输出文件（文章草稿、图片等）统一放在该项目根目录下的 `spec2article-wechat-output/` 文件夹中。

## Step 4-7: wewrite 管道（零改动，强制交互模式）

以下步骤完全使用 wewrite 的原始 `SKILL.md` 和 `toolkit/`，不做任何修改。

**交互模式协议**：加载 wewrite SKILL.md 后，在传递给 wewrite 的 prompt 头部追加以下指令——

```
[交互模式] 本会话必须使用 question 工具在每个决策点暂停等待用户确认，不得自动推进。
需暂停的节点：标题选择、骨架选择、配图决策、文章预览确认、发布确认。
```

确保 wewrite 在选题/框架/配图处暂停由用户确认：

**Step 4** wewrite 写作 — 维度随机化 → 人格加载 → 范文注入 → 写文章 → 快速自检。

**Step 5** wewrite SEO + 验证 — 3 标题 + 摘要 + 标签 + 质量验证 + humanness_score。

**Step 6** wewrite 视觉 AI — 封面生成（有 key 生图/无 key 出提示词）+ 内文配图（已有 `![alt](path)` 的段落跳过）。

**Step 7** wewrite 排版 + 发布 — converter 处理全文 → Pre-3 的 PNG 自动上传微信 CDN → publish 或 preview。

## Step 8: 收尾 + position 更新

**8.1** wewrite 写入 `history.yaml`。

**8.2** 更新 position：将本次覆盖的所有 change 标记为 processed，使下次不再显示。

```bash
python <skill-dir>/scripts/position.py processed <change-dir-1> <change-dir-2> ... <change-dir-N>
```

若用户在 Pre-2.1 中标记了跳过项，相关 change 已通过 `skipped` 命令持久化，无需重复处理。

**8.3** 回复用户：

- 最终标题 + media_id / HTML 路径
- 覆盖了 N 个 changes
- 编辑锚点提醒
- 输出位于 `spec2article-wechat-output/` 目录
- 下次运行不再显示已 processed 的 changes

## 脚本

| 脚本                  | 用途                           |
| --------------------- | ------------------------------ |
| `scripts/position.py` | 跟踪/查询/更新 change 处理位置 |

## 引用参考

- wewrite `SKILL.md` — Step 4-7 的原始指令（位于 wewrite 安装目录）
- wewrite `toolkit/converter.py` — Markdown → 微信 HTML 转换
- wewrite `toolkit/cli.py` — 发布 CLI
- drawio-skill `SKILL.md` — Pre-3.3 委托的原始指令（位于 drawio-skill 安装目录）
