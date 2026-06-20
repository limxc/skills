# AI Agent Skills

个人维护的 skills 仓库。

## 安装

```bash
npx skills add limxc/skills
```

## Skills 列表

| Skill | 说明 | 触发方式 |
|-------|------|----------|
| mao | 毛泽东哲学思维框架与问题分析方法，基于《矛盾论》《实践论》等核心著作 | `/mao <问题>` |
| disk-analyser-skill | Windows 磁盘空间分析工具，递归扫描目录并分类清理建议 | `/disk-space-analyzer <路径>` |
| spec2article-wechat | 从 Comet archive 生成微信公众号文章。读取已归档变更，经写作讨论后由 wewrite 管道完成写作/SEO/配图/排版/发布 | `/spec2article-wechat` |

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
├── disk-analyser-skill/
│   ├── SKILL.md
│   └── scripts/
│       ├── scanner.py
│       ├── categorizer.py
│       ├── formatter.py
│       ├── __main__.py
│       └── tests/
│           ├── test_scanner.py
│           ├── test_categorizer.py
│           ├── test_formatter.py
│           └── test_integration.py
└── spec2article-wechat/
    ├── SKILL.md
    ├── AGENTS.md
    ├── README.md
    ├── scripts/
    │   └── position.py
    └── references/
        ├── archives-workflow.md
        ├── writing-guide.md
        └── wechat-publish.md
```

> `spec2article-wechat` 的完整流程见 [`skills/spec2article-wechat/SKILL.md`](skills/spec2article-wechat/SKILL.md)
