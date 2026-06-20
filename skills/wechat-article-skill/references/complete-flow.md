# wechat-article-skill 完整流程

自实现前置（Pre-1 ~ Pre-3）+ wewrite 管道（Step 4-8，零改动）

```
┌─────────────────────────────────────────────────────────────────────┐
│                    wechat-article-skill 完整流程                      │
│              自实现前置 + wewrite 管道（零改动）                       │
└─────────────────────────────────────────────────────────────────────┘


Pre-1  环境 + 配置 + 位置读取
──────────────────────────────────────────────────────────────────────

  1.1  加载 Comet 环境变量
       COMET_ENV="${COMET_ENV:-$(find . ... -path '*/comet/scripts/comet-env.sh' -type f -print -quit)}"
       . "$COMET_ENV"

  1.2  检测 Python 依赖：requests, pyyaml, markdown, beautifulsoup4
       检测外部 skill 依赖：wewrite、drawio-skill、draw.io CLI
       wewrite 检测（可选，用于发布）：
       - config.yaml 存在 → 加载 wechat.appid/secret
       - 不存在或未配 → 设 skip_publish = true

  1.3  读取处理位置：
       python3 <skill>/scripts/position.py status

  1.4  发现未处理 archives：
       python3 <skill>/scripts/position.py pending
       若无 → 告知用户退出


Pre-2  Archive 选择 + 写作讨论
──────────────────────────────────────────────────────────────────────

  2.1  展示未处理 archives 清单（复选框）：
       ┌──────────────────────────────────────────────────┐
       │  [x] 2026-06-19-disk-space-analyzer             │
       │       新增磁盘分析工具                           │
       │  [ ] 2026-06-19-fix-disk-analyzer-slots-encoding│
       │       修复编码问题                               │
       │  [x] 2026-06-19-disk-analyzer-tests             │
       │       补全测试覆盖                               │
       └──────────────────────────────────────────────────┘
       用户勾选；全不选 → 退出

  2.2  写作讨论

       a) 标题讨论：
          - 根据 archives 内容生成 3 个候选标题
          - 用户选择或自定义

       b) 骨架推荐：
          - SCQA（技术决策叙事）
          - 时间线复盘（多个 archive 合写）
          - 对比（before/after）
          - 清单（多个独立功能点）
          - 用户确认

       c) 配图决策：
          - 遍历选中 archives，检查 design.md/proposal.md
          - 有架构变更 → "需要一张架构对比图，要吗？" ☑
          - 有新增/重构 → "需要目录结构展示，要吗？" ☑
          - 有流程变化 → "需要流程图，要吗？" ☐
          - 用户逐项确认

  2.3  写作人格（复用 wewrite personas）
       - style.yaml 有 writing_persona → 使用配置
       - 无 → 推荐 top 2 让用户选


Pre-3  素材提取 + 生图
──────────────────────────────────────────────────────────────────────

  3.1  读取归档内容（每选中一个 archive）：
       - proposal.md  → Why、What Changes、Impact
       - design.md   → Context、Decisions、Trade-offs（如有）
       - tasks.md    → 完成的任务清单
       - .comet.yaml → workflow 类型、日期

  3.2  输出结构化素材（格式兼容 wewrite）：
       topic:       磁盘分析工具开发复盘
       framework:   时间线复盘
       materials:
         - 动机：用户需要分析 Windows 磁盘空间占用
         - 架构：递归扫描 + 内容分类 + 清理建议
         - 测试：补全测试覆盖，包括 encoding edge cases

   3.3  执行配图决策：

        根据内容类型映射 drawio-skill 预设：
          - 架构变更 → Architecture diagram
          - 流程变化 → Flow diagram
          - ML 变更   → ML/Deep Learning diagram
          - 类/接口   → UML class diagram
          - 协议/交互 → Sequence diagram
          - 数据模型  → ER diagram

        对于每张需要生成的图：
          1. 构建自然语言描述（含关键组件和连接关系）
          2. 用 Skill tool 加载 drawio-skill SKILL.md
          3. 委托 drawio-skill：自然语言描述 + 预设类型
          4. drawio-skill 执行：.drawio XML → drawio CLI 导出 PNG → 自检修复 → 展示

        有目录结构 →
         ```
         ├── scripts/
         │   ├── scan.py
         │   └── analyze.py
         └── references/
         ```

   3.4  交互确认生图结果
        ┌────────────────────────────────────────────┐
        │  "这张架构图效果可以吗？                    │
        │                                            │
        │  [output/{slug}.png]                       │
        │                                            │
        │  A) 没问题，继续                           │
        │  B) 修改（描述修改需求，≤5轮迭代）          │
        │  C) 跳过这张图，纯文字段落无图             │
        └─────────┬──────────────────────────────────┘
                  │
        ┌─────────┴──────────────┐
        │           │            │
        A           B            C
        │           │            │
        │    用户在已有图片       │
        │    基础上描述修改       │
        │    drawio-skill 重渲    │
        │    回到确认（≤5轮）     │
        │                        │
        ▼                        ▼
       保留并嵌入                 删除该图行，
       markdown：                纯文字前进
       ![...](...png)

       达到 5 轮后：接受当前版本或跳过
       目录结构代码块同样走此确认循环
       确认无误后固定到文章

  3.5  生成完整文章草稿 output/article-{date}.md
       含 3.2 的素材 + 3.4 嵌入的图片/代码块

       ↓ 进入 wewrite 管道（零改动） ↓


Step 4  wewrite 写作（零改动）
──────────────────────────────────────────────────────────────────────

  4.1  维度随机化
  4.2  加载写作人格（persona/{人格}.yaml）
  4.3  范文风格注入（有范文库 → 范文；无 → exemplar-seeds.yaml）
  4.4  写文章（素材来自 Pre-3，图已嵌入 markdown）
       - 2-3 个编辑锚点
  4.5  快速自检


Step 5  wewrite SEO + 验证（零改动）
──────────────────────────────────────────────────────────────────────

  5.1  3 备选标题 + 摘要 + 标签 + 关键词密度
  5.2  质量验证（writing-guide.md 规则 1.1-3.2）
  5.3  humanness_score 辅助


Step 6  wewrite 视觉 AI（零改动）
──────────────────────────────────────────────────────────────────────

  6.1  实体提取
  6.2  封面生成（image_gen.py，有 key 生图 / 无 key 出提示词）
  6.3  封面验证
  6.4  内文配图
       - **已有 ![alt](path) 的段落 → 跳过**
       - 无图的段落按原有流程生图


Step 7  wewrite 排版 + 发布（零改动）
──────────────────────────────────────────────────────────────────────

  7.1  Metadata 预检
  7.2  排版（converter）
       - Pre-3 的 PNG → converter 识别为本地图片
       - publish → upload_image 上传微信 CDN → 替换 src
  7.3  发布或预览（根据 skip_publish）


Step 8  收尾 + position 更新
──────────────────────────────────────────────────────────────────────

  8.1  wewrite 写入 history.yaml
  8.2  更新 position：
       python3 <skill>/scripts/position.py set \
         2026-06-19-disk-analyzer-tests
  8.3  回复用户：
       - 最终标题 + media_id / HTML 路径
       - 覆盖了 N 个 archives
       - 编辑锚点提醒
       - 下次运行从新 position 开始
```
