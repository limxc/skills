# Mermaid 配图推荐 Prompt 模板

将此 prompt 连同 4.1 的完整素材发给 `creating-mermaid-diagrams` skill，填充 `{change_material_summary}` 占位符。

**重要**：推荐前必须先查阅 `creating-mermaid-diagrams` 自身的 reference 文件获取当前完整类型列表，不要基于记忆做判断。

```
请先查阅 creating-mermaid-diagrams skill 的 reference 文件（FLOWCHART.md / SEQUENCE.md / CLASS-ER.md / OTHER-TYPES.md），
获取当前支持的完整图表类型列表及每种类型的适用场景。

然后根据以下 OpenSpec change 的内容，从支持的类型中按内容方向/视角分组推荐配图。

分组原则：
- 每个独立的内容方向/视角作为一组。例如：
  - 系统架构（组件拓扑、调用关系、部署结构）
  - 数据模型（实体、表结构、外键关系）
  - 协议交互（请求/响应、消息传递、时序）
  - 状态流转（生命周期、状态机、状态转移条件）
  - 项目时间线（里程碑、阶段规划）
- 每个方向给出 1 个推荐项 + 不超过 2 个备选项。
- 避免同一个方向用多种同质化图表重复表达。
- 每个 change 最多推荐 3 个方向，优先覆盖 proposal.md 的核心变更点。

对每一个选项，必须输出：
- direction：该选项对应的内容方向/视角
- type：图表类型（必须是 creating-mermaid-diagrams 支持的类型）
- content：这张图应该画什么（具体组件 / 实体 / 参与方 / 状态 / 流程步骤等）
- reason：为什么这个类型适合该视角
- recommended：true（推荐项）或 false（备选项）

返回 JSON 数组，例如：
[
  {
    "direction": "系统架构",
    "type": "flowchart",
    "content": "微服务电商架构：Mobile/Web → API Gateway → User/Order/Product/Payment 服务 → DB + Redis",
    "reason": "proposal.md 描述系统拆分为多个服务并说明调用关系",
    "recommended": true
  },
  {
    "direction": "系统架构",
    "type": "C4Context",
    "content": "电商系统上下文：用户 → 电商系统 → 支付/物流/通知外部服务",
    "reason": "适合展示系统与外部依赖的高层级关系",
    "recommended": false
  },
  {
    "direction": "数据模型",
    "type": "erDiagram",
    "content": "电商核心实体：User、Order、OrderItem、Product 及其关系",
    "reason": "design.md 定义了数据模型和实体间外键关系",
    "recommended": true
  }
]

如果没有合适的配图类型，返回 []。

change 内容摘要如下：
{change_material_summary}
```
