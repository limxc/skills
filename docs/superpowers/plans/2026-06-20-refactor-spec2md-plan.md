---
change: refactor-spec2md
design-doc: docs/superpowers/specs/2026-06-20-refactor-spec2md-design.md
base-ref: 02b51e8523017df5f01d864cd399f35ee8558629
---

# spec2md 重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 spec2article-wechat 重构为 spec2md，移除 wewrite 依赖，自建写作人格系统，输出到 docs/

**Architecture:** 修改现有 SKILL.md 文件结构和流程，从 wewrite 移植 persona 文件，移除 wewrite/发布配置检查，新增记忆文件写入。

**Tech Stack:** Python (position.py), YAML (personas), Markdown (输出稿件)

## 涉及的技能目录

`<skill-dir>` = 原 spec2article-wechat SKILL.md 所在目录：
- `C:\Users\limxc\.config\opencode\skills\spec2article-wechat\`（项目副本）
- `C:\Users\limxc\.agents\skills\spec2article-wechat\`（全局安装）

两个目录都需要同步修改。

---

### Task 1: 移植写作人格文件

**Files:**
- Create: `<skill-dir>/personas/` 目录及 7 个 persona yaml 文件（从 wewrite `personas/` 复制）
- Source: `C:\Users\limxc\.agents\skills\wewrite\personas\*.yaml`

- [x] **Step 1: 复制 persona 文件**

```bash
# 确认目标目录存在，复制所有 persona YAML 文件
Copy-Item -Path "$env:USERPROFILE\.agents\skills\wewrite\personas\*.yaml" -Destination "<skill-dir>/personas/"
```

- [x] **Step 2: 验证复制结果**

```bash
Get-ChildItem -Path "<skill-dir>/personas/" -Filter "*.yaml"
```
Expected: 7 persona yaml 文件

---

### Task 2: SKILL.md 主流程重构

**Files:**
- Modify: `<skill-dir>/SKILL.md` — 全部重写

- [x] **Step 1: 重写 SKILL.md 头部**

更改：
- `name: spec2article-wechat` → `name: spec2md`
- 命令：`/spec2md`
- 描述：去除微信公众号绑定，改为通用 Markdown

- [x] **Step 2: 重写 Step 1（环境检查）**

移除：
- wewrite 依赖检查
- 微信发布配置检查 (`wechat.appid`)
保留：
- openspec 项目结构检测
- drawio-skill 检测

- [x] **Step 3: 重写 Step 2（Change 选择 + 写作讨论）**

要点：
- Pre-2.1 → Step 2.1：保留 question 工具选择 change
- Pre-2.3 → Step 2.3：保留 question 工具确认骨架
- Pre-2.5 → Step 2.5：从本地 `personas/` 加载人格，检查 `.memory.json` 并存注入
- 移除 wewrite `style.yaml` 引用

- [x] **Step 4: 重写 Step 3（素材提取 + 配图 + 写作）**

要点：
- Pre-3.1 → Step 3.1：保留素材提取逻辑
- Pre-3.2 → Step 3.2：保留 drawio 配图逻辑
- 新增：Step 3.3 写作（人格注入 + 记忆注入 → 生成文章）
- Pre-3.4 → Step 3.4：草案展示（直接对话）、修改、定稿
- Pre-3.5 → Step 3.5：写入 `docs/{change-name}-{date}/article.md`

- [x] **Step 5: 重写后处理**

Pre-9 → Step 4：
- position.py 更新
- 新增：记忆写入 `personas/<name>.memory.json`
- 回复用户（输出路径）

- [x] **Step 6: 去掉 Step 4-8 wewrite 管道**

删除整个 wewrite 管道章节，包括：
- 强制交互模式说明
- wewrite 技能加载指令
- SEO/视觉AI/排版发布/收尾

- [x] **Step 7: 更新异常处理表和反例表**

移除 wewrite 相关异常行，更新目录路径引用

- [x] **Step 8: 更新 metadata**

```yaml
version: 2.0.0
dependencies:
  - name: drawio-skill
    type: skill
  - name: OpenSpec
    type: skill
```

---

### Task 3: 更新 position.py

**Files:**
- Modify: `<skill-dir>/scripts/position.py`

- [x] **Step 1: 更新环境变量名**

`SPEC2ARTICLE_PROJECT_ROOT` → `SPEC2MD_PROJECT_ROOT`

- [x] **Step 2: 验证无其他路径依赖**

确认没有引用 `spec2article-wechat-output/` 路径

---

### Task 4: 更新 AGENTS.md 和 README.md

**Files:**
- Modify: `<skill-dir>/AGENTS.md`
- Modify: `<skill-dir>/READEME.md`

- [x] **Step 1: 更新 AGENTS.md**

```yaml
# Skill: spec2md
## Activation
- `/spec2md`
```

- [x] **Step 2: 更新 README.md**

更新名称、描述、用法、输出目录等

---

### Task 5: 全局安装同步 + 最终验证

- [x] **Step 1: 同步到全局安装**

若修改的是项目副本，同步到 `~/.agents/skills/spec2md/`

- [x] **Step 2: 运行一次 `/spec2md` 测试流程（脚本变更验证）**

验证：
- [x] 仅检查 openspec + drawio
- [x] change 选择正常
- [x] 输出路径为 `docs/{change-name}-{date}/`
- [x] position 正确更新

---

### Task 6: 提交所有变更

- [x] **Step 1: 提交**

```bash
git add -A && git commit -m "refactor: rename spec2article-wechat to spec2md, remove wewrite dependency, add writing persona system"
```
