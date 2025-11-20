# 全自动测试启动脚本
# 自动安装、启动、测试、监控

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "全自动测试系统" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 步骤 1: 自动修复常见错误
Write-Host "[1/5] 自动修复常见错误..." -ForegroundColor Yellow
python auto_fix_common_errors.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 部分修复可能失败，但继续执行..." -ForegroundColor Yellow
}
Write-Host ""

# 步骤 2: 启动全自动测试
Write-Host "[2/5] 启动全自动测试系统..." -ForegroundColor Yellow
Write-Host "注意: 测试将在后台运行，服务会自动启动" -ForegroundColor Cyan
Write-Host ""

# 启动自动测试（后台）
$testJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python auto_test.py
}

Write-Host "测试任务已启动 (Job ID: $($testJob.Id))" -ForegroundColor Green
Write-Host ""

# 步骤 3: 等待服务启动
Write-Host "[3/5] 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# 步骤 4: 检查服务状态
Write-Host "[4/5] 检查服务状态..." -ForegroundColor Yellow
python test_services.py
Write-Host ""

# 步骤 5: 启动监控（可选）
Write-Host "[5/5] 启动服务监控..." -ForegroundColor Yellow
Write-Host ""
Write-Host "选择操作:" -ForegroundColor Cyan
Write-Host "  1. 启动实时监控 (监控日志和错误)" -ForegroundColor White
Write-Host "  2. 查看测试任务状态" -ForegroundColor White
Write-Host "  3. 退出" -ForegroundColor White
Write-Host ""
$choice = Read-Host "请选择 (1-3)"

switch ($choice) {
    "1" {
        Write-Host "启动实时监控..." -ForegroundColor Green
        python monitor_services.py -d 600
    }
    "2" {
        Write-Host "测试任务状态:" -ForegroundColor Green
        Receive-Job -Job $testJob -Keep
        Get-Job
    }
    "3" {
        Write-Host "退出" -ForegroundColor Yellow
    }
}

# 清理
Write-Host ""
Write-Host "提示: 要停止测试任务，运行: Stop-Job -Id $($testJob.Id)" -ForegroundColor Cyan
Write-Host "提示: 要查看测试结果，运行: Receive-Job -Id $($testJob.Id)" -ForegroundColor Cyan

