# SSH 密鑰配置腳本
# 此腳本會將本地公鑰複製到服務器

$server = "165.154.233.55"
$user = "ubuntu"
$password = "Along2025!!!"
$publicKey = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"

Write-Host "🔑 配置 SSH 密鑰免密碼登錄..."
Write-Host "服務器: $user@$server"
Write-Host ""

# 創建臨時命令文件
$tempScript = [System.IO.Path]::GetTempFileName() + ".sh"
@"
#!/bin/bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '$publicKey' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "✅ 公鑰已添加到服務器"
"@ | Out-File -FilePath $tempScript -Encoding ASCII -NoNewline

Write-Host "📤 正在將公鑰複製到服務器..."
Write-Host "⚠️  提示：需要輸入密碼: $password"
Write-Host ""

# 使用 ssh 連接並執行腳本
$sshCommand = "ssh $user@$server 'bash -s' < $tempScript"
Invoke-Expression $sshCommand

# 清理臨時文件
Remove-Item $tempScript -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ SSH 密鑰配置完成！"
Write-Host ""
Write-Host "🧪 測試無密碼連接..."

# 測試連接（這次應該不需要密碼）
ssh -o "BatchMode=yes" -o "ConnectTimeout=5" $user@$server "echo '✅ 無密碼連接成功！'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SSH 密鑰配置成功！現在可以無密碼連接服務器了。"
} else {
    Write-Host ""
    Write-Host "⚠️  測試連接失敗，請檢查服務器配置。"
}
