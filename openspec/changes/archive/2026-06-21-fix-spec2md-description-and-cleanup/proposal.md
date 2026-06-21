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
