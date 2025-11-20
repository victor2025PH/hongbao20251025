# Full Stack Test Runner - Unified Entry Script
# 全栈测试统一入口脚本
# 一次执行完成所有测试（后端 API、前端测试等），并生成统一报告

param(
    [string]$AdminBaseUrl = "",
    [string]$MiniAppBaseUrl = "",
    [string]$FrontendBaseUrl = "",
    [string]$OutputRoot = "",
    [switch]$AllowFrontendFailure = $false
)

$ErrorActionPreference = "Continue"

# 脚本所在目录
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 获取项目根目录（从 docs/api-testing 向上两级）
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# 从环境变量读取测试目标地址（留有默认值）
if ([string]::IsNullOrEmpty($AdminBaseUrl)) {
    $AdminBaseUrl = $env:API_TEST_ADMIN_BASE_URL
    if ([string]::IsNullOrEmpty($AdminBaseUrl)) {
        $AdminBaseUrl = "http://165.154.233.55:8000"
    }
}

if ([string]::IsNullOrEmpty($MiniAppBaseUrl)) {
    $MiniAppBaseUrl = $env:API_TEST_MINIAPP_BASE_URL
    if ([string]::IsNullOrEmpty($MiniAppBaseUrl)) {
        $MiniAppBaseUrl = "http://165.154.233.55:8080"
    }
}

# 创建带时间戳的输出目录
if ([string]::IsNullOrEmpty($OutputRoot)) {
    $OutputRoot = Join-Path $PSScriptRoot "output"
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$RunDir = Join-Path $OutputRoot "full-stack-test-$timestamp"
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Full Stack Test Runner" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Admin API: $AdminBaseUrl" -ForegroundColor Cyan
Write-Host "MiniApp API: $MiniAppBaseUrl" -ForegroundColor Cyan
Write-Host "Output Directory: $RunDir" -ForegroundColor Cyan
Write-Host "Test Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

# 设置环境变量（供后续测试使用）
$env:API_TEST_ADMIN_BASE_URL = $AdminBaseUrl
$env:API_TEST_MINIAPP_BASE_URL = $MiniAppBaseUrl

# 测试汇总数据
$TestSummary = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    AdminBaseUrl = $AdminBaseUrl
    MiniAppBaseUrl = $MiniAppBaseUrl
    OutputDir = $RunDir
    Stages = @()
}

# ============================================
# 阶段 1: PowerShell API 测试
# ============================================
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Stage 1: PowerShell API Tests" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$psTestLog = Join-Path $RunDir "api-powershell-tests.csv"
$psErrorLog = Join-Path $RunDir "api-powershell-error.log"

$sw = [System.Diagnostics.Stopwatch]::StartNew()

try {
    $psTestScript = Join-Path $PSScriptRoot "run-comprehensive-test-improved.ps1"
    if (Test-Path $psTestScript) {
        & $psTestScript -OutputCsv $psTestLog -PublicIP ($AdminBaseUrl -replace "http://", "" -replace "https://", "" -replace ":.*", "") 2>&1 | Tee-Object -FilePath $psErrorLog
        
        # 读取 CSV 结果统计
        if (Test-Path $psTestLog) {
            $psResults = Import-Csv $psTestLog
            $psPassed = ($psResults | Where-Object { $_.Status -eq "Pass" }).Count
            $psFailed = ($psResults | Where-Object { $_.Status -eq "Fail" }).Count
            $psSkipped = ($psResults | Where-Object { $_.Status -eq "Skipped" }).Count
            $psTotal = $psResults.Count
        } else {
            $psPassed = 0
            $psFailed = 0
            $psSkipped = 0
            $psTotal = 0
        }
    } else {
        Write-Host "⚠️  PowerShell test script not found: $psTestScript" -ForegroundColor Yellow
        $psPassed = 0
        $psFailed = 0
        $psSkipped = 0
        $psTotal = 0
    }
} catch {
    Write-Host "❌ PowerShell API test failed: $($_.Exception.Message)" -ForegroundColor Red
    $psPassed = 0
    $psFailed = 1
    $psSkipped = 0
    $psTotal = 1
    $_.Exception | Out-File -FilePath $psErrorLog -Encoding UTF8
}

$sw.Stop()
$psDurationMs = $sw.ElapsedMilliseconds

$TestSummary.Stages += @{
    Name = "PowerShell API Tests"
    Total = $psTotal
    Passed = $psPassed
    Failed = $psFailed
    Skipped = $psSkipped
    DurationMs = $psDurationMs
    ReportFile = "api-powershell-tests.csv"
    LogFile = "api-powershell-error.log"
}

Write-Host "PowerShell API Tests: $psPassed/$psTotal passed ($psDurationMs ms)" -ForegroundColor $(if ($psFailed -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

# ============================================
# 阶段 2: 后端 pytest API 测试
# ============================================
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Stage 2: Backend pytest API Tests" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$backendHtmlReport = Join-Path $RunDir "backend-pytest-report.html"
$backendLog = Join-Path $RunDir "backend-pytest-output.log"

# 项目根目录已在脚本开头定义（从 docs/api-testing 向上两级）
# 如果 pytest.ini 不在预期位置，尝试向上查找
if (-not (Test-Path (Join-Path $ProjectRoot "pytest.ini"))) {
    $tempRoot = $ProjectRoot
    while (-not (Test-Path (Join-Path $tempRoot "pytest.ini"))) {
        $parent = Split-Path -Parent $tempRoot
        if ($parent -eq $tempRoot) {
            # 到达根目录，停止
            break
        }
        $tempRoot = $parent
    }
    if (Test-Path (Join-Path $tempRoot "pytest.ini")) {
        $ProjectRoot = $tempRoot
    }
}

$sw = [System.Diagnostics.Stopwatch]::StartNew()

try {
    Push-Location $ProjectRoot
    
    # 检查 pytest 是否可用
    $pytestCmd = Get-Command pytest -ErrorAction SilentlyContinue
    if (-not $pytestCmd) {
        Write-Host "⚠️  pytest not found. Install it with: pip install pytest pytest-html" -ForegroundColor Yellow
        $backendPassed = 0
        $backendFailed = 0
        $backendSkipped = 0
        $backendTotal = 0
    } else {
        # 运行 pytest
        pytest tests/api `
            --maxfail=1 `
            --disable-warnings `
            --html=$backendHtmlReport `
            --self-contained-html `
            --tb=short 2>&1 | Tee-Object -FilePath $backendLog
        
        $pytestExitCode = $LASTEXITCODE
        
        # 尝试解析 pytest 输出统计（简化版）
        if (Test-Path $backendLog) {
            $logContent = Get-Content $backendLog -Raw
            if ($logContent -match "(\d+) passed") {
                $backendPassed = [int]$matches[1]
            } else {
                $backendPassed = 0
            }
            if ($logContent -match "(\d+) failed") {
                $backendFailed = [int]$matches[1]
            } else {
                $backendFailed = 0
            }
            if ($logContent -match "(\d+) skipped") {
                $backendSkipped = [int]$matches[1]
            } else {
                $backendSkipped = 0
            }
            $backendTotal = $backendPassed + $backendFailed + $backendSkipped
        } else {
            $backendPassed = 0
            $backendFailed = 0
            $backendSkipped = 0
            $backendTotal = 0
        }
        
        if ($pytestExitCode -ne 0 -and $backendTotal -eq 0) {
            $backendFailed = 1
            $backendTotal = 1
        }
    }
} catch {
    Write-Host "❌ Backend pytest test failed: $($_.Exception.Message)" -ForegroundColor Red
    $backendPassed = 0
    $backendFailed = 1
    $backendSkipped = 0
    $backendTotal = 1
    $_.Exception | Out-File -FilePath $backendLog -Encoding UTF8
} finally {
    Pop-Location
}

$sw.Stop()
$backendDurationMs = $sw.ElapsedMilliseconds

$TestSummary.Stages += @{
    Name = "Backend pytest API Tests"
    Total = $backendTotal
    Passed = $backendPassed
    Failed = $backendFailed
    Skipped = $backendSkipped
    DurationMs = $backendDurationMs
    ReportFile = "backend-pytest-report.html"
    LogFile = "backend-pytest-output.log"
}

Write-Host "Backend pytest Tests: $backendPassed/$backendTotal passed ($backendDurationMs ms)" -ForegroundColor $(if ($backendFailed -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

# ============================================
# 阶段 3: 前端 Smoke Test
# ============================================
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Stage 3: Frontend Smoke Tests" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 确定前端测试地址
if ([string]::IsNullOrEmpty($FrontendBaseUrl)) {
    $FrontendBaseUrl = $env:API_TEST_FRONTEND_BASE_URL
    if ([string]::IsNullOrEmpty($FrontendBaseUrl)) {
        $FrontendBaseUrl = "http://localhost:3001"
    }
}

$frontendSmokeLog = Join-Path $RunDir "frontend-smoke-test-output.log"
$frontendSmokeReport = Join-Path $RunDir "frontend-smoke-test-report.html"

$sw = [System.Diagnostics.Stopwatch]::StartNew()

$frontendTests = @(
    @{Name = "Frontend Homepage"; Url = "$FrontendBaseUrl/"; ExpectedStatus = 200}
    @{Name = "Frontend Groups Page"; Url = "$FrontendBaseUrl/groups"; ExpectedStatus = 200}
)

$frontendPassed = 0
$frontendFailed = 0
$frontendSkipped = 0
$frontendTotal = $frontendTests.Count

Write-Host "Testing Frontend: $FrontendBaseUrl" -ForegroundColor Cyan
Write-Host ""

foreach ($test in $frontendTests) {
    try {
        $testSw = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri $test.Url -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        $testSw.Stop()
        
        if ($response.StatusCode -eq $test.ExpectedStatus) {
            Write-Host "  ✅ $($test.Name) - Status: $($response.StatusCode) ($($testSw.ElapsedMilliseconds)ms)" -ForegroundColor Green
            $frontendPassed++
        } else {
            Write-Host "  ⚠️  $($test.Name) - Status: $($response.StatusCode) (Expected: $($test.ExpectedStatus))" -ForegroundColor Yellow
            $frontendFailed++
        }
    } catch {
        Write-Host "  ❌ $($test.Name) - Error: $($_.Exception.Message)" -ForegroundColor Red
        $frontendFailed++
        "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $($test.Name) - Error: $($_.Exception.Message)" | Out-File -FilePath $frontendSmokeLog -Append -Encoding UTF8
    }
}

$sw.Stop()
$frontendDurationMs = $sw.ElapsedMilliseconds

# 生成简单的 HTML 报告
$frontendReportHtml = @"
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Frontend Smoke Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .pass { color: green; }
        .fail { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Frontend Smoke Test Report</h1>
    <p><strong>Test Time:</strong> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
    <p><strong>Frontend URL:</strong> $FrontendBaseUrl</p>
    <h2>Summary</h2>
    <ul>
        <li>Total: $frontendTotal</li>
        <li class="pass">Passed: $frontendPassed</li>
        <li class="fail">Failed: $frontendFailed</li>
    </ul>
    <h2>Test Details</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>URL</th>
            <th>Expected Status</th>
            <th>Result</th>
        </tr>
"@

foreach ($test in $frontendTests) {
    $result = "❌ Failed"
    try {
        $response = Invoke-WebRequest -Uri $test.Url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq $test.ExpectedStatus) {
            $result = "✅ Passed"
        }
    } catch {
        $result = "❌ Failed: $($_.Exception.Message)"
    }
    
    $frontendReportHtml += @"
        <tr>
            <td>$($test.Name)</td>
            <td><a href="$($test.Url)">$($test.Url)</a></td>
            <td>$($test.ExpectedStatus)</td>
            <td>$result</td>
        </tr>
"@
}

$frontendReportHtml += @"
    </table>
</body>
</html>
"@

$frontendReportHtml | Out-File -FilePath $frontendSmokeReport -Encoding UTF8

$TestSummary.Stages += @{
    Name = "Frontend Smoke Tests"
    Total = $frontendTotal
    Passed = $frontendPassed
    Failed = $frontendFailed
    Skipped = $frontendSkipped
    DurationMs = $frontendDurationMs
    ReportFile = "frontend-smoke-test-report.html"
    LogFile = "frontend-smoke-test-output.log"
}

Write-Host "Frontend Smoke Tests: $frontendPassed/$frontendTotal passed ($frontendDurationMs ms)" -ForegroundColor $(if ($frontendFailed -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

# ============================================
# 生成汇总 JSON
# ============================================
$summaryJson = Join-Path $RunDir "summary.json"
$TestSummary | ConvertTo-Json -Depth 10 | Out-File -FilePath $summaryJson -Encoding UTF8

# ============================================
# 生成汇总 CSV
# ============================================
$summaryCsv = Join-Path $RunDir "summary.csv"
$TestSummary.Stages | ForEach-Object {
    [PSCustomObject]@{
        Stage = $_.Name
        Total = $_.Total
        Passed = $_.Passed
        Failed = $_.Failed
        Skipped = $_.Skipped
        DurationMs = $_.DurationMs
        ReportFile = $_.ReportFile
        LogFile = $_.LogFile
    }
} | Export-Csv -Path $summaryCsv -NoTypeInformation -Encoding UTF8

# ============================================
# 调用报告生成脚本
# ============================================
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Generating Unified Report" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$reportScript = Join-Path $PSScriptRoot "render-full-stack-report.py"
$reportHtml = Join-Path $RunDir "full-stack-test-report.html"

if (Test-Path $reportScript) {
    try {
        python $reportScript --summary $summaryJson --output $reportHtml
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Unified report generated: $reportHtml" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Report generation failed with exit code $LASTEXITCODE" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Failed to generate unified report: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Report generator script not found: $reportScript" -ForegroundColor Yellow
}

# ============================================
# 最终汇总
# ============================================
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$totalTests = ($TestSummary.Stages | Measure-Object -Property Total -Sum).Sum
$totalPassed = ($TestSummary.Stages | Measure-Object -Property Passed -Sum).Sum
$totalFailed = ($TestSummary.Stages | Measure-Object -Property Failed -Sum).Sum
$totalSkipped = ($TestSummary.Stages | Measure-Object -Property Skipped -Sum).Sum
$totalDurationMs = ($TestSummary.Stages | Measure-Object -Property DurationMs -Sum).Sum

Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $totalPassed ✅" -ForegroundColor Green
Write-Host "Failed: $totalFailed ❌" -ForegroundColor Red
Write-Host "Skipped: $totalSkipped ⏭️" -ForegroundColor Yellow
Write-Host "Total Duration: $([math]::Round($totalDurationMs / 1000, 2))s" -ForegroundColor Cyan
Write-Host ""

Write-Host "Output Directory: $RunDir" -ForegroundColor Cyan
Write-Host "Unified Report: $reportHtml" -ForegroundColor Cyan
Write-Host ""

# 判断是否有阻断性失败
# 后端核心测试失败（健康检查、就绪检查、核心 API）会阻断
$blockingFailures = 0

foreach ($stage in $TestSummary.Stages) {
    if ($stage.Name -match "PowerShell API Tests|Backend pytest") {
        $blockingFailures += $stage.Failed
    }
}

# 前端测试失败是否阻断（默认阻断，除非指定 -AllowFrontendFailure）
$frontendStage = $TestSummary.Stages | Where-Object { $_.Name -match "Frontend" }
if ($frontendStage -and $frontendStage.Failed -gt 0 -and -not $AllowFrontendFailure) {
    $blockingFailures += $frontendStage.Failed
}

Write-Host ""
if ($blockingFailures -gt 0) {
    Write-Host "❌ Some critical tests failed. Exit code: 1" -ForegroundColor Red
    exit 1
} elseif ($totalFailed -gt 0) {
    Write-Host "⚠️  Some non-critical tests failed, but deployment can continue." -ForegroundColor Yellow
    Write-Host "   Exit code: 0 (non-blocking failures)" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "✅ All tests passed! Exit code: 0" -ForegroundColor Green
    exit 0
}

