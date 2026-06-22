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
| spec2md | 从 OpenSpec 变更归档生成 Markdown 总结文章，含 drawio 配图 | `/spec2md` |
| spec2readme | 从 OpenSpec 变更归档生成技术文档/README/changelog，含 Mermaid 配图 | `/spec2readme` |

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
├── spec2md/
│   ├── SKILL.md
│   ├── AGENTS.md
│   ├── README.md
│   ├── personas/
│   ├── scripts/
│   │   ├── position.py
│   │   └── append_readme.py
│   └── references/
├── spec2readme/
│   ├── SKILL.md
│   ├── AGENTS.md
│   ├── scripts/
│   │   ├── append_readme.py
│   │   ├── check_openspec.py
│   │   ├── cleanup_mmd.py
│   │   ├── env_check.py
│   │   ├── get_change_date.py
│   │   ├── position.py
│   │   ├── prepare_output.py
│   │   └── utils.py
│   └── test-prompts.json
```

> `spec2md` 详见 [`skills/spec2md/README.md`](skills/spec2md/README.md)
