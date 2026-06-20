## Context

`position.py` 的 `find_archives()` 函数只扫描 `openspec/changes/archive/`，遗漏了活跃 change（如 `openspec/changes/hqms-system-architecture-design/`）。

## Goals / Non-Goals

**Goals:**
- `find_archives()`（或更名后）应返回 `openspec/changes/` 下所有子目录中的 change（含 archive/ 内的）

**Non-Goals:**
- 不改动 CLI 命令名称（`list`/`pending`/`status`/`set`/`reset` 保持兼容）
- 不改动其他脚本或 SKILL.md

## Decisions

- 将 `find_archives()` 扫描路径从 `openspec/changes/archive/` 改为扫描 `openspec/changes/` 下所有子目录（排除 `archive` 自身不做为一个 change），同时扫描 `archive/` 内的子目录
- 保留向后兼容：返回数据格式不变

## Risks / Trade-offs

- 活跃 change 的内容可能未完成（如缺少 design.md），技能调用方需自行处理缺失字段
