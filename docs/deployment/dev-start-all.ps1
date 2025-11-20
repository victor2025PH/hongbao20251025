Param(
    [switch]$Rebuild = $false,
    [switch]$WithTests = $false,
    [int]$HealthTimeoutSeconds = 60
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

Write-Host "==[ 1/4 ] 加载本地环境变量 (.env 文件如果存在) ==" -ForegroundColor Cyan
$EnvFile = Join-Path $RepoRoot ".env"
if (Test-Path $EnvFile) {
    try {
        $lines = [System.IO.File]::ReadAllLines($EnvFile)

        foreach ($line in $lines) {
            # 跳过空行和注释行
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            if ($line.TrimStart().StartsWith("#")) { continue }

            # 找到第一个 =
            $index = $line.IndexOf("=")
            if ($index -lt 1) { continue }

            $name  = $line.Substring(0, $index).Trim()
            $value = $line.Substring($index + 1).Trim()

            if (-not [string]::IsNullOrWhiteSpace($name)) {
                # 只在当前进程设置环境变量，避免污染系统
                [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }

        Write-Host "已加载 .env" -ForegroundColor Green
    }
    catch {
        Write-Host "读取 .env 时出错：$($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "未找到 .env，使用系统环境变量。" -ForegroundColor Yellow
}

Write-Host "==[ 2/4 ] 启动 Docker Compose 服务 ==" -ForegroundColor Cyan

# 关闭 BuildKit，避免中文路径触发 buildx 异常
$env:DOCKER_BUILDKIT = "0"
$env:COMPOSE_DOCKER_CLI_BUILD = "0"

$composeArgs = @(
    "-f", (Join-Path $RepoRoot "docker-compose.yml")
)

$cmd = "docker compose $($composeArgs -join ' ') up -d"
if ($Rebuild) { $cmd += " --build" }

Write-Host "执行: $cmd" -ForegroundColor DarkCyan
Invoke-Expression $cmd

Write-Host "Docker 服务已启动，等待健康检查..." -ForegroundColor Green

Write-Host "==[ 3/4 ] 运行健康检查 Watchdog（单次模式） ==" -ForegroundColor Cyan

$WatchdogPath = Join-Path $RepoRoot "ops\health_watchdog.py"

if (Test-Path $WatchdogPath) {
    $pythonExe = "python"
    & $pythonExe $WatchdogPath "--once" "--timeout" $HealthTimeoutSeconds
} else {
    Write-Host "未找到 ops\health_watchdog.py，跳过健康检查。" -ForegroundColor Yellow
}

Write-Host "==[ 4/4 ] 可选执行全栈测试 ==" -ForegroundColor Cyan

if ($WithTests) {
    $FullStackTestScript = Join-Path $RepoRoot "docs\api-testing\run-full-stack-tests.ps1"
    if (Test-Path $FullStackTestScript) {
        Write-Host "开始执行全栈测试..." -ForegroundColor Cyan
        pwsh $FullStackTestScript
    } else {
        Write-Host "未找到 run-full-stack-tests.ps1，跳过测试。" -ForegroundColor Yellow
    }
}

Write-Host "全部完成。本地环境已启动。" -ForegroundColor Green

