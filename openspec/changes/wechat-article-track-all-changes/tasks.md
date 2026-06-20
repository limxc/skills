## 1. 修改 position.py

- [x] 1.1 将 `find_archives()` 改为 `find_changes()`，扫描 `openspec/changes/` 下所有子目录（含 `archive/` 内的）
- [x] 1.2 更新内部变量名和 docstring 以反映"changes"而非"archives"
- [x] 1.3 验证修改后 `python position.py list` 和 `python position.py pending` 能正确列出 HQMS 中的 change
