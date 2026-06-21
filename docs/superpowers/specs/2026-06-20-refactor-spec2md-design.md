---
comet_change: refactor-spec2md
role: technical-design
canonical_spec: openspec
---

# spec2article-wechat → spec2md 重构设计

## 背景

spec2article-wechat 原为 Comet 归档 → 微信公众号文章的转换工具，强依赖 wewrite 的写作、SEO、发布管道。实际使用中发现 wewrite 的发布/SEO 能力对于仅需 Markdown 输出的场景过于冗余，且频繁的 question 工具调用降低了交互效率。

## 目标

- 移除 wewrite 依赖，自建写作人格系统
- 重命名为 spec2md，输出通用 Markdown
- 输出到 `docs/{change-name}-{date}/`
- 引入人格记忆机制，积累用户偏好

## 非目标

- 不保留 SEO、封面图、发布能力
- 不改动 drawio-skill
- 不改动 position.py 核心逻辑

## 目录结构

```
<skill-dir>/
├── SKILL.md
├── scripts/
│   └── position.py
├── personas/
│   ├── tech-coder.yaml
│   ├── tech-coder.memory.json      # 记忆文件（自动创建）
│   ├── cold-analyst.yaml
│   ├── cold-analyst.memory.json
│   └── ...
```

## 工作流

```
Step 1  环境检查（openspec + drawio）+ position 读取
Step 2  Change 选择 + 写作讨论（标题/骨架/配图/人格+记忆注入）
Step 3  素材提取 + drawio 配图 + 写作 + 草案交互 → 定稿
Step 4  position 更新 + 记忆写入 + 回复
```

### Step 1 环境检查

- 检测 `openspec/changes/`（或 `archive/`）存在
- 仅检查 drawio-skill，不检查 wewrite 和发布配置
- `position.py status` → `position.py pending`

### Step 2 Change 选择 + 写作讨论

- 2.1 逐个 change 用 question 工具确认
- 2.2 标题确认
- 2.3 骨架匹配 + question 工具确认
- 2.4 配图计划
- 2.5 人格选择：
  1. 从 `personas/` 加载所有人格
  2. 按 topic 关键词匹配取 top 3
  3. 检查对应 `personas/<name>.memory.json` 是否存在
  4. 存在则注入记忆内容作为额外约束

### Step 3 素材提取 + 配图 + 写作

- 3.1 从 change 的 proposal/design/tasks/.comet.yaml 提取结构化素材
- 3.2 drawio-skill 配图生成
- 3.3 草案生成（人格注入 + 记忆注入 + 素材）
- 3.4 草案展示 → 直接对话反馈 → 修改 → 确认定稿
- 3.5 写入 `docs/{change-name}-{date}/article.md`

### Step 4 后处理

- 4.1 `position.py processed <change-dir>...`
- 4.2 总结本次交互中用户的偏好，写入 `personas/<name>.memory.json`

## 输出目录结构

```
docs/{change-name}-{date}/
├── article.md
├── {change-name}-architecture.png
├── {change-name}-architecture.drawio
└── ...
```

## 记忆机制

### 位置

`personas/<name>.memory.json` — 与人格定义同目录

### 结构

```json
{
  "preferences": [
    "不要在正文中引入代码块",
    "使用更多类比和实例来辅助说明"
  ]
}
```

### 生命周期

- **读取**：Step 2.5 选人格时，记忆注入写作 prompt
- **写入**：Step 4，文章定稿后总结用户本次反馈偏好

## 交互层级

- Step 2.1（change 选择）、Step 2.3（骨架确认）：使用 question 工具
- 其他子步骤：直接对话

## 风险

| 风险 | 缓解措施 |
|------|---------|
| 写作质量下降 | 人格注入 + 记忆积累补偿 |
| 人格文件与 wewrite 不同步 | 标注移植版本号，独立维护 |
| 用户习惯 `/spec2article-wechat` | SKILL.md 标注别名提示 |
