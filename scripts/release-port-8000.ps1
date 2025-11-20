# PowerShell 脚本：释放端口 8001
# 用途：检查并停止占用端口 8001 的进程，解决 Docker 容器启动时的端口冲突
# 注意：项目端口已从 8000 更改为 8001

param(
    [switch]$Force = $false  # 是否强制停止，不询问用户确认
)

$ErrorActionPreference = "Continue"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "检查端口 8001 占用情况" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# 查找占用端口 8001 的进程
$portInfo = netstat -ano | Select-String -Pattern ":8001.*LISTENING"

if (-not $portInfo) {
    Write-Host "✅ 端口 8001 未被占用" -ForegroundColor Green
    exit 0
}

Write-Host "⚠️  发现端口 8001 被占用：" -ForegroundColor Yellow
$portInfo | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Yellow
}

# 提取进程 ID（PID）
$processIds = $portInfo | ForEach-Object {
    $line = $_.ToString()
    $parts = $line -split '\s+'
    $processId = $parts[-1]  # 最后一列是 PID
    
    # 验证 PID 是否为数字
    if ($processId -match '^\d+$') {
        [int]$processId
    } else {
        $null
    }
} | Where-Object { $_ -ne $null } | Select-Object -Unique

if (-not $processIds -or $processIds.Count -eq 0) {
    Write-Host "❌ 无法从 netstat 输出中提取有效的进程 ID" -ForegroundColor Red
    exit 1
}

# 显示占用端口的进程信息
Write-Host "`n发现的进程 ID：" -ForegroundColor Cyan
foreach ($processId in $processIds) {
    try {
        $process = Get-Process -Id $processId -ErrorAction Stop
        Write-Host "  PID $processId : $($process.ProcessName) ($($process.Path))" -ForegroundColor Yellow
    } catch {
        Write-Host "  PID $processId : 进程不存在或无法访问" -ForegroundColor Red
    }
}

# 询问用户确认（除非使用 -Force）
if (-not $Force) {
    $response = Read-Host "`n是否停止这些进程以释放端口 8001？(Y/N)"
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Host "已取消操作" -ForegroundColor Yellow
        exit 0
    }
}

# 停止进程
Write-Host "`n正在停止进程..." -ForegroundColor Cyan
$stoppedCount = 0
$failedCount = 0

foreach ($processId in $processIds) {
    try {
        $process = Get-Process -Id $processId -ErrorAction Stop
        Write-Host "  停止进程 PID $processId ($($process.ProcessName))..." -ForegroundColor Yellow
        
        Stop-Process -Id $processId -Force -ErrorAction Stop
        
        # 等待进程完全退出
        Start-Sleep -Seconds 2
        
        # 验证进程是否已停止
        $stillRunning = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($stillRunning) {
            Write-Host "    ⚠️  进程仍在运行，可能需要手动停止" -ForegroundColor Red
            $failedCount++
        } else {
            Write-Host "    ✅ 进程已停止" -ForegroundColor Green
            $stoppedCount++
        }
    } catch {
        Write-Host "    ❌ 停止进程失败: $($_.Exception.Message)" -ForegroundColor Red
        $failedCount++
    }
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "操作完成" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "成功停止: $stoppedCount 个进程" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "失败: $failedCount 个进程" -ForegroundColor Red
}

# 再次检查端口是否已释放
Write-Host "`n再次检查端口 8001..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
$portCheck = netstat -ano | Select-String -Pattern ":8001.*LISTENING"

if (-not $portCheck) {
    Write-Host "✅ 端口 8001 已成功释放" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  端口 8001 仍被占用，可能需要手动处理" -ForegroundColor Yellow
    exit 1
}

