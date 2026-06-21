# spec2md

从 OpenSpec 变更归档生成 Markdown 文章（含 drawio 配图）。

## 使用

```
/spec2md
```

流程：
1. 环境检查（openspec 结构、drawio-skill、draw.io CLI）
2. 列出未处理的 change → 选择 → 确认标题、骨架、配图、写作人格
3. 素材提取 → drawio 配图 → 框架匹配 → 写作 → 草案确认 → 定稿
4. position 标记 + README 需求时间线追加

## 输出

`spec2md/{date}-{change-name}/article.md` 及配图文件。

## 依赖

- Python 3.8+
- draw.io Desktop CLI
- [drawio-skill](https://github.com/Agents365-ai/365-skills) `npx skills add Agents365-ai/365-skills -g`
- OpenSpec 项目（`openspec/changes/`）

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/position.py` | 追踪 change 的 processed/skipped 状态 |
| `scripts/append_readme.py` | 向 README.md 需求时间线追加文章链接 |

## License

MIT
