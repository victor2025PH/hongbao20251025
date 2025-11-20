# Local Deployment Script
# 本地部署脚本
# 功能：构建镜像 → 启动服务 → 执行全栈测试 → 生成报告

param(
    [switch]$SkipTests = $false,
    [switch]$SkipBuild = $false,
    [string]$EnvFile = ".env.local"
)

$ErrorActionPreference = "Continue"

# 脚本所在目录
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 获取项目根目录（从 docs/deployment 向上两级）
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Local Deployment Script" -ForegroundColor Yellow
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
        
        # 加载环境变量（PowerShell 方式）
        # 注意：PowerShell 中加载 .env 文件需要特殊处理
        Get-Content $EnvFile | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]+?)\s*=\s*(.+)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                if ($value -match '^["\'](.+)["\']$') {
                    $value = $matches[1]
                }
                [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
        Write-Host "✅ Environment variables loaded" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Environment file not found: $EnvFile" -ForegroundColor Yellow
        Write-Host "   Using default environment variables" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # ============================================
    # 步骤 2: 构建和启动服务
    # ============================================
    Write-Host "Step 2: Building and starting services..." -ForegroundColor Yellow
    
    if (-not $SkipBuild) {
        Write-Host "Building Docker images..." -ForegroundColor Cyan
        docker-compose -f docker-compose.yml -f docker-compose.override.yml build
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Docker build failed!" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Docker images built successfully" -ForegroundColor Green
    } else {
        Write-Host "⏭️  Skipping build (--SkipBuild)" -ForegroundColor Yellow
    }
    
    Write-Host "Starting services..." -ForegroundColor Cyan
    docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start services!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Services started successfully" -ForegroundColor Green
    Write-Host ""
    
    # ============================================
    # 步骤 3: 等待服务就绪
    # ============================================
    Write-Host "Step 3: Waiting for services to be ready..." -ForegroundColor Yellow
    
    $maxWait = 60  # 最大等待时间（秒）
    $waited = 0
    $servicesReady = $false
    
    while ($waited -lt $maxWait) {
        try {
            $adminHealth = Invoke-WebRequest -Uri "http://localhost:8000/healthz" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            $miniappHealth = Invoke-WebRequest -Uri "http://localhost:8080/healthz" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            
            if ($adminHealth.StatusCode -eq 200 -and $miniappHealth.StatusCode -eq 200) {
                $servicesReady = $true
                break
            }
        } catch {
            # 服务尚未就绪，继续等待
        }
        
        Start-Sleep -Seconds 2
        $waited += 2
        Write-Host "  Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    }
    
    if (-not $servicesReady) {
        Write-Host "⚠️  Services may not be fully ready, but continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ Services are ready" -ForegroundColor Green
    }
    Write-Host ""
    
    # ============================================
    # 步骤 4: 执行全栈测试
    # ============================================
    $deploymentSuccess = $true
    $testExitCode = 0
    
    if (-not $SkipTests) {
        Write-Host "Step 4: Running full stack tests..." -ForegroundColor Yellow
        
        # 设置测试目标地址（本地）
        $env:API_TEST_ADMIN_BASE_URL = "http://localhost:8000"
        $env:API_TEST_MINIAPP_BASE_URL = "http://localhost:8080"
        $env:API_TEST_FRONTEND_BASE_URL = "http://localhost:3001"
        
        $testScript = Join-Path $ProjectRoot "docs\api-testing\run-full-stack-tests.ps1"
        
        if (Test-Path $testScript) {
            & $testScript -AdminBaseUrl "http://localhost:8000" -MiniAppBaseUrl "http://localhost:8080" -FrontendBaseUrl "http://localhost:3001"
            $testExitCode = $LASTEXITCODE
            
            if ($testExitCode -eq 0) {
                Write-Host "✅ All tests passed!" -ForegroundColor Green
            } else {
                Write-Host "❌ Some tests failed (exit code: $testExitCode)" -ForegroundColor Red
                Write-Host "   Check test reports for details" -ForegroundColor Yellow
                $deploymentSuccess = $false
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
    # 步骤 5: 显示部署结果
    # ============================================
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "Deployment Summary" -ForegroundColor Yellow
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ Services are running:" -ForegroundColor Green
    Write-Host "   • Web Admin API: http://localhost:8000" -ForegroundColor White
    Write-Host "   • MiniApp API: http://localhost:8080" -ForegroundColor White
    Write-Host "   • Frontend: http://localhost:3001" -ForegroundColor White
    Write-Host ""
    
    if (-not $SkipTests) {
        $latestTestDir = Get-ChildItem (Join-Path $ProjectRoot "docs\api-testing\output") -Directory -ErrorAction SilentlyContinue | 
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
    Write-Host "   • View logs: docker-compose -f docker-compose.yml logs -f" -ForegroundColor White
    Write-Host "   • Stop services: docker-compose -f docker-compose.yml down" -ForegroundColor White
    Write-Host "   • Restart services: docker-compose -f docker-compose.yml restart" -ForegroundColor White
    Write-Host ""
    
    # ============================================
    # 步骤 6: 返回正确的退出码
    # ============================================
    if (-not $deploymentSuccess) {
        Write-Host "❌ Deployment completed but tests failed. Exit code: $testExitCode" -ForegroundColor Red
        exit $testExitCode
    } else {
        Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
        exit 0
    }
    
} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}

