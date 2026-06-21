## 1. SKILL.md 重构

## 1. SKILL.md 重构

- [x] 1.1 重写 SKILL.md：流程精简为 Step 1-4，移除 wewrite 管道
- [x] 1.2 更新触发命令：`/spec2article-wechat` → `/spec2md`
- [x] 1.3 更新描述和 metadata（版本、依赖、名称）
- [x] 1.4 添加交互层级规则说明

## 2. 写作人格移植

- [x] 2.1 从 wewrite 复制 persona yaml 到 `<skill-dir>/personas/`
- [x] 2.2 实现人格匹配逻辑：按 topic 关键词排序取 top 3
- [x] 2.3 实现人格注入：选中人格写入 prompt 指导写作
- [x] 2.4 在 Step 2.5 中加载本地 `personas/` 而非 wewrite 路径

## 3. 依赖检查精简

- [x] 3.1 移除 wewrite 依赖检测
- [x] 3.2 移除微信发布配置检测
- [x] 3.3 保留 openspec 项目结构检测和 drawio 检测
- [x] 3.4 更新异常处理表

## 4. 输出目录迁移

- [x] 4.1 输出目录从 `spec2article-wechat-output/` 改为 `docs/{change-name}-{date}/`
- [x] 4.2 更新 position.py：输出目录引用改为 `SPEC2MD_PROJECT_ROOT`
- [x] 4.3 确认输出包含：`article.md` + `*.png` + `*.drawio`

## 5. 交互层改造

- [x] 5.1 Step 2.1（change 选择）、Step 2.3（骨架确认）保留 question 工具
- [x] 5.2 Step 3.4.x（草案展示、收集反馈、修改、定稿）改为直接对话
- [x] 5.3 交互相应规则在 SKILL.md 中明确标注

## 6. 最终验证

- [x] 6.1 全局安装验证完成
- [x] 6.2 产物结构验证通过
