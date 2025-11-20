Param(
    [string]$Service = "",
    [switch]$OnlyError = $false
)

<#
用法示例：

  # 查看所有服务日志
  pwsh .\docs\deployment\tail-logs.ps1

  # 只看某个服务
  pwsh .\docs\deployment\tail-logs.ps1 -Service web_admin

  # 只看包含 ERROR/Traceback 的日志
  pwsh .\docs\deployment\tail-logs.ps1 -OnlyError
#>

$ErrorActionPreference = "Stop"

if ($Service) {
    $cmd = "docker compose logs -f $Service"
} else {
    $cmd = "docker compose logs -f"
}

Write-Host "执行: $cmd" -ForegroundColor Cyan

if ($OnlyError) {
    Invoke-Expression $cmd | Select-String -Pattern "ERROR|Traceback" -CaseSensitive:$false
} else {
    Invoke-Expression $cmd
}

