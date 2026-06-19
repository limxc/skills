---
comet_change: disk-space-analyzer
role: technical-design
canonical_spec: openspec
---

# Disk Analyser Skill — 技术设计文档

## 1. 架构概述

```
disk-analyser-skill/
├── SKILL.md
├── scripts/
│   ├── __init__.py
│   ├── __main__.py     # CLI 入口
│   ├── scanner.py      # 目录扫描
│   ├── categorizer.py  # 内容分类
│   └── formatter.py    # 输出格式化
└── references/
```

## 2. 数据流

```
User: "/disk-space-analyzer C:\"
  │
  ▼
__main__.py (argparse 解析路径)
  │
  ▼
scanner.scan(path) ──→ list[FolderNode]
  │                     每个节点: {path, size, children, skipped}
  │                     stderr: [PROGRESS] 逐文件夹推送
  ▼
categorizer.classify(nodes) ──→ list[FolderNode]
  │                             每个节点增加: category, recommendation
  ▼
formatter.format(nodes) ──→ str (树状表格)
  │
  ▼
stdout ← print() ← agent 捕获展示
```

## 3. 模块详述

### scanner.py

```python
class FolderNode:
    path: str
    size: int         # bytes
    children: list[FolderNode]
    skipped: list[str]  # 权限不足被跳过的路径

def scan(root: str, max_depth=5, min_size=1_000_000_000, progress=None) -> FolderNode
```

核心逻辑：
- `os.scandir()` 逐层遍历，不走 `os.walk()`
- 先扫顶层获取全部一级目录
- 对 >1GB 的目录递归，深度 ≤5 层
- 系统目录跳过（Windows, Program Files, Program Files (x86), System32, $Recycle.Bin）
- 权限不足 → 记录到 `skipped`，继续同级其他目录
- `progress` 回调每进入一个大文件夹触发一次: `progress(path, size_hint)`

### categorizer.py

```python
CATEGORIES = [
    (re.compile(r'(node_modules|\.npm|\.yarn|\.pnpm|bower_components)'), 
     'dependency-cache', Recommendation.SAFE),
    (re.compile(r'(Temp|tmp|cache)', re.I), 
     'temporary-files', Recommendation.SAFE),
    (re.compile(r'(__pycache__|\.pyc)'), 
     'code-build', Recommendation.CAUTIOUS),
    (re.compile(r'(bin|obj|\.vs)', re.I), 
     'code-build', Recommendation.CAUTIOUS),
    (re.compile(r'(dist|build|out|target|\.next|\.nuxt)', re.I), 
     'code-build', Recommendation.CAUTIOUS),
    (re.compile(r'Downloads', re.I), 
     'downloads', Recommendation.REVIEW),
    (re.compile(r'(Desktop|Documents|Pictures|Music|Videos)', re.I), 
     'user-data', Recommendation.REVIEW),
    (re.compile(r'(AppData\\Local\\Google|AppData\\Local\\Microsoft\\Edge|\.cache)', re.I), 
     'browser-cache', Recommendation.SAFE),
    (re.compile(r'Logs?', re.I), 
     'logs', Recommendation.CAUTIOUS),
    (re.compile(r'(\.git|\.svn|\.hg)'), 
     'vcs-data', Recommendation.CAUTIOUS),
]

class Recommendation(Enum):
    SAFE = "✅ safe-to-clean"
    CAUTIOUS = "⚠️ cautious"
    REVIEW = "🔍 review-manually"

def classify(node: FolderNode) -> FolderNode
def _match_category(name: str) -> tuple[str, Recommendation]
```

### formatter.py

```python
def format_report(root: FolderNode, duration: float) -> str
```

输出格式：

```
Scanned: C:\Users\TestUser | Total: 85.3 GB | Skipped: 2 paths | Duration: 3.2s
──────────────────────────────────────────────────────────────────────────
  Folder                         Size         Category              Action
  ──────────────────────────────────────────────────────────────────────────
  ├── AppData                    32.1 GB      user-data              🔍 review
  │   ├── Local\Temp             4.2 GB       temporary-files        ✅ safe            [TOP]
  │   ├── Local\Google\Cache     1.8 GB       browser-cache          ✅ safe
  │   └── Local\Microsoft        skipped      (permission denied)
  ├── Projects                   28.5 GB      code-build             ⚠️ cautious        [TOP]
  │   ├── project-a\node_modules 2.1 GB       dependency-cache       ✅ safe            [TOP]
  │   └── project-b\dist         1.5 GB       code-build             ⚠️ cautious
  └── Downloads                  15.2 GB      downloads              🔍 review          [TOP]
```

规则：
- 同级按大小降序
- 前 5 名标注 `[TOP]`
- 树状缩进：`├──` / `└──`（每层缩进 4 空格）

### __main__.py

```python
import argparse, sys, time
from . import scanner, categorizer, formatter

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="Directory to scan")
    ap.add_argument("--min-size", type=int, default=1_000_000_000)
    ap.add_argument("--max-depth", type=int, default=5)
    args = ap.parse_args()

    def progress(path, size_hint):
        hint = formatter.format_size(size_hint) if size_hint else "?"
        print(f"[PROGRESS] Scanning: {path} ({hint})", file=sys.stderr, flush=True)

    start = time.time()
    root = scanner.scan(args.path, args.max_depth, args.min_size, progress)
    elapsed = time.time() - start

    categorizer.classify(root)
    print(formatter.format_report(root, elapsed))

if __name__ == "__main__":
    main()
```

## 4. 进度与停止协议

| 阶段 | 动作 | 用户可见 |
|------|------|----------|
| 顶层扫描 | `progress("Scanning top-level...", "?")` | 快速闪过 |
| 深入大文件夹 | `progress("Deep scanning: AppData", "32.1 GB")` | 逐条显示 |
| 用户说"停下" | Agent 发 SIGTERM / taskkill | 进程终止 |
| 输出已收集数据 | `formatter.format()` 使用已入队的 FolderNode | 显示部分结果 |

## 5. 错误处理

| 场景 | 处理 |
|------|------|
| 路径不存在 | `sys.exit("ERROR: Path not found")` |
| 权限不足 | 跳过，记录到 skipped 列表 |
| 扫描被用户终止 | 使用已收集的数据输出报告 |
| 路径是文件而非目录 | 警告后扫描其父目录 |
