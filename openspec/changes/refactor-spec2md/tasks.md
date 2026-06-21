## 1. SKILL.md 重构

- [ ] 1.1 重写 SKILL.md：流程精简为 Pre-1 + Pre-2 + Pre-3 + 后处理，移除 Step 4-9
- [ ] 1.2 更新触发命令：`/spec2article-wechat` → `/spec2md`
- [ ] 1.3 更新描述和 metadata（版本、依赖、名称）
- [ ] 1.4 添加交互层级规则说明（x.x 用 question，x.x.x 直接对话）

## 2. 写作人格移植

- [ ] 2.1 从 wewrite 复制 `style.yaml` 到 `<skill-dir>/style.yaml`
- [ ] 2.2 实现人格匹配逻辑：按 topic 关键词排序取 top 3
- [ ] 2.3 实现人格注入：选中人格写入 prompt 指导写作
- [ ] 2.4 在 Pre-2.5 中加载本地 `style.yaml` 而非 wewrite 路径

## 3. 依赖检查精简

- [ ] 3.1 移除 wewrite 依赖检测
- [ ] 3.2 移除微信发布配置检测
- [ ] 3.3 保留 openspec 项目结构检测和 drawio 检测
- [ ] 3.4 更新异常处理表

## 4. 输出目录迁移

- [ ] 4.1 输出目录从 `spec2article-wechat-output/` 改为 `docs/{change-name}-{date}/`
- [ ] 4.2 更新 position.py：输出目录引用改为 `SPEC2MD_PROJECT_ROOT` 而非 `SPEC2ARTICLE_PROJECT_ROOT`
- [ ] 4.3 确认输出包含：`article.md` + `*.png` + `*.drawio`

## 5. 交互层改造

- [ ] 5.1 Pre-2.1（change 选择）、Pre-2.3（骨架确认）保留 question 工具
- [ ] 5.2 3.4.x（草案展示、收集反馈、修改、定稿）改为直接对话
- [ ] 5.3 移除 3.3 图片确认中的 question 工具（改为直接对话）

## 6. 最终验证

- [ ] 6.1 运行完整 `/spec2md` 流程确认无报错
- [ ] 6.2 验证产物输出到 `docs/{change-name}-{date}/`
