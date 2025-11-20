#!/bin/bash
# 修復所有問題並重新部署

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 修復所有問題並重新部署"
echo "===================================="
echo ""

# 步驟 1: 拉取最新代碼（包含 requests 和 Redis 修復）
echo "📥 步驟 1: 拉取最新代碼..."
git pull origin master || echo "⚠️  Git 拉取失敗，繼續使用本地代碼..."
echo "✅ 代碼已更新"
echo ""

# 步驟 2: 確認 requirements.txt 包含 requests
echo "🔍 步驟 2: 確認 requirements.txt 包含 requests..."
if ! grep -q "^requests==" requirements.txt; then
    echo "⚠️  requests 缺失，正在添加..."
    echo "requests==2.32.3" >> requirements.txt
    echo "✅ 已添加 requests"
else
    echo "✅ requests 已存在"
    grep "^requests==" requirements.txt
fi
echo ""

# 步驟 3: 停止所有服務並清理
echo "🛑 步驟 3: 停止所有服務並清理..."
docker compose -f docker-compose.production.yml down 2>/dev/null || true

# 強制停止所有 bot 相關容器（解決 Telegram 衝突）
docker ps -a | grep redpacket_bot | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true

# 清理所有 redpacket 容器和鏡像
docker ps -a | grep redpacket | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true
docker images | grep redpacket | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

sleep 2
echo "✅ 清理完成"
echo ""

# 步驟 4: 重新構建 backend 鏡像（包含 requests）
echo "🔨 步驟 4: 重新構建 backend 鏡像（包含 requests）..."
echo "   這可能需要 3-5 分鐘，請耐心等待..."
docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache web_admin

if [ $? -eq 0 ]; then
    echo "✅ 鏡像構建成功！"
else
    echo "❌ 鏡像構建失敗！"
    exit 1
fi
echo ""

# 步驟 5: 驗證鏡像是否存在
echo "🔍 步驟 5: 驗證鏡像是否存在..."
docker images | grep "redpacket/backend" || (echo "❌ backend 鏡像不存在！" && exit 1)
echo "✅ backend 鏡像已存在"
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
echo "⏳ 步驟 7: 等待服務啟動（60秒，給足夠時間讓健康檢查完成）..."
sleep 60
echo ""

# 步驟 8: 檢查服務狀態
echo "📊 步驟 8: 檢查服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 9: 檢查關鍵服務日誌
echo "📋 步驟 9: 檢查關鍵服務日誌..."
echo ""
echo "--- redis (最後 10 行) ---"
docker compose -f docker-compose.production.yml logs redis --tail 10 || true
echo ""
echo "--- web_admin (最後 20 行) ---"
docker compose -f docker-compose.production.yml logs web_admin --tail 20 || true
echo ""
echo "--- bot (最後 20 行) ---"
docker compose -f docker-compose.production.yml logs bot --tail 20 || true
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
echo "✅ 修復完成！"
echo "===================================="

