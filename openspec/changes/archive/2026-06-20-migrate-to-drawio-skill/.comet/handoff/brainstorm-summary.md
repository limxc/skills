# Brainstorm Summary

- Change: migrate-to-drawio-skill
- Date: 2026-06-19

## 确认的技术方案

1. **集成模式**: Pre-3 直接委托 drawio-skill（同 wewrite 模式），无桥接脚本。移除 `scripts/diagram.py` 和 `diagrams` Python 依赖。
2. **图表类型判定**: Pre-2.2c 扩展为 6 种（架构图、ML/深度学习、流程图、UML 类图、序列图、ER 图），根据 archive 内容智能匹配。
3. **输出规格**: 使用 drawio-skill 预设样式和默认尺寸，不强制 1080px 宽度。SKILL.md 保留 WeChat 高清说明。
4. **生成流程**: 识别需求+类型 → 加载 drawio-skill → 生成 .drawio XML → CLI 导出 PNG → 自检修复 ≤2 轮 → 展示 → 迭代反馈 ≤5 轮 → 最终 PNG。
5. **确认循环**: 保留现有 3.4 确认机制（A.继续 B.重生成 C.跳过），交互方式不变。

## 关键取舍与风险

- draw.io Desktop CLI 必需 → 已确认已安装
- 旧 YAML spec 不兼容 → old diagram.py 移除，历史 spec 需手动转换
- drawio-skill 不可用 → Pre-1 增加可用性检查，失败时提前报错

## 测试策略

- 集成验证：真实调用一次 drawio-skill 生成测试图
- 边界场景：无 archive 内容、多 archive 合并配图

## Spec Patch

- `specs/diagram-generation/spec.md`: 移除 1080px 硬约束要求
