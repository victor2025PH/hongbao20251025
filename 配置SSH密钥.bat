@echo off
chcp 65001 >nul
title SSH 密鑰配置
color 0A

echo.
echo ============================================================
echo           🔑 SSH 密鑰配置（無密碼登錄）
echo ============================================================
echo.
echo 服務器: ubuntu@165.154.233.55
echo 密碼: Along2025!!!
echo.
echo ⚠️  重要提示：
echo    輸入密碼時不會顯示任何字符（這是正常的安全行為）
echo    直接輸入密碼後按 Enter 即可
echo.
echo ============================================================
echo.
pause

echo.
echo 📤 正在將公鑰複製到服務器...
echo.

type "%USERPROFILE%\.ssh\id_rsa.pub" | ssh ubuntu@165.154.233.55 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'SUCCESS: SSH key added successfully'"

if errorlevel 1 (
    echo.
    echo ❌ 配置失敗！
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 🧪 測試無密碼連接...
echo ============================================================
echo.

ssh -o "BatchMode=yes" -o "ConnectTimeout=5" ubuntu@165.154.233.55 "echo 'SUCCESS: Passwordless connection works!' && hostname && whoami"

if errorlevel 1 (
    echo.
    echo ⚠️  測試連接失敗
    echo 可能需要等待幾秒後重試
) else (
    echo.
    echo ============================================================
    echo ✅ SSH 密鑰配置成功！
    echo ============================================================
    echo.
    echo 現在可以無密碼連接服務器了！
    echo 可以執行自動部署腳本進行部署。
    echo.
)

echo.
pause