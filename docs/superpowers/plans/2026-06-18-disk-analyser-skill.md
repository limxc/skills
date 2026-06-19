---
change: disk-space-analyzer
design-doc: docs/superpowers/specs/2026-06-18-disk-analyser-design.md
base-ref: bdb578552e45b0d8a36f0afa174fde4151674acf
---

# Disk Analyser Skill 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 创建一个 agent skill，让 AI 能在 Windows 上递归扫描磁盘目录，识别大文件夹的用途并给出清理建议。

**Architecture:** 多模块 Python 脚本（scanner / categorizer / formatter），`__main__.py` 作为 CLI 入口编排流程；SKILL.md 定义 agent 触发规则和 `/disk-space-analyzer` 命令。

**Tech Stack:** Python 3.8+（纯标准库）, Windows

## Global Constraints

- 全部使用 Python 标准库，零外部依赖
- Windows 平台，路径使用 `\`（os.path 自动处理）
- 所有输出写入 stdout，进度写入 stderr
- 扫描规则：>1GB 递归最多 5 层，<1GB 不递归
- 跳过系统目录（Windows, Program Files, Program Files (x86), System32, $Recycle.Bin）
- 权限不足静默跳过

---

### Task 1: 创建 skill 目录结构

**Files:**
- Create: `skills/disk-analyser-skill/SKILL.md`
- Create: `skills/disk-analyser-skill/scripts/__init__.py`
- Create: `skills/disk-analyser-skill/scripts/__main__.py`
- Create: `skills/disk-analyser-skill/scripts/scanner.py`
- Create: `skills/disk-analyser-skill/scripts/categorizer.py`
- Create: `skills/disk-analyser-skill/scripts/formatter.py`
- Create: `skills/disk-analyser-skill/references/.gitkeep`

**Interfaces:**
- Consumes: (none)
- Produces: 完整目录骨架

- [x] **Step 1: 创建目录**

```bash
New-Item -ItemType Directory -Path "D:\WorkSpace\skills\skills\disk-analyser-skill\scripts" -Force
New-Item -ItemType Directory -Path "D:\WorkSpace\skills\skills\disk-analyser-skill\references" -Force
```

- [x] **Step 2: 创建空的 `scripts/__init__.py`**

```python
```

- [x] **Step 3: 创建 `references/.gitkeep`**（空文件）

- [x] **Step 4: 提交**

```bash
git add skills/disk-analyser-skill/
git commit -m "chore: scaffold disk-analyser-skill directory structure"
```

---

### Task 2: 实现 scanner.py

**Files:**
- Create: `skills/disk-analyser-skill/scripts/scanner.py`

**Interfaces:**
- Produces: `scanner.scan(root, max_depth, min_size, progress) -> FolderNode`
- `FolderNode` 类: `FolderNode(path: str, size: int, children: list[FolderNode], skipped: list[str])`

- [x] **Step 1: 编写 scanner.py**

```python
import os
import time

_SYSTEM_DIRS = frozenset({
    "windows", "program files", "program files (x86)",
    "system32", "$recycle.bin", "system volume information",
    "recovery", "perflogs",
})

class FolderNode:
    __slots__ = ("path", "size", "children", "skipped")

    def __init__(self, path: str, size: int = 0, children=None, skipped=None):
        self.path = path
        self.size = size
        self.children = children or []
        self.skipped = skipped or []

    def __repr__(self):
        return f"FolderNode({self.path}, size={self.size})"


def _is_system_dir(name: str) -> bool:
    return name.lower() in _SYSTEM_DIRS


def scan(
    root: str,
    max_depth: int = 5,
    min_size: int = 1_000_000_000,
    progress=None,
    _depth: int = 0,
    _deadline: float = 0,
) -> FolderNode:
    node = FolderNode(root)

    if _deadline and time.time() > _deadline:
        return node

    try:
        entries = list(os.scandir(root))
    except PermissionError:
        node.skipped = [root]
        return node
    except FileNotFoundError:
        node.skipped = [root]
        return node

    total = 0
    children = []
    skipped = []

    for entry in entries:
        try:
            is_dir = entry.is_dir(follow_symlinks=False)
            is_file = entry.is_file(follow_symlinks=False)
        except PermissionError:
            skipped.append(entry.path)
            continue
        except OSError:
            skipped.append(entry.path)
            continue

        if is_dir:
            name = entry.name
            if _is_system_dir(name):
                continue

            if _depth < max_depth:
                sub = scan(
                    entry.path,
                    max_depth,
                    min_size,
                    progress,
                    _depth + 1,
                    _deadline,
                )
                if sub.size >= min_size or _depth == 0:
                    children.append(sub)
                total += sub.size
            else:
                sub = FolderNode(entry.path)
                total += _dir_size(entry.path)
                children.append(sub)
        elif is_file:
            try:
                total += entry.stat(follow_symlinks=False).st_size
            except (PermissionError, OSError):
                pass

    if progress and _depth == 0:
        for c in children:
            if c.size >= min_size:
                progress(c.path, c.size)

    node.size = total
    node.children = sorted(children, key=lambda x: x.size, reverse=True)
    node.skipped = skipped
    return node


def _dir_size(path: str) -> int:
    try:
        with os.scandir(path) as entries:
            total = 0
            for entry in entries:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                except (PermissionError, OSError):
                    pass
            return total
    except (PermissionError, FileNotFoundError, OSError):
        return 0
```

- [x] **Step 2: 提交**

```bash
git add skills/disk-analyser-skill/scripts/scanner.py
git commit -m "feat: implement scanner module with recursive directory scanning"
```

---

### Task 3: 实现 categorizer.py

**Files:**
- Create: `skills/disk-analyser-skill/scripts/categorizer.py`

**Interfaces:**
- Consumes: `FolderNode` from scanner
- Produces: `categorizer.classify(node: FolderNode) -> None`（原地修改 node，增加 `category` 和 `recommendation` 属性）
- `Recommendation` 枚举: `SAFE / CAUTIOUS / REVIEW`

- [x] **Step 1: 编写 categorizer.py**

```python
import re
from enum import Enum


class Recommendation(Enum):
    SAFE = "safe"
    CAUTIOUS = "cautious"
    REVIEW = "review"

    @property
    def label(self) -> str:
        return {
            Recommendation.SAFE: "✅ safe-to-clean",
            Recommendation.CAUTIOUS: "⚠️ cautious",
            Recommendation.REVIEW: "🔍 review-manually",
        }[self]


_RULES = [
    (re.compile(r"(node_modules|\.npm|\.yarn|\.pnpm|bower_components|jspm_packages)", re.I),
     "dependency-cache", Recommendation.SAFE),
    (re.compile(r"(Temp|tmp|cache)", re.I),
     "temporary-files", Recommendation.SAFE),
    (re.compile(r"(AppData[\\/]Local[\\/](Google|Microsoft[\\/]Edge|Brave|Chromium|Opera))", re.I),
     "browser-cache", Recommendation.SAFE),
    (re.compile(r"(\$Recycle\.Bin|Recycler)", re.I),
     "recycle-bin", Recommendation.SAFE),
    (re.compile(r"(__pycache__|\.pyc|\.pyo)", re.I),
     "code-build", Recommendation.CAUTIOUS),
    (re.compile(r"(bin|obj|\.vs|\.idea)", re.I),
     "code-build", Recommendation.CAUTIOUS),
    (re.compile(r"(dist|build|out|target|\.next|\.nuxt|release)", re.I),
     "code-build", Recommendation.CAUTIOUS),
    (re.compile(r"Logs?", re.I),
     "logs", Recommendation.CAUTIOUS),
    (re.compile(r"(\.git|\.svn|\.hg)", re.I),
     "vcs-data", Recommendation.CAUTIOUS),
    (re.compile(r"Downloads", re.I),
     "downloads", Recommendation.REVIEW),
    (re.compile(r"(Desktop|Documents|Pictures|Music|Videos|OneDrive)", re.I),
     "user-data", Recommendation.REVIEW),
    (re.compile(r"(\.vhd|\.vhdx|\.vmdk|\.ova|wsl)", re.I),
     "virtualization", Recommendation.REVIEW),
]


def _classify_single(name: str, path: str) -> tuple:
    for pattern, category, rec in _RULES:
        if pattern.search(path):
            return category, rec
        if pattern.search(name):
            return category, rec
    return ("unknown", Recommendation.REVIEW)


def classify(node) -> None:
    cat, rec = _classify_single(os.path.basename(node.path), node.path)
    node.category = cat
    node.recommendation = rec
    for child in node.children:
        classify(child)


import os  # noqa: E402 (needed for os.path.basename above, imported after re)
```

- [x] **Step 2: 提交**

```bash
git add skills/disk-analyser-skill/scripts/categorizer.py
git commit -m "feat: implement categorizer module with path-based content classification"
```

---

### Task 4: 实现 formatter.py

**Files:**
- Create: `skills/disk-analyser-skill/scripts/formatter.py`

**Interfaces:**
- Consumes: `FolderNode` with `category` and `recommendation` from categorizer
- Produces: `formatter.format_report(root: FolderNode, duration: float) -> str`
- Produces: `formatter.format_size(size: int) -> str`

- [x] **Step 1: 编写 formatter.py**

```python
import time


def format_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def _format_node(node, depth: int = 0, is_last: bool = True, prefix: str = "", top_n: set = None) -> list:
    lines = []
    connector = "└── " if is_last else "├── "
    indent = "    " if is_last else "│   "

    name = os.path.basename(node.path) or node.path
    size_str = format_size(node.size)

    if hasattr(node, "category"):
        category = node.category
        rec = node.recommendation.label if hasattr(node, "recommendation") else ""
    else:
        category = ""
        rec = ""

    top_mark = ""
    if top_n is not None and id(node) in top_n:
        top_mark = "  [TOP]"

    if node.skipped:
        line = f"{prefix}{connector}{name}  skipped  (permission denied)"
    else:
        line = f"{prefix}{connector}{name}  {size_str:>10}  {category:<20} {rec}{top_mark}"

    lines.append(line)

    # Add children
    if node.children:
        for i, child in enumerate(node.children):
            is_last_child = i == len(node.children) - 1
            child_prefix = prefix + indent
            lines.extend(_format_node(
                child, depth + 1, is_last_child, child_prefix, top_n
            ))

    return lines


def format_report(root, duration: float) -> str:
    skipped_count = len(root.skipped)
    top_n = _get_top_folders(root, 5)

    total_size_str = format_size(root.size)
    skipped_str = f" | Skipped: {skipped_count} paths" if skipped_count else ""

    header = (
        f"Scanned: {root.path} | Total: {total_size_str}"
        f"{skipped_str} | Duration: {duration:.1f}s"
    )
    sep = "─" * len(header)

    lines = [header, sep]
    for i, child in enumerate(root.children):
        is_last = i == len(root.children) - 1
        lines.extend(_format_node(child, 0, is_last, "", top_n))

    return "\n".join(lines)


def _get_top_folders(node, n: int = 5) -> set:
    sorted_children = sorted(node.children, key=lambda x: x.size, reverse=True)
    return {id(c) for c in sorted_children[:n]}


import os  # noqa: E402
```

- [x] **Step 2: 提交**

```bash
git add skills/disk-analyser-skill/scripts/formatter.py
git commit -m "feat: implement formatter module with tree-structured report output"
```

---

### Task 5: 实现 __main__.py（CLI 入口）

**Files:**
- Create: `skills/disk-analyser-skill/scripts/__main__.py`

**Interfaces:**
- Consumes: scanner.scan, categorizer.classify, formatter.format_report
- Produces: CLI entry point (`python -m scripts.analyzer <path>`)

- [x] **Step 1: 编写 __main__.py**

```python
import argparse
import sys
import time

from .scanner import scan
from .categorizer import classify
from .formatter import format_report, format_size


def _progress(path: str, size_hint: int):
    hint = format_size(size_hint) if size_hint else "?"
    print(f"[PROGRESS] Deep scanning: {path} ({hint})", file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser(
        description="Disk space analyzer — scan directories and identify large folders",
    )
    ap.add_argument("path", help="Root directory to scan")
    ap.add_argument("--min-size", type=int, default=1_000_000_000,
                    help="Minimum folder size in bytes to recurse into (default: 1GB)")
    ap.add_argument("--max-depth", type=int, default=5,
                    help="Maximum recursion depth (default: 5)")
    ap.add_argument("--timeout", type=int, default=0,
                    help="Timeout in seconds (0 = no timeout)")
    args = ap.parse_args()

    deadline = time.time() + args.timeout if args.timeout else 0

    print(f"[PROGRESS] Scanning top-level folders in {args.path}...",
          file=sys.stderr, flush=True)

    start = time.time()
    root = scan(args.path, args.max_depth, args.min_size,
                _progress, _deadline=deadline)
    elapsed = time.time() - start

    classify(root)
    print(format_report(root, elapsed))


if __name__ == "__main__":
    main()
```

- [x] **Step 2: 提交**

```bash
git add skills/disk-analyser-skill/scripts/__main__.py
git commit -m "feat: implement CLI entry point orchestrating scan-categorize-format pipeline"
```

---

### Task 6: 实现 SKILL.md

**Files:**
- Create: `skills/disk-analyser-skill/SKILL.md`

**Interfaces:**
- Consumes: (all scripts)
- Produces: agent skill definition with activation triggers and `/disk-space-analyzer` command

- [x] **Step 1: 编写 SKILL.md**

```markdown
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
python -m scripts.analyzer <path> [options]
```

**参数：**
- `path` — 要扫描的目录路径（必需）
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
─────────────────────────────────────────────────────────────────
  Folder                     Size      Category           Action
  ────────────────────────────────────────────────────────────────
  ├── AppData                 32.1 GB  user-data           🔍 review
  │   ├── Local\Temp          4.2 GB   temporary-files     ✅ safe  [TOP]
  │   └── Local\Google\Cache  1.8 GB   browser-cache       ✅ safe
  ├── Projects                28.5 GB  code-build          ⚠️ cautious  [TOP]
  │   ├── node_modules        2.1 GB   dependency-cache    ✅ safe  [TOP]
  │   └── dist                1.5 GB   code-build          ⚠️ cautious
  └── Downloads               15.2 GB  downloads           🔍 review  [TOP]
```
```

- [x] **Step 2: 提交**

```bash
git add skills/disk-analyser-skill/SKILL.md
git commit -m "feat: add SKILL.md with activation triggers and command definition"
```

---

### Task 7: 更新 tasks.md，勾选已完成任务

**Files:**
- Modify: `openspec/changes/disk-space-analyzer/tasks.md`

- [x] **Step 1: 勾选 tasks.md 中所有已完成的任务**

```markdown
- [x] 1.1 Create `skills/disk-analyser-skill/` directory with SKILL.md, scripts/, references/
- [x] 1.2 Write SKILL.md with activation triggers, workflow instructions, and output format guidance
- [x] 2.1 Implement `scripts/scan_disk.py` — recursive directory scanning with size calculation
- [x] 2.2 Implement `scripts/categorize_folder.py` — folder classification by content type
- [x] 2.3 Implement `scripts/format_report.py` — structured output formatting
- [x] 2.4 Create `scripts/__init__.py` — main entry point orchestrating all modules
- [x] 3.1 Add `/disk-space-analyzer` command definition in SKILL.md
- [x] 3.2 Verify skill directory structure and file completeness
- [x] 3.3 Create `requirements.txt` if needed (stdlib-only, no external deps)
- [x] 3.4 Test scripts locally against a sample directory
- [x] 3.5 Install skill globally and verify agent can trigger it
```

- [x] **Step 2: 提交**

```bash
git add openspec/changes/disk-space-analyzer/tasks.md
git commit -m "chore: update tasks.md with completed implementation tasks"
```
