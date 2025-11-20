# Production Deployment Script
# 生产环境部署脚本
# 功能：拉取最新镜像 → 启动服务 → 执行全栈测试 → 生成报告

param(
    [switch]$SkipTests = $false,
    [switch]$SkipPull = $false,
    [switch]$AllowFrontendFailure = $false,
    [string]$EnvFile = ".env.production",
    [string]$AdminBaseUrl = "",
    [string]$MiniAppBaseUrl = "",
    [string]$FrontendBaseUrl = ""
)

$ErrorActionPreference = "Continue"

# 脚本所在目录
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 获取项目根目录（从 docs/deployment 向上两级）
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Production Deployment Script" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Cyan
Write-Host "Environment File: $EnvFile" -ForegroundColor Cyan
Write-Host ""

# 切换到项目根目录
Push-Location $ProjectRoot

try {
    # ============================================
    # 步骤 1: 检查环境文件
    # ============================================
    Write-Host "Step 1: Checking environment file..." -ForegroundColor Yellow
    
    if (Test-Path $EnvFile) {
        Write-Host "✅ Found environment file: $EnvFile" -ForegroundColor Green
        
        # 加载环境变量（仅加载非敏感部分）
        # 注意：生产环境敏感变量应从安全存储读取，这里仅加载配置
        Get-Content $EnvFile | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]+?)\s*=\s*(.+)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                if ($value -match '^["\'](.+)["\']$') {
                    $value = $matches[1]
                }
                # 仅设置非敏感变量（示例，实际应根据需要过滤）
                if ($key -notmatch 'PASSWORD|SECRET|KEY|TOKEN') {
                    [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
                }
            }
        }
        Write-Host "✅ Environment variables loaded" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Environment file not found: $EnvFile" -ForegroundColor Yellow
        Write-Host "   Make sure .env.production exists with production configuration" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # ============================================
    # 步骤 2: 拉取最新镜像（可选）
    # ============================================
    if (-not $SkipPull) {
        Write-Host "Step 2: Pulling latest images..." -ForegroundColor Yellow
        docker-compose -f docker-compose.production.yml pull
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  Failed to pull some images, continuing with existing images..." -ForegroundColor Yellow
        } else {
            Write-Host "✅ Images pulled successfully" -ForegroundColor Green
        }
        Write-Host ""
    } else {
        Write-Host "⏭️  Skipping image pull (--SkipPull)" -ForegroundColor Yellow
        Write-Host ""
    }
    
    # ============================================
    # 步骤 3: 启动服务
    # ============================================
    Write-Host "Step 3: Starting services..." -ForegroundColor Yellow
    
    docker-compose -f docker-compose.production.yml up -d --build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start services!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Services started successfully" -ForegroundColor Green
    Write-Host ""
    
    # ============================================
    # 步骤 4: 等待服务就绪
    # ============================================
    Write-Host "Step 4: Waiting for services to be ready..." -ForegroundColor Yellow
    
    # 确定测试目标地址
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
    
    $maxWait = 90  # 生产环境等待更长时间
    $waited = 0
    $servicesReady = $false
    
    while ($waited -lt $maxWait) {
        try {
            $adminHealth = Invoke-WebRequest -Uri "$AdminBaseUrl/healthz" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            $miniappHealth = Invoke-WebRequest -Uri "$MiniAppBaseUrl/healthz" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            
            if ($adminHealth.StatusCode -eq 200 -and $miniappHealth.StatusCode -eq 200) {
                $servicesReady = $true
                break
            }
        } catch {
            # 服务尚未就绪，继续等待
        }
        
        Start-Sleep -Seconds 3
        $waited += 3
        Write-Host "  Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    }
    
    if (-not $servicesReady) {
        Write-Host "⚠️  Services may not be fully ready, but continuing..." -ForegroundColor Yellow
        Write-Host "   You may want to check service logs: docker-compose -f docker-compose.production.yml logs" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Services are ready" -ForegroundColor Green
    }
    Write-Host ""
    
    # ============================================
    # 步骤 5: 执行全栈测试
    # ============================================
    if (-not $SkipTests) {
        Write-Host "Step 5: Running full stack tests..." -ForegroundColor Yellow
        Write-Host "   Admin API: $AdminBaseUrl" -ForegroundColor Gray
        Write-Host "   MiniApp API: $MiniAppBaseUrl" -ForegroundColor Gray
        Write-Host ""
        
        # 确定前端测试地址（如果有前端服务）
        if ([string]::IsNullOrEmpty($FrontendBaseUrl)) {
            try {
                # 尝试从 AdminBaseUrl 推断前端地址（如果前端在同一服务器）
                $adminHost = ($AdminBaseUrl -replace "http://", "" -replace "https://", "" -split ":")[0]
                $FrontendBaseUrl = "http://${adminHost}:3001"
                # 尝试访问前端健康检查（可选，不阻断）
                $frontendTest = Invoke-WebRequest -Uri "$FrontendBaseUrl" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($frontendTest.StatusCode -eq 200) {
                    Write-Host "   Frontend detected at: $FrontendBaseUrl" -ForegroundColor Gray
                } else {
                    $FrontendBaseUrl = ""
                }
            } catch {
                # 前端不可用，跳过前端测试
                $FrontendBaseUrl = ""
            }
        }
        
        # 设置测试目标地址
        $env:API_TEST_ADMIN_BASE_URL = $AdminBaseUrl
        $env:API_TEST_MINIAPP_BASE_URL = $MiniAppBaseUrl
        if (-not [string]::IsNullOrEmpty($FrontendBaseUrl)) {
            $env:API_TEST_FRONTEND_BASE_URL = $FrontendBaseUrl
        }
        
        $testScript = Join-Path $ProjectRoot "docs\api-testing\run-full-stack-tests.ps1"
        
        if (Test-Path $testScript) {
            $testParams = @{
                AdminBaseUrl = $AdminBaseUrl
                MiniAppBaseUrl = $MiniAppBaseUrl
            }
            if (-not [string]::IsNullOrEmpty($FrontendBaseUrl)) {
                $testParams["FrontendBaseUrl"] = $FrontendBaseUrl
            }
            if ($AllowFrontendFailure) {
                $testParams["AllowFrontendFailure"] = $true
            }
            
            & $testScript @testParams
            $testExitCode = $LASTEXITCODE
            
            if ($testExitCode -eq 0) {
                Write-Host "✅ All tests passed!" -ForegroundColor Green
            } else {
                Write-Host "❌ Some tests failed (exit code: $testExitCode)" -ForegroundColor Red
                Write-Host "   Deployment completed, but tests indicate issues" -ForegroundColor Yellow
                Write-Host "   Check test reports for details" -ForegroundColor Yellow
                # 生产环境测试失败返回非零退出码
                exit $testExitCode
            }
        } else {
            Write-Host "⚠️  Test script not found: $testScript" -ForegroundColor Yellow
            Write-Host "   Skipping tests..." -ForegroundColor Yellow
        }
        Write-Host ""
    } else {
        Write-Host "⏭️  Skipping tests (--SkipTests)" -ForegroundColor Yellow
        Write-Host ""
    }
    
    # ============================================
    # 步骤 6: 显示部署结果
    # ============================================
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "Deployment Summary" -ForegroundColor Yellow
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ Services are running:" -ForegroundColor Green
    Write-Host "   • Web Admin API: $AdminBaseUrl" -ForegroundColor White
    Write-Host "   • MiniApp API: $MiniAppBaseUrl" -ForegroundColor White
    Write-Host ""
    
    if (-not $SkipTests) {
        $latestTestDir = Get-ChildItem (Join-Path $ProjectRoot "docs\api-testing\output") -Directory | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -First 1
        
        if ($latestTestDir) {
            $reportPath = Join-Path $latestTestDir.FullName "full-stack-test-report.html"
            Write-Host "📊 Test Report:" -ForegroundColor Cyan
            Write-Host "   $reportPath" -ForegroundColor White
            Write-Host ""
        }
    }
    
    Write-Host "📋 Useful commands:" -ForegroundColor Cyan
    Write-Host "   • View logs: docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor White
    Write-Host "   • Stop services: docker-compose -f docker-compose.production.yml down" -ForegroundColor White
    Write-Host "   • Restart services: docker-compose -f docker-compose.production.yml restart" -ForegroundColor White
    Write-Host "   • Check service status: docker-compose -f docker-compose.production.yml ps" -ForegroundColor White
    Write-Host ""
    
    # ============================================
    # 步骤 7: 返回正确的退出码
    # ============================================
    if (-not $SkipTests) {
        if ($testExitCode -ne 0) {
            Write-Host "❌ Production deployment completed but tests failed. Exit code: $testExitCode" -ForegroundColor Red
            exit $testExitCode
        }
    }
    
    Write-Host "✅ Production deployment completed successfully!" -ForegroundColor Green
    exit 0
    
} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}

