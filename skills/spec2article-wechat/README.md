# spec2article-wechat

从 Comet 开发归档生成微信公众号文章。

## 功能

完成 Comet 工作流变更后，`/spec2article-wechat` 读取已归档的 change，生成总结文章（含配图），经用户确认后发布到微信公众号草稿箱。

## 使用

```
/spec2article-wechat
```

流程：
1. 检测依赖（wewrite、drawio-skill、draw.io CLI）
2. 查找未处理的归档 change
3. 讨论标题、骨架、配图
4. drawio-skill 生成示意图
5. 委托 wewrite 完成写作、SEO、排版、发布

## 输入交互

展示带编号的 change 清单，用户输入：
- **数字**（如 `1,3`）— 选中写进文章
- **s+数字**（如 `s2`）— 标记为"以后不再提示"
- 逗号分隔混输，如 `1,3,s2`
- 空输入退出

已标记为 processed 或 skipped 的 change 下次不再显示。

## 输出

生成的文件位于项目根目录的 `spec2article-wechat-output/` 文件夹。

## 依赖

- Python 3.8+
- draw.io Desktop CLI（`drawio --version`）
- Comet 工作流（用于产生归档 change）
- 微信公众号 AppID 和 AppSecret（用于发布）

## 外部 Skill 依赖

- [wewrite](https://github.com/oaker-io/wewrite) — 写作、SEO、排版、发布管道
- [drawio-skill](https://github.com/Agents365-ai/365-skills) — 通过 draw.io CLI 导出生成示意图

安装：
```bash
npx skills add oaker-io/wewrite -g
npx skills add Agents365-ai/365-skills -g
```

## License

MIT
