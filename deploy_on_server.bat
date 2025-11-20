@echo off
chcp 65001 >nul
echo ====================================
echo 🚀 雲服務器部署腳本
echo ====================================
echo.
echo 此腳本將連接到雲服務器並執行部署
echo 服務器地址: 165.154.233.55
echo 用戶名: ubuntu
echo.
echo ⚠️  注意：連接時需要輸入密碼: Along2025!!!
echo.
pause

echo.
echo 📥 步驟 1: 連接到服務器並拉取最新代碼...
ssh ubuntu@165.154.233.55 "cd /opt/redpacket && git pull origin master && echo '✅ 代碼更新成功'"

echo.
echo 🔨 步驟 2: 執行部署腳本...
ssh ubuntu@165.154.233.55 "cd /opt/redpacket && chmod +x deploy/scripts/deploy_on_server.sh && bash deploy/scripts/deploy_on_server.sh"

echo.
echo ✅ 部署完成！
echo.
echo 📋 驗證服務狀態:
ssh ubuntu@165.154.233.55 "cd /opt/redpacket && docker compose -f docker-compose.production.yml ps"

echo.
echo 🔍 測試健康檢查:
ssh ubuntu@165.154.233.55 "curl -s http://127.0.0.1:8000/healthz"

echo.
pause
