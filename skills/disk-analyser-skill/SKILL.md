---
name: disk-analyser-skill
description: >-
  Analyzes Windows disk space usage by recursively scanning directories,
  identifying large folders, classifying their content types, and providing
  cleanup recommendations. Activates when users ask about disk space, storage
  analysis, large folders, or what's taking up space on their drives. Supports
  the /disk-space-analyzer command.
license: MIT
---

# /disk-space-analyzer — Windows 磁盘空间分析

分析指定目录的磁盘空间使用情况，以树状结构展示大文件夹及其用途分类和清理建议。

## 触发方式

- 用户输入 `/disk-space-analyzer <path>` 直接调用
- 用户自然语言描述磁盘相关问题自动触发，如：
  - "分析 C 盘空间"
  - "看看 D 盘什么占空间"
  - "找出大文件夹"
  - "我的磁盘空间不够了"

## 依赖

- **Python 3.8+** — 脚本运行环境
- Windows 操作系统
- 无需外部 Python 包

## 工作原理

脚本位于 `scripts/` 目录下，agent 自动调用：

```
python -m scripts <path> [options]
```

**参数：**
- `path` — 要扫描的目录路径（必须）
- `--min-size` — 递归最小大小，默认 1GB（字节）
- `--max-depth` — 最大递归深度，默认 5
- `--timeout` — 超时秒数，0 表示不超时

**扫描规则：**
- 使用 `os.scandir()` 高效遍历
- 文件夹 >1GB 才递归深入，最多 5 层
- 跳过系统目录（Windows, Program Files 等）
- 权限不足时跳过并报告
- 进度信息实时通过 stderr 输出，agent 捕获并展示

**分类与建议：**
- 基于路径和名称匹配识别文件夹用途
- 每个文件夹标注清理安全等级：
  - ✅ safe-to-clean — 可删除（临时文件、缓存）
  - ⚠️ cautious — 谨慎操作（构建产物、日志）
  - 🔍 review-manually — 需人工检查（下载、文档）

**用户停止：**
扫描过程中如果用户说"停下"或"够了"，agent 可以终止进程并使用已收集的数据输出报告。

## 输出示例

```
Scanned: C:\Users\TestUser | Total: 85.3 GB | Duration: 3.2s
─────────────────────────────────────────────────
├── AppData  32.1 GB  user-data           🔍 review-manually
│   ├── Local\Temp  4.2 GB   temporary-files     ✅ safe-to-clean  [TOP]
│   └── Local\Google\Cache  1.8 GB   browser-cache       ✅ safe-to-clean
├── Projects  28.5 GB  code-build          ⚠️ cautious  [TOP]
│   ├── node_modules  2.1 GB   dependency-cache    ✅ safe-to-clean  [TOP]
│   └── dist  1.5 GB   code-build          ⚠️ cautious
└── Downloads  15.2 GB  downloads           🔍 review-manually  [TOP]
```
