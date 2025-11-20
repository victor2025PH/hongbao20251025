# 手动启动服务脚本（用于调试）
# 设置编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "手动启动服务" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查端口
Write-Host "[1/4] 检查端口占用..." -ForegroundColor Yellow
$port8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
$port8080 = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

if ($port8001) {
    Write-Host "警告: 端口 8001 已被占用 (PID: $($port8001.OwningProcess))" -ForegroundColor Yellow
    $kill = Read-Host "是否停止占用进程? (y/n)"
    if ($kill -eq 'y') {
        Stop-Process -Id $port8001.OwningProcess -Force
        Write-Host "进程已停止" -ForegroundColor Green
    }
}

if ($port8080) {
    Write-Host "警告: 端口 8080 已被占用 (PID: $($port8080.OwningProcess))" -ForegroundColor Yellow
    $kill = Read-Host "是否停止占用进程? (y/n)"
    if ($kill -eq 'y') {
        Stop-Process -Id $port8080.OwningProcess -Force
        Write-Host "进程已停止" -ForegroundColor Green
    }
}
Write-Host ""

# 初始化数据库
Write-Host "[2/4] 初始化数据库..." -ForegroundColor Yellow
python -c "from models.db import init_db; init_db(); print('数据库初始化成功')"
Write-Host ""

# 启动服务
Write-Host "[3/4] 启动服务..." -ForegroundColor Yellow
Write-Host "注意: 服务将在新窗口中启动" -ForegroundColor Cyan
Write-Host ""

# 启动 Web Admin
Write-Host "启动 Web Admin (端口 8001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONIOENCODING='utf-8'; `$env:PYTHONUTF8='1'; python -m uvicorn web_admin.main:app --host 0.0.0.0 --port 8001 --reload"
Start-Sleep -Seconds 3

# 启动 MiniApp API
Write-Host "启动 MiniApp API (端口 8080)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONIOENCODING='utf-8'; `$env:PYTHONUTF8='1'; python -m uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --reload"
Start-Sleep -Seconds 3

# 等待服务启动
Write-Host "[4/4] 等待服务启动..." -ForegroundColor Yellow
Write-Host "等待 15 秒让服务完全启动..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# 测试服务
Write-Host ""
Write-Host "测试服务..." -ForegroundColor Yellow
python test_services.py

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "服务启动完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务端点:" -ForegroundColor Cyan
Write-Host "  Web Admin:   http://localhost:8001" -ForegroundColor White
Write-Host "  MiniApp API: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

