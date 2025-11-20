#!/bin/bash
# 完整修復方案 - 解決環境變量和網絡問題

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 完整修復方案"
echo "===================================="
echo ""

# 步驟 1: 確保 .env.production 存在
echo "📝 步驟 1: 檢查 .env.production..."
if [ ! -f .env.production ]; then
    echo "⚠️  .env.production 不存在，嘗試恢復..."
    if [ -f /tmp/.env.production.bak ]; then
        cp /tmp/.env.production.bak .env.production
        sed -i 's/NOWPAYMENTS_IPN_URLhttps/NOWPAYMENTS_IPN_URL=https/g' .env.production
        echo "✅ .env.production 已恢復並修復"
    else
        echo "❌ 無法恢復 .env.production，請手動創建"
        exit 1
    fi
else
    echo "✅ .env.production 存在"
fi

# 驗證環境變量
echo ""
echo "🔍 驗證環境變量..."
grep -q "POSTGRES_USER=" .env.production && echo "✅ POSTGRES_USER 已設置" || echo "❌ POSTGRES_USER 未設置"
grep -q "POSTGRES_DB=" .env.production && echo "✅ POSTGRES_DB 已設置" || echo "❌ POSTGRES_DB 未設置"
grep -q "POSTGRES_PASSWORD=" .env.production && echo "✅ POSTGRES_PASSWORD 已設置" || echo "❌ POSTGRES_PASSWORD 未設置"

# 步驟 2: 停止所有服務
echo ""
echo "🛑 步驟 2: 停止所有服務..."
docker compose -f docker-compose.production.yml down 2>/dev/null || true
echo "✅ 服務已停止"

# 步驟 3: 設置 Docker 鏡像加速器（解決網絡問題）
echo ""
echo "🌐 步驟 3: 設置 Docker 鏡像加速器..."
if [ ! -f /etc/docker/daemon.json ]; then
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json > /dev/null <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    echo "✅ Docker 鏡像加速器已設置並重啟"
    sleep 5
else
    echo "⚠️  Docker 鏡像加速器已存在"
fi

# 步驟 4: 手動拉取基礎鏡像（處理網絡超時）
echo ""
echo "📥 步驟 4: 手動拉取基礎鏡像..."
echo "  拉取 postgres:15-alpine..."
docker pull postgres:15-alpine || echo "⚠️  postgres 拉取失敗，將在構建時重試"

echo "  拉取 redis:7-alpine..."
docker pull redis:7-alpine || echo "⚠️  redis 拉取失敗，將在構建時重試"

echo "  拉取 prom/prometheus:latest..."
docker pull prom/prometheus:latest || echo "⚠️  prometheus 拉取失敗，將在構建時重試"

echo "  拉取 grafana/grafana:latest..."
docker pull grafana/grafana:latest || echo "⚠️  grafana 拉取失敗，將在構建時重試"

# 步驟 5: 構建並啟動服務
echo ""
echo "🔨 步驟 5: 構建並啟動服務..."
echo "  使用環境變量文件: .env.production"

# 使用 --env-file 明確指定環境變量文件
docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache || {
    echo "⚠️  構建失敗，嘗試不使用 --no-cache..."
    docker compose --env-file .env.production -f docker-compose.production.yml build
}

docker compose --env-file .env.production -f docker-compose.production.yml up -d

echo ""
echo "⏳ 等待服務啟動（30秒）..."
sleep 30

# 步驟 6: 檢查服務狀態
echo ""
echo "📊 步驟 6: 檢查服務狀態..."
docker compose -f docker-compose.production.yml ps

# 步驟 7: 測試健康檢查
echo ""
echo "🧪 步驟 7: 測試健康檢查..."
echo ""
echo "Web Admin:"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"

echo "MiniApp API:"
curl -s http://127.0.0.1:8080/healthz && echo "" || echo "⚠️  MiniApp API 健康檢查失敗"

# 步驟 8: 顯示日誌（如果有問題）
echo ""
echo "📋 步驟 8: 最近的日誌（最後20行）..."
docker compose -f docker-compose.production.yml logs --tail 20

echo ""
echo "===================================="
echo "✅ 修復完成！"
echo "===================================="
echo ""
echo "如果服務未運行，請檢查日誌："
echo "  docker compose -f docker-compose.production.yml logs -f"
echo ""

