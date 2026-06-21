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
