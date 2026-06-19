# AI Agent Skills

个人维护的skills仓库。

## 安装

```bash
npx skills add limxc/skills
```

## Skills 列表

### **教员视角**

```
  毛泽东的哲学思维框架与问题分析方法。基于《矛盾论》《实践论》等核心著作及40+篇一手文献的深度调研，提炼6个核心心智模型、6条可操作的决策启发式和完整的辩证表达DNA。
  用途：作为思维顾问，用毛泽东式的辩证唯物主义框架分析复杂问题、提升认知水平、训练抓本质的能力。
  当用户提到「用毛选的视角」「毛泽东会怎么看」「矛盾分析法」「实践论思维」「抓主要矛盾」「用主席的视角」「用教员的视角」「从毛选中学」「实事求是」「群众路线」「辩证法」「一分为二」「星星之火可以燎原」「农村包围城市」「论持久战」「战略定力」「辩证唯物主义」时使用。
  即使用户只是说「帮我分析这个复杂问题」「怎么看本质」「怎么调查研究」「抓关键」「问题很乱怎么理清楚」「当前阶段该做什么」「怎么找突破口」「怎么判断时机」「没有调查就没有发言权」也应触发。
```

****_触发方式_**：

- `/mao <问题>`

### **disk-analyser-skill**

Windows 磁盘空间分析工具，递归扫描目录、识别大文件夹、分类用途并提供清理建议。

**测试覆盖**: 44 个测试用例（单元测试 + 集成测试），验证扫描准确性、分类逻辑、TOP5 大小排序。

**_触发方式_**：

- `/disk-space-analyzer <路径>`

### **素材积累相关 skills**

- `agent-skill-creator` — 根据工作流描述创建跨平台 agent skill

## 项目结构

```
skills/
├── mao/
│   ├── SKILL.md
│   └── references/
│       └── research/
│           ├── 01-writings.md
│           ├── 02-conversations.md
│           ├── 03-expression-dna.md
│           ├── 04-external-views.md
│           ├── 05-decisions.md
│           └── 06-timeline.md
└── disk-analyser-skill/
    ├── SKILL.md
    └── scripts/
        ├── scanner.py
        ├── categorizer.py
        ├── formatter.py
        ├── __main__.py
        └── tests/
            ├── test_scanner.py
            ├── test_categorizer.py
            ├── test_formatter.py
            └── test_integration.py
```
