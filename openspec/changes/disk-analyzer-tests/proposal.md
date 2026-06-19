## Why

disk-space-analyzer 技能目前没有测试覆盖，无法保证扫描结果的正确性，特别是 TOP5 文件夹大小与 Windows 资源管理器的一致性。需要添加测试来验证核心功能。

## What Changes

- 为 scanner、categorizer、formatter 模块添加单元测试
- 添加集成测试，验证 `/disk-space-analyzer <path>` 命令从用户输入触发后成功返回结果
- 验证 TOP5 文件夹大小与 Windows 资源管理器查看一致

## Capabilities

### New Capabilities
- (无新 capability)

### Modified Capabilities
- (无 spec 级别变更)

## Impact

- 仅新增测试文件，不修改现有模块代码
- 新增 `scripts/tests/` 测试目录
