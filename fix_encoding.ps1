# 修复 PowerShell 编码问题
# 设置控制台编码为 UTF-8

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# 设置环境变量
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Write-Host "编码已设置为 UTF-8" -ForegroundColor Green
Write-Host "现在可以运行 Python 脚本，中文将正确显示" -ForegroundColor Green

