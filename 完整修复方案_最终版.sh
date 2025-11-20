#!/bin/bash
# 完整修復方案 - 最終版
# 解決：鏡像不存在、pandas 缺失、環境變量警告

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 完整修復方案 - 最終版"
echo "===================================="
echo ""

# 步驟 1: 確認代碼已更新（包含 pandas 和 openpyxl）
echo "📥 步驟 1: 確認代碼已更新..."
git pull origin master || {
    echo "⚠️  Git 拉取失敗，繼續使用本地代碼..."
}
echo "✅ 代碼已確認"
echo ""

# 步驟 2: 確認 requirements.txt 包含 pandas 和 openpyxl
echo "🔍 步驟 2: 確認 requirements.txt 包含 pandas 和 openpyxl..."
if grep -q "pandas" requirements.txt && grep -q "openpyxl" requirements.txt; then
    echo "✅ pandas 和 openpyxl 已在 requirements.txt 中"
    grep -E "pandas|openpyxl" requirements.txt
else
    echo "❌ 缺少 pandas 或 openpyxl，正在添加..."
    echo "pandas==2.2.3" >> requirements.txt
    echo "openpyxl==3.1.5" >> requirements.txt
    echo "✅ 已添加 pandas 和 openpyxl"
fi
echo ""

# 步驟 3: 確認 .env.production 存在
echo "🔍 步驟 3: 確認 .env.production 存在..."
if [ ! -f .env.production ]; then
    echo "❌ .env.production 不存在！"
    echo "   請確保已創建 .env.production 文件"
    exit 1
fi
echo "✅ .env.production 已存在"
echo ""

# 步驟 4: 檢查 .env.production 是否包含 POSTGRES_USER 和 POSTGRES_DB
echo "🔍 步驟 4: 檢查 .env.production 中的環境變量..."
if grep -q "POSTGRES_USER" .env.production && grep -q "POSTGRES_DB" .env.production; then
    echo "✅ POSTGRES_USER 和 POSTGRES_DB 已設置"
    grep -E "POSTGRES_USER|POSTGRES_DB" .env.production | sed 's/=.*/=***/'  # 隱藏密碼
else
    echo "⚠️  警告：POSTGRES_USER 或 POSTGRES_DB 未設置，將使用默認值"
fi
echo ""

# 步驟 5: 停止所有服務
echo "🛑 步驟 5: 停止所有服務..."
docker compose -f docker-compose.production.yml down
echo "✅ 服務已停止"
echo ""

# 步驟 6: 刪除舊的 web_admin 容器（如果存在）
echo "🗑️  步驟 6: 清理舊的 web_admin 容器..."
docker rm -f redpacket_web_admin 2>/dev/null || echo "  web_admin 容器不存在"
echo "✅ 清理完成"
echo ""

# 步驟 7: 刪除舊的 backend 鏡像（如果存在，強制重新構建）
echo "🗑️  步驟 7: 刪除舊的 backend 鏡像（強制重新構建）..."
docker rmi redpacket/backend:latest 2>/dev/null || echo "  鏡像不存在或已被使用，將強制重新構建"
echo "✅ 準備重新構建"
echo ""

# 步驟 8: 重新構建 backend 鏡像（包含 pandas 和 openpyxl）
echo "🔨 步驟 8: 重新構建 backend 鏡像（包含 pandas 和 openpyxl）..."
echo "   這可能需要 3-5 分鐘，請耐心等待..."
docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache bot web_admin miniapp_api || {
    echo "⚠️  構建失敗，嘗試使用緩存重新構建..."
    docker compose --env-file .env.production -f docker-compose.production.yml build bot web_admin miniapp_api
}

if [ $? -eq 0 ]; then
    echo "✅ 鏡像構建完成"
else
    echo "❌ 鏡像構建失敗！"
    exit 1
fi
echo ""

# 步驟 9: 驗證鏡像是否存在
echo "🔍 步驟 9: 驗證鏡像是否存在..."
if docker images | grep -q "redpacket/backend"; then
    echo "✅ backend 鏡像已存在"
    docker images | grep "redpacket/backend"
else
    echo "❌ backend 鏡像不存在！"
    exit 1
fi
echo ""

# 步驟 10: 使用 --env-file 啟動所有服務
echo "🚀 步驟 10: 使用 --env-file 啟動所有服務..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ 服務啟動命令執行成功"
else
    echo "❌ 服務啟動失敗！"
    exit 1
fi
echo ""

# 步驟 11: 等待服務啟動
echo "⏳ 步驟 11: 等待服務啟動（30秒）..."
sleep 30
echo ""

# 步驟 12: 檢查服務狀態
echo "📊 步驟 12: 檢查服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 13: 檢查 web_admin 日誌（確認 pandas 已安裝）
echo "📋 步驟 13: 檢查 web_admin 日誌（最後 30 行）..."
docker compose -f docker-compose.production.yml logs web_admin --tail 30 | grep -i "pandas\|openpyxl\|error\|failed\|ModuleNotFound" || echo "✅ 未發現 pandas 或 openpyxl 錯誤"
echo ""

# 步驟 14: 完整日誌（用於診斷）
echo "📋 步驟 14: 檢查 web_admin 完整啟動日誌（最後 20 行）..."
docker compose -f docker-compose.production.yml logs web_admin --tail 20
echo ""

# 步驟 15: 測試健康檢查
echo "🧪 步驟 15: 測試健康檢查..."
echo ""
echo "Web Admin (8000):"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"

echo "MiniApp API (8080):"
curl -s http://127.0.0.1:8080/healthz && echo "" || echo "⚠️  MiniApp API 健康檢查失敗"
echo ""

echo "===================================="
echo "✅ 修復完成！"
echo "===================================="
echo ""
echo "如果服務正常運行，您應該看到："
echo "  - 所有容器狀態為 'Up' 或 'healthy'"
echo "  - 健康檢查返回 {'ok': true}"
echo "  - 日誌中沒有 'ModuleNotFoundError' 錯誤"
echo ""

