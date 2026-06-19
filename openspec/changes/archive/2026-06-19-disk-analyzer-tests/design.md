## 实现说明

### 单元测试

使用 Python 标准库 `unittest` 和 `unittest.mock`：
- `test_scanner.py` — 测试 scanner 的目录遍历、权限跳过、系统目录跳过、文件夹大小计算
- `test_categorizer.py` — 测试 classify 的分类逻辑和 Recommendation 映射
- `test_formatter.py` — 测试 format_report 输出格式，尤其是 `_get_top_folders` 的 TOP5 排序逻辑

### 集成测试

- 使用 `subprocess` 调用 `python -m scripts <path>` 验证命令行入口
- 通过 `disk_usage` 或直接对比已知大小的测试目录，验证 TOP5 大小与预期一致

### TOP5 验证方案

创建一个已知结构的临时目录，手动计算各文件夹大小，然后运行扫描验证 TOP5 结果一致。
