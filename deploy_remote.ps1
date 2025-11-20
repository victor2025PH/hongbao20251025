# 远程部署脚本 - PowerShell 版本
# 使用方法: .\deploy_remote.ps1

$ErrorActionPreference = "Stop"

# 设置环境变量
$env:DEPLOY_HOST = "165.154.233.55"
$env:DEPLOY_USER = "ubuntu"
$env:DEPLOY_PATH = "/opt/redpacket"
$env:DEPLOY_BRANCH = "master"

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "🚀 开始远程自动部署测试" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "部署配置:" -ForegroundColor Green
Write-Host "  服务器: $($env:DEPLOY_USER)@$($env:DEPLOY_HOST)" -ForegroundColor White
Write-Host "  项目目录: $($env:DEPLOY_PATH)" -ForegroundColor White
Write-Host "  分支: $($env:DEPLOY_BRANCH)" -ForegroundColor White
Write-Host "  时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host ""

# 检查 bash 是否存在
$bashPath = Get-Command bash -ErrorAction SilentlyContinue
if (-not $bashPath) {
    Write-Host "❌ 未找到 bash 命令" -ForegroundColor Red
    Write-Host ""
    Write-Host "请安装 Git for Windows 或使用 WSL" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "或者，您可以手动在 Git Bash 中执行以下命令:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "export DEPLOY_HOST=$($env:DEPLOY_HOST)" -ForegroundColor Gray
    Write-Host "export DEPLOY_USER=$($env:DEPLOY_USER)" -ForegroundColor Gray
    Write-Host "export DEPLOY_PATH=$($env:DEPLOY_PATH)" -ForegroundColor Gray
    Write-Host "export DEPLOY_BRANCH=$($env:DEPLOY_BRANCH)" -ForegroundColor Gray
    Write-Host "bash deploy/scripts/deploy_remote.sh" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "✅ 找到 bash: $($bashPath.Source)" -ForegroundColor Green
Write-Host ""

# 检查部署脚本是否存在
if (-not (Test-Path "deploy/scripts/deploy_remote.sh")) {
    Write-Host "❌ 部署脚本不存在: deploy/scripts/deploy_remote.sh" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 部署脚本存在: deploy/scripts/deploy_remote.sh" -ForegroundColor Green
Write-Host ""

# 执行部署脚本
Write-Host "开始执行部署..." -ForegroundColor Cyan
Write-Host ""

try {
    # 使用 bash 执行脚本
    & bash deploy/scripts/deploy_remote.sh
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "====================================" -ForegroundColor Green
        Write-Host "✅ 部署完成！" -ForegroundColor Green
        Write-Host "====================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "====================================" -ForegroundColor Red
        Write-Host "❌ 部署失败！退出代码: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "====================================" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host ""
    Write-Host "❌ 执行过程中出错: $_" -ForegroundColor Red
    exit 1
}

