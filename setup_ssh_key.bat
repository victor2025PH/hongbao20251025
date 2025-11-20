@echo off
chcp 65001 >nul
echo ====================================
echo 🔑 SSH 密鑰配置腳本
echo ====================================
echo.
echo 此腳本將配置無密碼 SSH 登錄
echo 服務器: ubuntu@165.154.233.55
echo.
echo ⚠️  重要提示：
echo.
echo   1. 接下來的 SSH 連接會要求輸入密碼
echo   2. 密碼是: Along2025!!!
echo   3. 輸入密碼時不會顯示任何字符（這是正常的安全行為）
echo   4. 直接輸入密碼後按 Enter 即可
echo.
echo ====================================
echo.
pause

echo.
echo 📤 步驟 1: 讀取本地公鑰...
type "%USERPROFILE%\.ssh\id_rsa.pub" > temp_public_key.txt
if errorlevel 1 (
    echo ❌ 錯誤: 未找到 SSH 公鑰文件
    echo 請先運行: ssh-keygen -t rsa -b 4096
    pause
    exit /b 1
)

echo ✅ 公鑰已讀取
echo.

echo 📤 步驟 2: 複製公鑰到服務器...
echo.
echo ⚠️  現在會提示輸入密碼，請輸入: Along2025!!!
echo     （輸入時不會顯示字符，直接輸入後按 Enter）
echo.
echo ------------------------------------
echo.

type temp_public_key.txt | ssh ubuntu@165.154.233.55 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo '✅ 公鑰已添加成功'"

if errorlevel 1 (
    echo.
    echo ❌ 連接失敗！請檢查：
    echo    1. 網絡連接是否正常
    echo    2. 服務器地址是否正確（165.154.233.55）
    echo    3. 密碼是否正確（Along2025!!!）
    del temp_public_key.txt 2>nul
    pause
    exit /b 1
)

del temp_public_key.txt 2>nul

echo.
echo ====================================
echo 🧪 步驟 3: 測試無密碼連接...
echo ====================================
echo.

ssh -o "BatchMode=yes" -o "ConnectTimeout=5" ubuntu@165.154.233.55 "echo '✅ 無密碼連接成功！' && hostname && whoami"

if errorlevel 1 (
    echo.
    echo ⚠️  測試連接失敗，可能需要檢查服務器配置
) else (
    echo.
    echo ====================================
    echo ✅ SSH 密鑰配置成功！
    echo ====================================
    echo.
    echo 現在可以無密碼連接服務器了！
    echo 可以執行部署腳本進行自動部署。
)

echo.
pause
