## Why

wechat-article-skill 的 position.py 目前只扫描 `openspec/changes/archive/` 下的已归档 changes，无法找到仍在活跃中的 changes。这限制了技能的适用范围——用户可能在 change 未归档时就希望生成文章。

## What Changes

- `position.py` 中 `find_archives()` 改为扫描 `openspec/changes/` 下所有子目录（含非 archive 的活跃 change），同时保留对 `openspec/changes/archive/` 的扫描
- 更新 CLI 帮助文本和变量名以反映"changes"而非仅"archives"
- 不涉及 API 变动，不新增 capability

## Capabilities

无新增 capability。仅修改已有脚本的内部行为。

## Impact

仅影响 `position.py` 文件。对外 CLI 接口不变。
