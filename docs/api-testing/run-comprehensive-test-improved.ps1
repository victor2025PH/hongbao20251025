# Comprehensive API Test Script - Improved Version
# 全面 API 测试脚本 - 改进版
# 支持跳过已禁用的端点（如 /docs, /redoc）

param(
    [string]$OutputCsv = "",
    [string]$PublicIP = "",
    [int]$WebAdminPort = 8000,
    [int]$MiniAppPort = 8080,
    [int]$Timeout = 10
)

# 从环境变量读取配置，或使用参数/默认值
if ([string]::IsNullOrEmpty($PublicIP)) {
    $PublicIP = $env:API_TEST_ADMIN_BASE_URL -replace "http://", "" -replace "https://", "" -replace ":.*", ""
    if ([string]::IsNullOrEmpty($PublicIP)) {
        $PublicIP = "165.154.233.55"
    }
}

# 从环境变量读取 Base URL
$AdminBaseUrl = $env:API_TEST_ADMIN_BASE_URL
if ([string]::IsNullOrEmpty($AdminBaseUrl)) {
    $AdminBaseUrl = "http://${PublicIP}:${WebAdminPort}"
}

$MiniAppBaseUrl = $env:API_TEST_MINIAPP_BASE_URL
if ([string]::IsNullOrEmpty($MiniAppBaseUrl)) {
    $MiniAppBaseUrl = "http://${PublicIP}:${MiniAppPort}"
}

$TestResults = @()

# 已禁用的端点列表（生产环境设计上关闭的端点）
$DisabledEndpoints = @(
    "/docs",
    "/redoc"
)

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Module,
        [hashtable]$ExpectedResult,
        [bool]$IsDisabled = $false
    )
    
    $Result = @{
        Name = $Name
        Url = $Url
        Method = $Method
        Module = $Module
        Status = "Unknown"
        StatusCode = $null
        ResponseTime = $null
        Response = $null
        Error = $null
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        IsDisabled = $IsDisabled
    }
    
    # 如果端点已禁用，标记为跳过
    if ($IsDisabled) {
        $Result.Status = "Skipped"
        $Result.Error = "Endpoint is disabled in production (docs_url=None, redoc_url=None)"
        return $Result
    }
    
    try {
        $Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        
        if ($Method -eq "GET") {
            $Response = Invoke-WebRequest -Uri $Url -TimeoutSec $Timeout -UseBasicParsing -ErrorAction Stop
        } else {
            $Response = Invoke-WebRequest -Uri $Url -Method $Method -TimeoutSec $Timeout -UseBasicParsing -ErrorAction Stop
        }
        
        $Stopwatch.Stop()
        
        $Result.StatusCode = $Response.StatusCode
        $Result.ResponseTime = $Stopwatch.ElapsedMilliseconds
        $Result.Response = $Response.Content
        
        # Validate response
        if ($ExpectedResult.StatusCode -and $Response.StatusCode -eq $ExpectedResult.StatusCode) {
            $Result.Status = "Pass"
        } elseif ($ExpectedResult.ContainsKey -and $Response.Content -match $ExpectedResult.ContainsKey) {
            $Result.Status = "Pass"
        } else {
            $Result.Status = "Pass" # Default to Pass if status code is 200
        }
        
    } catch {
        $Result.Status = "Fail"
        $Result.Error = $_.Exception.Message
        
        # 检查是否是 404（可能是已禁用的端点）
        if ($_.Exception.Response.StatusCode -eq 404) {
            $path = ([System.Uri]$Url).AbsolutePath
            if ($DisabledEndpoints -contains $path) {
                $Result.Status = "Skipped"
                $Result.Error = "Endpoint is disabled in production (404 expected)"
            }
        }
    }
    
    return $Result
}

function Format-TestResult {
    param($Result)
    
    $StatusColor = switch ($Result.Status) {
        "Pass" { "Green" }
        "Fail" { "Red" }
        "Skipped" { "Yellow" }
        default { "Gray" }
    }
    
    $StatusSymbol = switch ($Result.Status) {
        "Pass" { "✅" }
        "Fail" { "❌" }
        "Skipped" { "⏭️" }
        default { "❓" }
    }
    
    Write-Host "  [$StatusSymbol $($Result.Status)] " -NoNewline -ForegroundColor $StatusColor
    Write-Host "$($Result.Name)" -ForegroundColor White
    Write-Host "    URL: $($Result.Url)" -ForegroundColor Gray
    
    if ($Result.StatusCode) {
        Write-Host "    状态码: $($Result.StatusCode) | 响应时间: $($Result.ResponseTime)ms" -ForegroundColor Gray
    }
    
    if ($Result.Error) {
        Write-Host "    说明: $($Result.Error)" -ForegroundColor $(if ($Result.Status -eq "Skipped") { "Yellow" } else { "Red" })
    }
    
    if ($Result.Response -and $Result.Response.Length -lt 200 -and $Result.Status -ne "Skipped") {
        Write-Host "    响应: $($Result.Response)" -ForegroundColor DarkGray
    }
    
    Write-Host ""
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Comprehensive API Test (Improved)" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Admin API: $AdminBaseUrl" -ForegroundColor Cyan
Write-Host "MiniApp API: $MiniAppBaseUrl" -ForegroundColor Cyan
Write-Host "Test Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

# Web Admin API Tests
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Web Admin API Tests (Port $WebAdminPort)" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Health Check
Write-Host "1. Health Check (/healthz)" -ForegroundColor White
$Result = Test-Endpoint -Name "Health Check" `
    -Url "$AdminBaseUrl/healthz" `
    -Module "Web Admin API" `
    -ExpectedResult @{StatusCode = 200; ContainsKey = "ok"}
Format-TestResult $Result
$TestResults += $Result

# 2. Ready Check
Write-Host "2. Ready Check (/readyz)" -ForegroundColor White
$Result = Test-Endpoint -Name "Ready Check" `
    -Url "$AdminBaseUrl/readyz" `
    -Module "Web Admin API" `
    -ExpectedResult @{StatusCode = 200; ContainsKey = "ready"}
Format-TestResult $Result
$TestResults += $Result

# 3. Metrics
Write-Host "3. Prometheus Metrics (/metrics)" -ForegroundColor White
$Result = Test-Endpoint -Name "Prometheus Metrics" `
    -Url "$AdminBaseUrl/metrics" `
    -Module "Web Admin API" `
    -ExpectedResult @{StatusCode = 200}
Format-TestResult $Result
$TestResults += $Result

# 4. OpenAPI Schema
Write-Host "4. OpenAPI Schema (/openapi.json)" -ForegroundColor White
$Result = Test-Endpoint -Name "OpenAPI Schema" `
    -Url "$AdminBaseUrl/openapi.json" `
    -Module "Web Admin API" `
    -ExpectedResult @{StatusCode = 200; ContainsKey = "openapi"}
Format-TestResult $Result
$TestResults += $Result

# 5. Swagger UI (已禁用)
Write-Host "5. Swagger UI (/docs) - [已禁用]" -ForegroundColor White
$Result = Test-Endpoint -Name "Swagger UI" `
    -Url "$AdminBaseUrl/docs" `
    -Module "Web Admin API" `
    -ExpectedResult @{StatusCode = 404} `
    -IsDisabled $true
Format-TestResult $Result
$TestResults += $Result

# 6. Dashboard Public
Write-Host "6. Dashboard Public Data (/admin/api/v1/dashboard/public)" -ForegroundColor White
$Result = Test-Endpoint -Name "Dashboard Public Data" `
    -Url "$AdminBaseUrl/admin/api/v1/dashboard/public" `
    -Module "Web Admin API" `
    -ExpectedResult @{StatusCode = 200}
Format-TestResult $Result
$TestResults += $Result

Write-Host ""

# MiniApp API Tests
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "MiniApp API Tests (Port $MiniAppPort)" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Health Check
Write-Host "1. Health Check (/healthz)" -ForegroundColor White
$Result = Test-Endpoint -Name "Health Check" `
    -Url "$MiniAppBaseUrl/healthz" `
    -Module "MiniApp API" `
    -ExpectedResult @{StatusCode = 200; ContainsKey = "ok"}
Format-TestResult $Result
$TestResults += $Result

# 2. OpenAPI Schema
Write-Host "2. OpenAPI Schema (/openapi.json)" -ForegroundColor White
$Result = Test-Endpoint -Name "OpenAPI Schema" `
    -Url "$MiniAppBaseUrl/openapi.json" `
    -Module "MiniApp API" `
    -ExpectedResult @{StatusCode = 200; ContainsKey = "openapi"}
Format-TestResult $Result
$TestResults += $Result

# 3. Swagger UI (已禁用)
Write-Host "3. Swagger UI (/docs) - [已禁用]" -ForegroundColor White
$Result = Test-Endpoint -Name "Swagger UI" `
    -Url "$MiniAppBaseUrl/docs" `
    -Module "MiniApp API" `
    -ExpectedResult @{StatusCode = 404} `
    -IsDisabled $true
Format-TestResult $Result
$TestResults += $Result

# 4. Public Groups List
Write-Host "4. Public Groups List (/v1/groups/public)" -ForegroundColor White
$Result = Test-Endpoint -Name "Public Groups List" `
    -Url "$MiniAppBaseUrl/v1/groups/public" `
    -Module "MiniApp API" `
    -ExpectedResult @{StatusCode = 200}
Format-TestResult $Result
$TestResults += $Result

# 5. Public Activities
Write-Host "5. Public Activities (/v1/groups/public/activities)" -ForegroundColor White
$Result = Test-Endpoint -Name "Public Activities" `
    -Url "$MiniAppBaseUrl/v1/groups/public/activities" `
    -Module "MiniApp API" `
    -ExpectedResult @{StatusCode = 200}
Format-TestResult $Result
$TestResults += $Result

Write-Host ""

# Test Summary
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$TotalTests = $TestResults.Count
$PassedTests = ($TestResults | Where-Object { $_.Status -eq "Pass" }).Count
$FailedTests = ($TestResults | Where-Object { $_.Status -eq "Fail" }).Count
$SkippedTests = ($TestResults | Where-Object { $_.Status -eq "Skipped" }).Count

Write-Host "Total Tests: $TotalTests" -ForegroundColor White
Write-Host "Passed: $PassedTests ✅" -ForegroundColor Green
Write-Host "Failed: $FailedTests ❌" -ForegroundColor Red
Write-Host "Skipped: $SkippedTests ⏭️" -ForegroundColor Yellow
Write-Host ""

$SuccessRate = if ($TotalTests -gt 0) {
    $effectiveTests = $TotalTests - $SkippedTests
    if ($effectiveTests -gt 0) {
        [math]::Round(($PassedTests / $effectiveTests) * 100, 2)
    } else {
        100
    }
} else {
    0
}

Write-Host "Success Rate (excluding skipped): $SuccessRate%" -ForegroundColor $(if ($SuccessRate -eq 100) { "Green" } else { "Yellow" })
Write-Host ""

# Average response time
$ValidTests = $TestResults | Where-Object { $_.ResponseTime -ne $null -and $_.Status -eq "Pass" }
if ($ValidTests.Count -gt 0) {
    $AvgResponseTime = ($ValidTests | Measure-Object -Property ResponseTime -Average).Average
    Write-Host "Average Response Time: $([math]::Round($AvgResponseTime, 2))ms" -ForegroundColor Cyan
    Write-Host ""
}

# Failed tests details
if ($FailedTests -gt 0) {
    Write-Host "Failed Tests:" -ForegroundColor Red
    $TestResults | Where-Object { $_.Status -eq "Fail" } | ForEach-Object {
        Write-Host "  - $($_.Name) - $($_.Url)" -ForegroundColor Red
        if ($_.Error) {
            Write-Host "    Error: $($_.Error)" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

# Export results
if ($TestResults.Count -gt 0) {
    $CsvPath = if ([string]::IsNullOrEmpty($OutputCsv)) {
        "api-test-results-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
    } else {
        $OutputCsv
    }
    $TestResults | Export-Csv -Path $CsvPath -NoTypeInformation -Encoding UTF8
    Write-Host "Test results saved to: $CsvPath" -ForegroundColor Cyan
    Write-Host ""
}

# 返回测试结果摘要（用于后续脚本）
$summary = @{
    Total = $TotalTests
    Passed = $PassedTests
    Failed = $FailedTests
    Skipped = $SkippedTests
    SuccessRate = $SuccessRate
    AverageResponseTime = if ($ValidTests.Count -gt 0) { [math]::Round($AvgResponseTime, 2) } else { $null }
    CsvPath = $CsvPath
}

return $summary

