---
comet_change: refine-spec2md-output
role: technical-design
canonical_spec: openspec
archived-with: 2026-06-21-refine-spec2md-output
status: archived
---

# Refine spec2md output and post-processing

## Context

spec2md 的 Step 4 后处理目前将生成的文章输出到 `docs/{change-name}-{date}/`，之后直接回复用户。项目 README.md 缺少对已生成文章的索引。输出目录 `docs/` 含义模糊，与 spec2md 无直接关联。此外，Step 3.3 的框架选择缺少跳过选项。

## 变更范围

### 1. 输出路径修改 (docs/ → spec2md/)

全文约 10 处 `docs/` 引用统一替换为 `spec2md/`，包括但不限于：
- Step 3 Input/Output 标注
- Step 3.2 配图输出目录
- Step 3.6 目录创建路径 `New-Item -ItemType Directory -Path "spec2md/{change-name}-{date}" -Force`
- Step 3.6 文件写入路径
- Step 4.4 回复中的路径显示

`{change-name}` 和 `{date}` 命名逻辑不变（第一个 change 目录名 + YYYY-MM-DD）。

### 2. Step 3.3 新增「不使用框架」选项

在写作框架选择的 question 工具中，除现有框架选项外，新增一个 `D) 不使用框架` 选项。选择后跳过框架注入，文章仅按骨架结构和 persona 风格组织。对应的 `references/frameworks.md` 中不读取。

### 3. Step 4 后处理重构

现有 Step 4 结构：

```
4.1 position.py processed
4.2 history.yaml 更新
4.3 回复用户
```

重构为：

```
4.1 position.py processed（不变）
4.2 history.yaml 更新（不变）
4.3 README 需求时间线追加（新增）
4.4 回复汇总（原 4.3 加强）
```

**Step 4.3 实现逻辑**（内嵌 PowerShell，不创建独立脚本）：

```powershell
$readmePath = Join-Path $projectRoot "README.md"
$linkEntry = "- [$title - $date](spec2md/$articleDir/article.md)"
$sectionHeader = "## 需求时间线"

if (-not (Test-Path $readmePath)) {
    "`n$sectionHeader`n`n$linkEntry" | Set-Content $readmePath
} else {
    $content = Get-Content $readmePath -Raw
    if ($content -match "$sectionHeader[\s\S]*?(?=\n## |\z)") {
        # Section exists, append after last entry
        $section = $matches[0]
        $newSection = "$section`n$linkEntry"
        $content = $content.Replace($section, $newSection)
        Set-Content $readmePath $content
    } else {
        # Section doesn't exist, create at end
        Add-Content $readmePath "`n$sectionHeader`n`n$linkEntry"
    }
}
```

**Step 4.4 回复汇总**（在原 4.3 基础上增加）：
- 最终标题：`{title}`
- 文章路径：`spec2md/{article-name}-{date}/article.md`（原 `docs/...`）
- 覆盖 N 个 changes：`{dir-1}`, `{dir-2}`
- 配图：N 张
- 写作人格：`{persona-name}`
- ✅ position 已更新
- ✅ history.yaml 已记录
- ✅ 需求时间线已追加
- 下次运行不再显示已 processed 的 changes

### 4. skill-creator 优化

最后阶段运行 skill-creator，分析 spec2md SKILL.md，审查优化建议后选择性应用。保持回退能力（git diff 可还原）。

## 风险

- `README.md` 文件不存在时的正确处理
- 多用户并发编辑 README.md 的冲突风险（低概率，忽略）
- skill-creator 的优化建议可能过于激进，需人工审核
