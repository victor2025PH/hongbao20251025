# 全自动测试启动脚本（修复编码问题）
# 使用方法: powershell -ExecutionPolicy Bypass -File start_auto_test.ps1

# 设置编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# 设置 Python 环境变量
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# 设置 PowerShell 输出编码
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "全自动测试系统" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "编码已设置为 UTF-8" -ForegroundColor Green
Write-Host ""

# 运行自动修复
Write-Host "[1/3] 运行自动修复..." -ForegroundColor Yellow
python auto_fix_common_errors.py
Write-Host ""

# 运行全自动测试
Write-Host "[2/3] 启动全自动测试..." -ForegroundColor Yellow
Write-Host "注意: 测试将在后台运行，服务会自动启动" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 可以停止测试" -ForegroundColor Cyan
Write-Host ""

python auto_test.py

Write-Host ""
Write-Host "测试完成！" -ForegroundColor Green

