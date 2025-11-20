#!/bin/bash
# 恢復配置並開始部署

cd /opt/redpacket

echo "===================================="
echo "✅ 文件已修復，現在恢復配置並部署"
echo "===================================="
echo ""

# 步驟 1: 恢復 .env.production
echo "📝 步驟 1: 恢復 .env.production..."
if [ -f /tmp/.env.production.bak ]; then
    cp /tmp/.env.production.bak .env.production
    # 修復缺少等號的問題
    sed -i 's/NOWPAYMENTS_IPN_URLhttps/NOWPAYMENTS_IPN_URL=https/g' .env.production
    echo "✅ .env.production 已恢復並修復"
else
    echo "⚠️  未找到備份文件 /tmp/.env.production.bak"
    echo "   請手動配置 .env.production"
fi
echo ""

# 步驟 2: 驗證關鍵文件
echo "📋 步驟 2: 驗證關鍵文件..."
[ -f docker-compose.production.yml ] && echo "✅ docker-compose.production.yml 存在" || echo "❌ docker-compose.production.yml 不存在"
[ -d deploy ] && echo "✅ deploy/ 目錄存在" || echo "❌ deploy/ 目錄不存在"
[ -f .env.production ] && echo "✅ .env.production 存在" || echo "❌ .env.production 不存在"
[ -d frontend-next ] && echo "✅ frontend-next/ 目錄存在" || echo "❌ frontend-next/ 目錄不存在"
echo ""

# 步驟 3: 構建 Docker 鏡像
echo "🔨 步驟 3: 構建 Docker 鏡像..."
docker compose -f docker-compose.production.yml build
echo ""

# 步驟 4: 啟動所有服務
echo "🚀 步驟 4: 啟動所有服務..."
docker compose -f docker-compose.production.yml up -d
echo ""

# 步驟 5: 等待服務啟動
echo "⏳ 步驟 5: 等待服務啟動（30秒）..."
sleep 30
echo ""

# 步驟 6: 檢查服務狀態
echo "📊 步驟 6: 檢查服務狀態..."
docker compose -f docker-compose.production.yml ps
echo ""

# 步驟 7: 測試健康檢查
echo "🧪 步驟 7: 測試健康檢查..."
curl -s http://127.0.0.1:8000/healthz || echo "⚠️  Web Admin 健康檢查失敗"
curl -s http://127.0.0.1:8080/healthz || echo "⚠️  MiniApp API 健康檢查失敗"
echo ""

echo "===================================="
echo "✅ 部署完成！"
echo "===================================="
echo ""
echo "查看日誌："
echo "  docker compose -f docker-compose.production.yml logs -f"
echo ""

