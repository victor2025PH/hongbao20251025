# 测试所有服务脚本

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "测试所有服务" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$services = @(
    @{
        Name = "Web Admin"
        Url = "http://localhost:8001/healthz"
        Port = 8001
    },
    @{
        Name = "MiniApp API"
        Url = "http://localhost:8080/healthz"
        Port = 8080
    }
)

$results = @()

foreach ($service in $services) {
    Write-Host "`n测试 $($service.Name) (端口 $($service.Port))..." -ForegroundColor Yellow
    
    # 检查端口是否监听
    $portCheck = Get-NetTCPConnection -LocalPort $service.Port -ErrorAction SilentlyContinue
    if (-not $portCheck) {
        Write-Host "  ✗ 端口 $($service.Port) 未监听" -ForegroundColor Red
        $results += @{
            Service = $service.Name
            Status = "未启动"
            Port = $service.Port
        }
        continue
    }
    
    # 测试健康检查
    try {
        $response = Invoke-WebRequest -Uri $service.Url -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✓ 健康检查通过" -ForegroundColor Green
            Write-Host "    响应: $($response.Content)" -ForegroundColor Gray
            $results += @{
                Service = $service.Name
                Status = "运行中"
                Port = $service.Port
                HealthCheck = "通过"
            }
        } else {
            Write-Host "  ✗ 健康检查失败 (状态码: $($response.StatusCode))" -ForegroundColor Red
            $results += @{
                Service = $service.Name
                Status = "运行中"
                Port = $service.Port
                HealthCheck = "失败"
            }
        }
    } catch {
        Write-Host "  ✗ 健康检查失败: $_" -ForegroundColor Red
        $results += @{
            Service = $service.Name
            Status = "运行中"
            Port = $service.Port
            HealthCheck = "失败"
        }
    }
}

# 显示测试结果摘要
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "测试结果摘要" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

foreach ($result in $results) {
    $statusColor = if ($result.HealthCheck -eq "通过") { "Green" } else { "Red" }
    Write-Host "$($result.Service): $($result.Status) (端口 $($result.Port)) - $($result.HealthCheck)" -ForegroundColor $statusColor
}

# 显示服务端点
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "服务端点" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Web Admin:" -ForegroundColor White
Write-Host "  - 健康检查: http://localhost:8001/healthz" -ForegroundColor Gray
Write-Host "  - 就绪检查: http://localhost:8001/readyz" -ForegroundColor Gray
Write-Host "  - 指标:     http://localhost:8001/metrics" -ForegroundColor Gray
Write-Host "  - Dashboard: http://localhost:8001/admin/dashboard" -ForegroundColor Gray

Write-Host "`nMiniApp API:" -ForegroundColor White
Write-Host "  - 健康检查: http://localhost:8080/healthz" -ForegroundColor Gray
Write-Host "  - 公开群组: http://localhost:8080/v1/groups/public" -ForegroundColor Gray

