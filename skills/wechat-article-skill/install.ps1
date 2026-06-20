param(
    [string]$Platform = ""
)

$SkillName = "wechat-article-skill"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Installing $SkillName..." -ForegroundColor Green

# Detect platform
function Detect-Platform {
    if (Test-Path "$env:USERPROFILE\.claude\skills") { return "claude" }
    if (Test-Path "$env:USERPROFILE\.copilot\skills") { return "copilot" }
    if (Test-Path "$env:USERPROFILE\.gemini\skills") { return "gemini" }
    if (Test-Path "$env:USERPROFILE\.config\opencode\skills") { return "opencode" }
    if (Test-Path "$env:USERPROFILE\.agents") { return "universal" }
    # Check if in a git repo (project-level install)
    if (Test-Path ".git") { return "project" }
    return "unknown"
}

if (-not $Platform) {
    $Platform = Detect-Platform
}

$Target = switch ($Platform) {
    "claude"    { "$env:USERPROFILE\.claude\skills\$SkillName" }
    "copilot"   { "$env:USERPROFILE\.copilot\skills\$SkillName" }
    "gemini"    { "$env:USERPROFILE\.gemini\skills\$SkillName" }
    "opencode"  { "$env:USERPROFILE\.config\opencode\skills\$SkillName" }
    "universal" { "$env:USERPROFILE\.agents\skills\$SkillName" }
    "project"   { "$PWD\skills\$SkillName" }
    default     { $null }
}

if (-not $Target) {
    Write-Host "Unknown platform: $Platform" -ForegroundColor Red
    Write-Host "Usage: .\install.ps1 [-Platform claude|copilot|gemini|opencode|universal|project]"
    Write-Host ""
    Write-Host "Detected options:"
    if (Test-Path "$env:USERPROFILE\.claude\skills") { Write-Host "  - claude" }
    if (Test-Path "$env:USERPROFILE\.copilot\skills") { Write-Host "  - copilot" }
    if (Test-Path "$env:USERPROFILE\.gemini\skills") { Write-Host "  - gemini" }
    if (Test-Path "$env:USERPROFILE\.config\opencode\skills") { Write-Host "  - opencode" }
    if (Test-Path "$env:USERPROFILE\.agents") { Write-Host "  - universal" }
    exit 1
}

# Create target and copy files
New-Item -ItemType Directory -Path $Target -Force | Out-Null
Get-ChildItem -Path "$ScriptDir\*" -Exclude "install.ps1" | Copy-Item -Destination $Target -Recurse -Force

Write-Host ""
Write-Host "Skill installed successfully at: $Target" -ForegroundColor Green

# Install drawio-skill dependency
Write-Host ""
Write-Host "Installing drawio-skill dependency..." -ForegroundColor Yellow
npx skills add Agents365-ai/365-skills -g 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Failed to install drawio-skill. Install manually:" -ForegroundColor Yellow
    Write-Host "  npx skills add Agents365-ai/365-skills -g" -ForegroundColor Yellow
}

# Check draw.io CLI
$drawioCheck = Get-Command drawio -ErrorAction SilentlyContinue
if (-not $drawioCheck) {
    Write-Host "Warning: draw.io CLI not found. Diagram generation requires draw.io Desktop CLI." -ForegroundColor Yellow
    Write-Host "  Download from: https://github.com/jgraph/drawio-desktop/releases" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "To use it, type: /wechat-article" -ForegroundColor Cyan
