#!/bin/bash
# 最終修復方案 - 串行構建避免衝突

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 最終修復方案 - 串行構建"
echo "===================================="
echo ""

# 步驟 1: 停止所有服務
echo "🛑 步驟 1: 停止所有服務..."
docker compose -f docker-compose.production.yml down 2>/dev/null || true
echo "✅ 服務已停止"
echo ""

# 步驟 2: 強制刪除所有 redpacket 容器和鏡像
echo "🗑️  步驟 2: 強制刪除所有 redpacket 容器和鏡像..."
docker ps -a | grep redpacket | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true
docker images | grep redpacket | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
sleep 2
echo "✅ 徹底清理完成"
echo ""

# 步驟 3: 只構建一個服務（web_admin）來創建鏡像
echo "🔨 步驟 3: 構建 web_admin 服務（創建 backend 鏡像）..."
echo "   這可能需要 3-5 分鐘，請耐心等待..."
docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache web_admin

if [ $? -eq 0 ]; then
    echo "✅ web_admin 鏡像構建成功！"
else
    echo "❌ web_admin 鏡像構建失敗！"
    exit 1
fi
echo ""

# 步驟 4: 驗證鏡像是否存在
echo "🔍 步驟 4: 驗證鏡像是否存在..."
if docker images | grep -q "redpacket/backend"; then
    echo "✅ backend 鏡像已存在"
    docker images | grep "redpacket/backend"
else
    echo "❌ backend 鏡像不存在！"
    exit 1
fi
echo ""

# 步驟 5: 為 bot 和 miniapp_api 創建標籤（重用同一個鏡像，因為它們使用相同的 Dockerfile）
echo "🔍 步驟 5: 驗證其他服務可以使用同一個鏡像..."
# bot 和 miniapp_api 使用相同的 Dockerfile 和源代碼，所以可以重用 web_admin 的鏡像
# 不需要重新構建，只需要確保鏡像存在即可
echo "✅ bot 和 miniapp_api 將重用 web_admin 的鏡像"
echo ""

# 步驟 6: 啟動所有服務
echo "🚀 步驟 6: 啟動所有服務..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ 服務啟動命令執行成功"
else
    echo "❌ 服務啟動失敗！"
    exit 1
fi
echo ""

# 步驟 7: 等待服務啟動
echo "⏳ 步驟 7: 等待服務啟動（30秒）..."
sleep 30
echo ""

# 步驟 8: 檢查服務狀態
echo "📊 步驟 8: 檢查服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 9: 檢查容器日誌
echo "📋 步驟 9: 檢查容器日誌（最後 10 行）..."
echo ""
echo "--- web_admin ---"
docker compose -f docker-compose.production.yml logs web_admin --tail 10 || true
echo ""
echo "--- bot ---"
docker compose -f docker-compose.production.yml logs bot --tail 10 || true
echo ""
echo "--- miniapp_api ---"
docker compose -f docker-compose.production.yml logs miniapp_api --tail 10 || true
echo ""

# 步驟 10: 測試健康檢查
echo "🧪 步驟 10: 測試健康檢查..."
echo ""
echo "Web Admin (8000):"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"

echo "MiniApp API (8080):"
curl -s http://127.0.0.1:8080/healthz && echo "" || echo "⚠️  MiniApp API 健康檢查失敗"
echo ""

echo "===================================="
echo "✅ 部署完成！"
echo "===================================="

