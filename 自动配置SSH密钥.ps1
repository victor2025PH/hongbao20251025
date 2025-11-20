# 自動配置 SSH 密鑰腳本
# 此腳本會自動輸入密碼配置 SSH 密鑰

$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "🔑 SSH 密鑰自動配置" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$server = "165.154.233.55"
$user = "ubuntu"
$password = "Along2025!!!"

# 檢查公鑰
$publicKeyPath = "$env:USERPROFILE\.ssh\id_rsa.pub"
if (-not (Test-Path $publicKeyPath)) {
    Write-Host "❌ 錯誤: 未找到 SSH 公鑰文件" -ForegroundColor Red
    Write-Host "請先運行: ssh-keygen -t rsa -b 4096" -ForegroundColor Yellow
    exit 1
}

$publicKey = (Get-Content $publicKeyPath -Raw).Trim()
Write-Host "✅ 已讀取公鑰" -ForegroundColor Green
Write-Host ""

# 方法：使用 plink (PuTTY) 或直接使用 ssh 命令
# 由於 PowerShell 的 SSH 不支持自動輸入密碼，我們需要手動執行

Write-Host "📤 正在配置 SSH 密鑰..." -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  注意：需要使用 ssh 命令手動執行" -ForegroundColor Yellow
Write-Host ""
Write-Host "請在終端中執行以下命令：" -ForegroundColor Cyan
Write-Host ""
Write-Host "echo '$publicKey' | ssh $user@$server `"mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo '✅ SSH key added successfully'`"" -ForegroundColor White
Write-Host ""
Write-Host "當提示輸入密碼時，輸入: $password" -ForegroundColor Yellow
Write-Host ""

# 嘗試使用 echo 和管道
Write-Host "正在嘗試自動配置..." -ForegroundColor Green
Write-Host ""

# 創建臨時文件
$tempScript = [System.IO.Path]::GetTempFileName()
$publicKey | Out-File -FilePath $tempScript -Encoding ASCII -NoNewline

# 使用 Start-Process 執行 SSH 命令
$sshCommand = "type `"$tempScript`" | ssh $user@$server `"mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'SUCCESS'`""

Write-Host "執行命令: $sshCommand" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  請在打開的終端窗口中輸入密碼: $password" -ForegroundColor Red
Write-Host ""

# 執行命令（會在另一個窗口中打開）
Start-Process powershell -ArgumentList "-NoExit", "-Command", $sshCommand

Write-Host ""
Write-Host "已打開新的終端窗口執行 SSH 配置" -ForegroundColor Green
Write-Host "請在新窗口中輸入密碼: $password" -ForegroundColor Yellow
Write-Host ""

# 清理臨時文件
Start-Sleep -Seconds 2
Remove-Item $tempScript -ErrorAction SilentlyContinue

Write-Host "配置完成後，測試連接..." -ForegroundColor Cyan
Write-Host "按任意鍵繼續..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 測試連接
Write-Host ""
Write-Host "🧪 測試無密碼連接..." -ForegroundColor Cyan
ssh -o "BatchMode=yes" -o "ConnectTimeout=5" ubuntu@165.154.233.55 "echo '✅ 無密碼連接成功！'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SSH 密鑰配置成功！" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  無密碼連接失敗，請檢查配置" -ForegroundColor Yellow
}

Write-Host ""
pause
