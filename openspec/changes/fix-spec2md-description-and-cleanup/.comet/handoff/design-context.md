# Comet Design Handoff

- Change: fix-spec2md-description-and-cleanup
- Phase: design
- Mode: compact
- Context hash: 905c560b6ea9826aa5fb6af02c683b31853bc019168189225245ead4f6c1c6c0

Generated-by: comet-handoff.sh

OpenSpec remains the canonical capability spec. This handoff is a deterministic, source-traceable context pack, not an agent-authored summary.

## openspec/changes/fix-spec2md-description-and-cleanup/proposal.md

- Source: openspec/changes/fix-spec2md-description-and-cleanup/proposal.md
- Lines: 1-34
- SHA256: c620034ba9bb25fbc9deaf1c510e81a1babb0a1b2e70437fc7f1ff47b2fa900f

```md
## Why

spec2md skill 的内容与实际行为存在多处偏差：描述中称"Comet development archives"但实际消费的是 `openspec/changes/` 目录；引用了已废弃的 `history.yaml` 降权功能；README 输出目录与实际不一致；Step 4.2 使用 Windows-only PowerShell 代码；references/ 目录包含冗余文件。这些偏差降低了技能的准确性和可维护性。

## What Changes

- **移除**：写作人格降权逻辑（2.5.2）和 `history.yaml` 全部引用
- **修正**：SKILL.md/README 中"Comet" → "OpenSpec" 命名（6 处）
- **修正**：Step 编号错误（2.5.2 引用 Step 4.4 → Step 4.3）
- **修正**：README 输出目录 `docs/` → `spec2md/`
- **修正**：README "人格记忆注入" → "写作人格"
- **修正**：`references/frameworks.md` 用户选择 → 自动匹配规则
- **转换**：Step 4.2 从 PowerShell 内联代码 → `scripts/append_readme.py` Python 脚本
- **清理**：移除 `references/exemplars/` 空目录、`references/drawio-usage.md`、`references/drawio-style-presets.md`（冗余副本）
- **更新**：AGENTS.md 引用新脚本

## Capabilities

### New Capabilities
- 无新增 capability

### Modified Capabilities
- 无 spec 级别变更（仅技能内部描述和脚本调整）

## Impact

- `skills/spec2md/SKILL.md` — 多处文本修正，Step 4.2 改为 Python 脚本调用
- `skills/spec2md/README.md` — 描述和目录路径修正
- `skills/spec2md/AGENTS.md` — 新增脚本引用
- `skills/spec2md/references/frameworks.md` — 输出格式改为自动匹配规则
- `skills/spec2md/references/persona-selection.md` — 移除规则 3（降权处理）
- `skills/spec2md/references/writing-guide.md` — 移除 history.yaml 维度追踪
- `skills/spec2md/references/` — 删除 3 个冗余文件
- `skills/spec2md/scripts/append_readme.py` — 新增
```

## openspec/changes/fix-spec2md-description-and-cleanup/design.md

- Source: openspec/changes/fix-spec2md-description-and-cleanup/design.md
- Lines: 1-28
- SHA256: e56d3c602c286e8878f99cabbdc7073683772b4e2da869fd76a8808bec2d5414

```md
## Context

spec2md skill (`skills/spec2md/`) 存在多处内容与实际行为偏差，包括命名不准确（Comet → OpenSpec）、引用已废弃功能（history.yaml 降权）、README 目录不一致、Step 4.2 使用 Windows-only PowerShell、frameworks.md 与 SKILL.md 行为矛盾、以及 references/ 下存在冗余文件。这些偏差在 skills 仓库内积累，不影响功能但降低技能质量和可移植性。

## Goals / Non-Goals

**Goals:**
- 消除所有"描述与实际行为不符"的偏差
- 移除已废弃的 history.yaml 功能链路
- Step 4.2 跨平台化（PowerShell → Python）
- 清理冗余参考文件

**Non-Goals:**
- 不改变 spec2md 的核心工作流逻辑
- 不涉及 drawio-skill 或其他外部依赖的修改
- 不改变 position.py 的行为

## Decisions

1. **Python 替代 PowerShell**：Step 4.2 脚本化。spec2md 已有 Python 依赖（position.py），新增 `append_readme.py` 零额外依赖，且跨平台兼容。
2. **直接移除 history.yaml 相关代码**：而非保留并标记 deprecated。降权功能已被移除，无保留价值。
3. **frameworks.md 改为自动匹配参考**：原文件是 wewrite 的框架选择 UI，spec2md 的 Step 3.3 已改为 auto-match，因此重写 frameworks.md 的说明以匹配实际行为。
4. **移除 drawio 参考副本**：drawio-usage.md 和 drawio-style-presets.md 是从 drawio-skill 复制的，spec2md 委托 drawio-skill 生成图表，drawio-skill 自含这些文档，因此移除冗余副本。

## Risks / Trade-offs

- 无功能风险 — 所有更改仅涉及描述文本和脚本实现方式
- `append_readme.py` 正则匹配依赖 `## 需求时间线` 标题格式，与现有 README 保持一致
```

## openspec/changes/fix-spec2md-description-and-cleanup/tasks.md

- Source: openspec/changes/fix-spec2md-description-and-cleanup/tasks.md
- Lines: 1-33
- SHA256: 28fda5dc51ac0062bd088358481506ac49ae7be54ffa3ad56bd61c2fe0cbfa0a

```md
## 1. 移除 history.yaml 降权功能

- [x] 1.1 移除 SKILL.md Step 2.5.2（history.yaml 降权逻辑）
- [x] 1.2 简化 SKILL.md Step 2.5.2（原 2.5.3），移除历史检查
- [x] 1.3 移除 SKILL.md Step 4.2（history.yaml 写入）
- [x] 1.4 移除 SKILL.md 中 history.yaml 的输出、错误处理和引用
- [x] 1.5 移除 references/persona-selection.md 规则 3（降权处理）
- [x] 1.6 移除 references/writing-guide.md 中 history.yaml 维度追踪

## 2. 修正命名不准确

- [x] 2.1 SKILL.md "Comet" → "OpenSpec"（6 处）
- [x] 2.2 README.md "Comet 开发归档" → "OpenSpec 变更归档"
- [x] 2.3 修正 README 输出目录 `docs/` → `spec2md/`

## 3. 修复编号错误和描述

- [x] 3.1 修正 Step 2.5.2 引用 "Step 4.4" → "Step 4.3"
- [x] 3.2 修正 Step 4 概览 "history 记录" → 移除
- [x] 3.3 README "人格记忆注入" → "写作人格"

## 4. 跨平台化 Step 4.2

- [x] 4.1 创建 `scripts/append_readme.py`
- [x] 4.2 替换 SKILL.md 中 PowerShell 内联代码为 Python 调用
- [x] 4.3 更新 AGENTS.md 引用新脚本

## 5. 清理冗余文件和修正框架

- [x] 5.1 移除空目录 `references/exemplars/`
- [x] 5.2 移除冗余文件 `references/drawio-usage.md`
- [x] 5.3 移除冗余文件 `references/drawio-style-presets.md`
- [x] 5.4 重写 `references/frameworks.md` 输出格式为自动匹配规则
```

