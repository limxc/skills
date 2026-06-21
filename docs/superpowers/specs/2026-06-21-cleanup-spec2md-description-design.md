---
comet_change: fix-spec2md-description-and-cleanup
role: technical-design
canonical_spec: openspec
---

# spec2md 描述修正与清理 — Design Doc

## 变更性质

本次变更为非功能性的文档、描述和脚本实现修正，不涉及新的技术设计。所有改动已在 open 阶段直接完成。

## 设计要点

| 项目 | 处理方式 |
|------|---------|
| history.yaml 降权 | 直接移除功能链路 |
| Comet → OpenSpec 命名 | SKILL.md/README 文本替换 |
| Step 4.2 PowerShell → Python | `scripts/append_readme.py` 替代内联 Powershell 代码 |
| frameworks.md 用户选择 → auto-match | 重写输出格式说明 |
| 冗余文件清理 | 移除 drawio-usage.md、drawio-style-presets.md、exemplars/ |

## 风险

无。所有变更仅影响技能的描述文本、参考文档和脚本实现方式，不改变 spec2md 的核心工作流逻辑。
