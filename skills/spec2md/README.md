# spec2md

从 OpenSpec 变更归档生成 Markdown 文章。

## 功能

完成 Comet 工作流变更后，`/spec2md` 读取已归档的 change，使用写作人格生成总结文章（含 drawio 配图），经用户确认后输出到项目 `spec2md/` 目录。

## 使用

```
/spec2md
```

流程：
1. 检测依赖（openspec、drawio-skill、draw.io CLI）
2. 查找未处理的归档 change
3. 用户选择 change、标题、骨架、配图、写作人格
4. 写作人格 + drawio-skill 生成示意图
5. 写作 → 草案展示 → 直接对话修改 → 定稿
6. 输出到 `spec2md/{change-name}-{date}/`

## 输入交互

展示带编号的 change 清单，用户输入：
- **数字**（如 `1,3`）— 选中写进文章
- **s+数字**（如 `s2`）— 标记为"以后不再提示"
- 逗号分隔混输，如 `1,3,s2`
- 空输入退出

已标记为 processed 或 skipped 的 change 下次不再显示。

## 输出

生成的文件位于项目根目录的 `spec2md/{change-name}-{date}/` 文件夹。

## 依赖

- Python 3.8+
- draw.io Desktop CLI（`drawio --version`）
- Comet 工作流（用于产生 OpenSpec 归档 change）

## 外部 Skill 依赖

- [drawio-skill](https://github.com/Agents365-ai/365-skills) — 通过 draw.io CLI 导出生成示意图

安装：
```bash
npx skills add Agents365-ai/365-skills -g
```

## License

MIT
