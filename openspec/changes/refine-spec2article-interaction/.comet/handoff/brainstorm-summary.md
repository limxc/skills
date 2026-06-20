# Brainstorm Summary

- Change: refine-spec2article-interaction
- Date: 2026-06-20

## 确认的技术方案

在 spec2article-wechat 的 Pre-3 阶段，配图确认（3.3）后、生成草稿（原 3.4）前，新增「草稿展示 + 用户反馈调整」步骤。

- 3.4: agent 展示全文草案（直接文本呈现），用户逐段或整体反馈修改意见，agent 当场调整并重新展示，循环直到用户满意
- 调整不设硬上限
- 满意后执行 3.5（原 3.4 顺延），写入 `.md` 文件
- Step 4-8 wewrite 管道入口强化 `[交互模式]` 指令，明确定义决策点暂停列表

## 关键取舍与风险

- 增加一次交互环节但避免发布后不满需要重跑
- 交互次数由用户自然决定，避免 agent 单方截断

## 测试策略

- 运行 `npx skills validate` 验证 SKILL.md 格式
- 全局安装后确认 skill 加载与交互正常

## Spec Patch

无
