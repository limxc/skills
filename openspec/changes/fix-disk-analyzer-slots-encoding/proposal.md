## Why

调用 `disk-analyser-skill` 的 `disk-space-analyzer` 进行分析时，因 `FolderNode.__slots__` 缺少 `category` 和 `recommendation`，`categorizer.classify()` 在赋值 `node.category`/`node.recommendation` 时抛出 `AttributeError`。同时 `categorizer.py` 使用了 Python 中非法的代理对 Unicode 转义 `\ud83d\udd0d`，导致模块导入即报 `SyntaxError`。此外，`formatter.py` 和 `__main__.py` 使用了部分 GBK 编码无法表示的 Unicode 字符（如 emoji、em dash），在中英文 Windows 系统下可能输出 `UnicodeEncodeError`。

## What Changes

- `FolderNode.__slots__` 增加 `category` 和 `recommendation`
- 修复 `categorizer.py` 中非法代理对转义 `\ud83d\udd0d` → 合法 `\U0001F50D`
- 在 `__main__.py` 入口处设置 stdout/stderr 编码为 UTF-8，确保 GBK 终端能安全输出
- 或在 `formatter.py` 中对输出字符做 GBK 兼容处理

## Capabilities

### New Capabilities
（无新增 capability）

### Modified Capabilities
（spec 未改变，无需 delta spec）

## Impact

涉及 `scripts/scanner.py`、`scripts/categorizer.py`、`scripts/formatter.py`、`scripts/__main__.py`。均为修复性修改，不改变外部行为。
