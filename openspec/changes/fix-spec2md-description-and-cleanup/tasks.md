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
