## Change

fix-disk-analyzer-slots-encoding

## Background

Bug fix for `disk-analyser-skill` 分析报错：`FolderNode.__slots__` 缺少字段 + 非法代理对 + GBK 兼容问题。

## Fix Plan

### 修复 1：scanner.py — `__slots__` 补齐

在 `FolderNode.__slots__` 元组末尾添加 `"category"` 和 `"recommendation"`。

### 修复 2：categorizer.py — 非法代理对转义

`Recommendation.REVIEW` 的 `\ud83d\udd0d`（Python 3 非法 lone surrogate）替换为正确 4 字节转义 `\U0001F50D`。

### 修复 3：__main__.py — GBK 编码兼容

在 `main()` 入口添加 `sys.stdout.reconfigure(encoding='utf-8')` 和 `sys.stderr.reconfigure(encoding='utf-8')`，确保 GBK 控制台下 Unicode 输出不抛异常。
