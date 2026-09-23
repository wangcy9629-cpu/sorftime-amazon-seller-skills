# 安装 Sorftime Amazon Seller Skills 到本机 AI 工具（Windows）
# 用法：powershell -ExecutionPolicy Bypass -File install.ps1

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsDir = Join-Path $Root "skills"

if (-not (Test-Path $SkillsDir)) {
    Write-Host "找不到 skills/ 目录，请在仓库根目录运行本脚本。" -ForegroundColor Red
    exit 1
}

$count = (Get-ChildItem -Path $SkillsDir -Directory).Count
$found = 0

function Install-To {
    param([string]$Target, [string]$Label)
    $parent = Split-Path -Parent $Target
    if (Test-Path $parent) {
        if (-not (Test-Path $Target)) { New-Item -ItemType Directory -Path $Target -Force | Out-Null }
        Copy-Item -Path (Join-Path $SkillsDir "*") -Destination $Target -Recurse -Force
        Write-Host "  $Label  ->  $Target  ($count 个技能)" -ForegroundColor Green
        $script:found = 1
    }
}

Write-Host "开始安装 Sorftime Amazon Seller Skills ..."
Write-Host ""

Install-To -Target (Join-Path $HOME ".workbuddy\skills") -Label "WorkBuddy"
Install-To -Target (Join-Path $HOME ".claude\skills")    -Label "Claude Code"
Install-To -Target (Join-Path $HOME ".codex\skills")     -Label "Codex"

if ($found -eq 0) {
    Write-Host "  没检测到已安装的 AI 工具目录。" -ForegroundColor Yellow
    Write-Host "  请手动把 skills\ 下的目录复制到你的 skills 路径。"
}

Write-Host ""
Write-Host "----------------------------------------"
Write-Host "下一步：配置 Sorftime 数据通道"
Write-Host ""
Write-Host "  npm install -g sorftime-cli"
Write-Host "  sorftime add myprofile <你的 Account-SK>"
Write-Host "  sorftime use myprofile"
Write-Host ""
Write-Host "没有账号？专属通道注册（含 7 天免费试用）："
Write-Host "  https://open.sorftime.com/home?tag=ODY2OA~~   优惠码：8668"
Write-Host "----------------------------------------"
