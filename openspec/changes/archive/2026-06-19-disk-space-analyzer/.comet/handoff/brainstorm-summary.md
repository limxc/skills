# Brainstorm Summary

- Change: disk-space-analyzer
- Date: 2026-06-18

## 确认的技术方案

采用方案 B：多模块 Python（scanner + categorizer + formatter），`__main__.py` 作为 CLI 入口编排流程。

### scanner.py

```python
import os

def scan(root_path, max_depth=5, min_size=1_000_000_000):
    """递归扫描目录树，返回 FolderNode 列表。
    
    规则：
    - 使用 os.scandir() 替代 os.walk() 提升性能
    - 文件夹 > min_size(1GB) 才递归，最多 max_depth(5) 层
    - 跳过系统目录（Windows, Program Files, Program Files (x86), System32, $Recycle.Bin）
    - 权限不足时跳过并记录，不中断扫描
    - 默认 30s 超时截断
    """
    ...
```

### categorizer.py

```python
CATEGORY_RULES = [
    (r'(node_modules|\.npm|\.yarn|\.pnpm)', 'dependency-cache', 'safe'),
    (r'(Temp|tmp|cache)', 'temporary-files', 'safe'),
    (r'Downloads', 'downloads', 'review'),
    (r'(dist|build|out|__pycache__|\.next|\.nuxt)', 'code-build', 'cautious'),
    (r'(bin|obj|\.vs)', 'code-build', 'cautious'),
    (r'(Desktop|Documents|Pictures|Music|Videos)', 'user-data', 'review'),
    (r'(AppData/Local/Google|AppData/Local/Microsoft/Edge)', 'browser-cache', 'safe'),
    ...
]
```

### formatter.py

输出树状结构：

```
Scanned: C:\Users\TestUser | Total: 85.3 GB | Folders >1GB: 12 | Duration: 3.2s
─────────────────────────────────────────────────────
  Folder                         Size     Category         Action
  ────────────────────────────────────────────────────────────────
  ├── AppData                    32.1 GB  user-data         🔍 review
  │   ├── Local\Temp             4.2 GB   temporary-files   ✅ safe
  │   └── Local\Google\Cache     1.8 GB   browser-cache     ✅ safe
  ├── Projects                   28.5 GB  code-build        ⚠️ cautious
  │   ├── project-a\node_modules 2.1 GB   dependency-cache  ✅ safe [TOP]
  │   └── project-b\dist         1.5 GB   code-build        ⚠️ cautious
  └── Downloads                  15.2 GB  downloads          🔍 review
```

## 关键取舍与风险

- **os.scandir 优先**：一次系统调用拿到类型+属性，比 os.walk 快 2-10 倍
- **实时进度**：`print(msg, file=sys.stderr, flush=True)` 逐层/逐大文件夹推送进度，agent 捕获并展示
- **用户按需停止**：先扫顶层（快），再逐个深入大文件夹；用户喊停后 agent kill 进程，用已收集结果输出报告
- **纯标准库**：零外部依赖，免安装
- **跳过 vs 报错**：权限不足静默跳过，在汇总中报告跳过的目录数

## 测试策略

- `scanner.py`：mock 目录结构，验证递归深度、大小计算、系统目录跳过、权限错误处理
- `categorizer.py`：各类路径 pattern 匹配测试 + unknown 回退
- `formatter.py`：验证输出格式、排序、树状缩进

## Spec Patch

无
