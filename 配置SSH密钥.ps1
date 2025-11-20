# SSH 密鑰配置腳本
# 在 PowerShell 終端中執行此腳本

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "🔑 SSH 密鑰配置（無密碼登錄）" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服務器: ubuntu@165.154.233.55" -ForegroundColor White
Write-Host ""

# 檢查公鑰是否存在
$publicKeyPath = "$env:USERPROFILE\.ssh\id_rsa.pub"
if (-not (Test-Path $publicKeyPath)) {
    Write-Host "❌ 錯誤: 未找到 SSH 公鑰文件" -ForegroundColor Red
    Write-Host "請先運行: ssh-keygen -t rsa -b 4096" -ForegroundColor Yellow
    pause
    exit 1
}

$publicKey = Get-Content $publicKeyPath
Write-Host "✅ 已讀取公鑰" -ForegroundColor Green
Write-Host ""

Write-Host "⚠️  重要提示：" -ForegroundColor Red
Write-Host "   接下來會要求輸入密碼" -ForegroundColor Yellow
Write-Host "   密碼: Along2025!!!" -ForegroundColor White
Write-Host "   輸入時不會顯示任何字符（這是正常的）" -ForegroundColor Gray
Write-Host "   直接在鍵盤輸入密碼後按 Enter" -ForegroundColor White
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意鍵開始執行 SSH 命令..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

Write-Host "📤 正在將公鑰複製到服務器..." -ForegroundColor Green
Write-Host ""

# 執行 SSH 命令複製公鑰
$sshCommand = @"
mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo '✅ 公鑰已添加成功'
"@

$publicKey | ssh ubuntu@165.154.233.55 $sshCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "🧪 測試無密碼連接..." -ForegroundColor Yellow
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host ""
    
    ssh -o "BatchMode=yes" -o "ConnectTimeout=5" ubuntu@165.154.233.55 "echo '✅ 無密碼連接成功！'; hostname; whoami"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "====================================" -ForegroundColor Cyan
        Write-Host "✅ SSH 密鑰配置成功！" -ForegroundColor Green
        Write-Host "====================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "現在可以無密碼連接服務器了！" -ForegroundColor White
        Write-Host "可以執行自動部署腳本進行部署。" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "⚠️  測試連接失敗" -ForegroundColor Yellow
        Write-Host "可能需要等待幾秒後重試" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "❌ 配置失敗！" -ForegroundColor Red
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "  1. 網絡連接問題" -ForegroundColor White
    Write-Host "  2. 密碼輸入錯誤" -ForegroundColor White
    Write-Host "  3. 服務器不可達" -ForegroundColor White
}

Write-Host ""
pause
