#!/bin/bash
# 解決服務未啟動問題

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 解決服務未啟動問題"
echo "===================================="
echo ""

# 步驟 1: 確保 .env.production 存在且格式正確
echo "📝 步驟 1: 檢查 .env.production..."
if [ ! -f .env.production ]; then
    echo "❌ .env.production 不存在！"
    if [ -f /tmp/.env.production.bak ]; then
        cp /tmp/.env.production.bak .env.production
        sed -i 's/NOWPAYMENTS_IPN_URLhttps/NOWPAYMENTS_IPN_URL=https/g' .env.production
        echo "✅ .env.production 已恢復"
    else
        echo "❌ 無法恢復 .env.production，請手動創建"
        exit 1
    fi
else
    echo "✅ .env.production 存在"
fi

# 驗證環境變量格式
echo ""
echo "🔍 驗證環境變量格式..."
if grep -q "^POSTGRES_USER=" .env.production; then
    echo "✅ POSTGRES_USER 格式正確"
else
    echo "❌ POSTGRES_USER 格式錯誤或不存在"
fi

if grep -q "^POSTGRES_DB=" .env.production; then
    echo "✅ POSTGRES_DB 格式正確"
else
    echo "❌ POSTGRES_DB 格式錯誤或不存在"
fi

if grep -q "^POSTGRES_PASSWORD=" .env.production; then
    echo "✅ POSTGRES_PASSWORD 格式正確"
else
    echo "❌ POSTGRES_PASSWORD 格式錯誤或不存在"
fi

echo ""
echo "環境變量值（脫敏）："
grep "^POSTGRES_USER=" .env.production | sed 's/=.*/=***/'
grep "^POSTGRES_DB=" .env.production | sed 's/=.*/=***/'
grep "^POSTGRES_PASSWORD=" .env.production | sed 's/=.*/=***/'

# 步驟 2: 檢查是否有容器在運行
echo ""
echo "📊 步驟 2: 檢查容器狀態..."
if docker ps -a | grep -q redpacket; then
    echo "⚠️  發現現有容器："
    docker ps -a | grep redpacket
    echo ""
    echo "停止並刪除現有容器..."
    docker compose -f docker-compose.production.yml down --remove-orphans 2>/dev/null || true
else
    echo "✅ 沒有現有容器"
fi

# 步驟 3: 使用 --env-file 明確指定環境變量文件啟動服務
echo ""
echo "🚀 步驟 3: 使用 --env-file 啟動服務..."
echo "  使用環境變量文件: .env.production"

# 先檢查配置文件是否正確
echo ""
echo "🔍 檢查配置（使用環境變量文件）..."
docker compose --env-file .env.production -f docker-compose.production.yml config > /tmp/docker-compose-config.yml 2>&1 || {
    echo "❌ 配置文件檢查失敗，查看錯誤："
    cat /tmp/docker-compose-config.yml
    exit 1
}

# 查看環境變量是否被正確讀取
echo ""
echo "驗證環境變量是否被讀取："
docker compose --env-file .env.production -f docker-compose.production.yml config 2>/dev/null | grep "POSTGRES_USER" | head -1
docker compose --env-file .env.production -f docker-compose.production.yml config 2>/dev/null | grep "POSTGRES_DB" | head -1

# 啟動服務
echo ""
echo "🔨 啟動服務..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ 服務啟動命令執行成功"
else
    echo "❌ 服務啟動失敗！"
    echo ""
    echo "查看詳細錯誤："
    docker compose --env-file .env.production -f docker-compose.production.yml up -d 2>&1 | tail -20
    exit 1
fi

# 步驟 4: 等待服務啟動
echo ""
echo "⏳ 步驟 4: 等待服務啟動（30秒）..."
sleep 30

# 步驟 5: 檢查服務狀態
echo ""
echo "📊 步驟 5: 檢查服務狀態..."
docker compose -f docker-compose.production.yml ps

# 步驟 6: 檢查服務日誌
echo ""
echo "📋 步驟 6: 檢查服務日誌（最後30行）..."
docker compose -f docker-compose.production.yml logs --tail 30

# 步驟 7: 測試健康檢查
echo ""
echo "🧪 步驟 7: 測試健康檢查..."
echo ""
echo "Web Admin:"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"

echo "MiniApp API:"
curl -s http://127.0.0.1:8080/healthz && echo "" || echo "⚠️  MiniApp API 健康檢查失敗"

echo ""
echo "===================================="
echo "✅ 修復完成！"
echo "===================================="
echo ""

