# 启动所有服务脚本
# 用于测试所有服务

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "启动所有服务进行测试" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 检查 Python
Write-Host "`n[1/5] 检查 Python 环境..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Python 未安装或不在 PATH 中" -ForegroundColor Red
    exit 1
}

# 检查端口占用
Write-Host "`n[2/5] 检查端口占用..." -ForegroundColor Yellow
$ports = @(8001, 8080, 3001)
foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "警告: 端口 $port 已被占用" -ForegroundColor Yellow
    } else {
        Write-Host "端口 $port 可用" -ForegroundColor Green
    }
}

# 检查 .env 文件
Write-Host "`n[3/5] 检查环境配置..." -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host ".env 文件存在" -ForegroundColor Green
} else {
    Write-Host "警告: .env 文件不存在，将使用默认配置" -ForegroundColor Yellow
}

# 初始化数据库
Write-Host "`n[4/5] 初始化数据库..." -ForegroundColor Yellow
$initResult = python -c "from models.db import init_db; init_db()" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "数据库初始化成功" -ForegroundColor Green
} else {
    Write-Host "数据库初始化失败，但继续启动服务" -ForegroundColor Yellow
    Write-Host $initResult -ForegroundColor Yellow
}

# 启动服务
Write-Host "`n[5/5] 启动服务..." -ForegroundColor Yellow
Write-Host "`n注意: 服务将在后台启动，请使用以下命令查看日志:" -ForegroundColor Cyan
Write-Host "  - Web Admin: Get-Content web_admin.log -Wait" -ForegroundColor White
Write-Host "  - MiniApp API: Get-Content miniapp.log -Wait" -ForegroundColor White
Write-Host "  - Bot: Get-Content bot.log -Wait" -ForegroundColor White

# 启动 Web Admin (端口 8001)
Write-Host "`n启动 Web Admin (端口 8001)..." -ForegroundColor Cyan
Start-Process python -ArgumentList "-m", "uvicorn", "web_admin.main:app", "--host", "0.0.0.0", "--port", "8001" -RedirectStandardOutput "web_admin.log" -RedirectStandardError "web_admin_error.log" -WindowStyle Hidden

# 等待服务启动
Start-Sleep -Seconds 3

# 启动 MiniApp API (端口 8080)
Write-Host "启动 MiniApp API (端口 8080)..." -ForegroundColor Cyan
Start-Process python -ArgumentList "-m", "uvicorn", "miniapp.main:app", "--host", "0.0.0.0", "--port", "8080" -RedirectStandardOutput "miniapp.log" -RedirectStandardError "miniapp_error.log" -WindowStyle Hidden

# 等待服务启动
Start-Sleep -Seconds 3

# 测试健康检查
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "执行健康检查测试" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Start-Sleep -Seconds 5

# 测试 Web Admin
Write-Host "`n测试 Web Admin (http://localhost:8001/healthz)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/healthz" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Web Admin 健康检查通过" -ForegroundColor Green
        Write-Host "  响应: $($response.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Web Admin 健康检查失败: $_" -ForegroundColor Red
}

# 测试 MiniApp API
Write-Host "`n测试 MiniApp API (http://localhost:8080/healthz)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/healthz" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ MiniApp API 健康检查通过" -ForegroundColor Green
        Write-Host "  响应: $($response.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ MiniApp API 健康检查失败: $_" -ForegroundColor Red
}

# 显示服务状态
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "服务状态" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Web Admin:     http://localhost:8001" -ForegroundColor White
Write-Host "MiniApp API:   http://localhost:8080" -ForegroundColor White
Write-Host "`n健康检查端点:" -ForegroundColor Cyan
Write-Host "  - Web Admin:   http://localhost:8001/healthz" -ForegroundColor White
Write-Host "  - Web Admin:   http://localhost:8001/readyz" -ForegroundColor White
Write-Host "  - Web Admin:   http://localhost:8001/metrics" -ForegroundColor White
Write-Host "  - MiniApp API: http://localhost:8080/healthz" -ForegroundColor White

Write-Host "`n注意: Bot 服务需要 BOT_TOKEN 环境变量，请手动启动:" -ForegroundColor Yellow
Write-Host "  python app.py" -ForegroundColor White

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "启动完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

