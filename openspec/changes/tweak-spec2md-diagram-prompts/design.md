## 实现说明

### 配图提示词优化

在 Step 3.2 的 6 个提示词模板末尾，统一追加以下布局质量约束（自然语言，不增加额外模板参数）：

```
布局要求：
- 节点之间保持充足间距（简单图≥200px 水平、≥150px 垂直；复杂图≥350px 水平、≥250px 垂直）
- 在行/列之间留出约 80px 的空白路由通道，避免连线穿越无关形状
- 多连线节点的出入口点均匀分布在形状四边，避免堆叠在同一点
- 跨多行的连线使用 waypoints 绕行四周，不从图表中间横穿
- 所有坐标对齐到 10 的倍数
- 文字使用 html=1 确保正确渲染，形状大小适应文字内容，避免裁剪
```

无需改动架构，只需调整传递给 drawio-skill 的自然语言描述。

### 安装地址修正

- 头部 metadata 的 `url` 从 `https://github.com/Agents365-ai/365-skills` 改为 `https://github.com/Agents365-ai/drawio-skill`
- Step 1.2 的安装命令从 `npx skills add Agents365-ai/365-skills -g` 改为 `npx skills add https://github.com/Agents365-ai/drawio-skill --skill drawio-skill`
