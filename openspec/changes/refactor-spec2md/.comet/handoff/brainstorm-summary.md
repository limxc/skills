# Brainstorm Summary

- Change: refactor-spec2md
- Date: 2026-06-20

## 确认的技术方案

1. **重命名**：spec2article-wechat → spec2md，命令 `/spec2md`
2. **移除 wewrite**：写作人格从 `personas/` 移植，自建匹配 + 注入逻辑
3. **依赖**：仅保留 openspec + drawio-skill
4. **输出**：`docs/{change-name}-{date}/`（article.md + *.png + *.drawio）
5. **流程**：Step 1（环境）→ Step 2（选择/写作讨论）→ Step 3（素材/配图/写作/定稿）→ Step 4（后处理）
6. **记忆机制**：`personas/<name>.memory.json`，Step 4 写入，下次 Step 2 选人格时注入
7. **交互**：Step 2.1/2.3 用 question 工具，3.4.x 直接对话

## 关键取舍与风险

- [R1] 写作质量下降 → 人格注入 + 记忆积累补偿
- [R2] style.yaml 与 wewrite 不同步 → 标注移植版本，独立维护
- [R3] 命令变更 → SKILL.md 标注别名提示

## 测试策略

- 手动跑 `/spec2md` 完整流程验证
- 验证输出到 `docs/{change}-{date}/`
- 验证 position 正确更新

## Spec Patch

无
