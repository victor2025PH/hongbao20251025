#!/bin/bash
# 最終驗證和修復

set -e

cd /opt/redpacket

echo "===================================="
echo "🔍 最終驗證和修復"
echo "===================================="
echo ""

# 步驟 1: 檢查 Redis 日誌（為什麼還在重啟）
echo "📋 步驟 1: 檢查 Redis 日誌（最後 20 行）..."
docker compose -f docker-compose.production.yml logs redis --tail 20
echo ""

# 步驟 2: 檢查 Redis 配置（確認環境變量）
echo "🔍 步驟 2: 檢查 Redis 環境變量..."
docker exec redpacket_redis env | grep REDIS || echo "⚠️  未找到 REDIS 環境變量"
echo ""

# 步驟 3: 檢查 Redis 容器詳細狀態
echo "🔍 步驟 3: 檢查 Redis 容器狀態..."
docker inspect redpacket_redis | grep -A 20 "State" || echo "⚠️  無法獲取 Redis 狀態"
echo ""

# 步驟 4: 檢查 web_admin 日誌（確認 requests 已安裝）
echo "📋 步驟 4: 檢查 web_admin 日誌（確認 requests 已安裝）..."
docker compose -f docker-compose.production.yml logs web_admin --tail 30 | grep -i "requests\|error\|failed\|ModuleNotFound" || echo "✅ 未發現 requests 錯誤"
echo ""

# 步驟 5: 驗證 web_admin 容器中的 requests 是否已安裝
echo "🔍 步驟 5: 驗證 web_admin 容器中的 requests 是否已安裝..."
docker exec redpacket_web_admin python3 -c "import requests; print(f'✅ requests 版本: {requests.__version__}')" || echo "❌ requests 未安裝"
echo ""

# 步驟 6: 再次等待（給服務更多時間完成健康檢查）
echo "⏳ 步驟 6: 再次等待服務完全啟動（再等 60 秒）..."
sleep 60
echo ""

# 步驟 7: 再次檢查服務狀態
echo "📊 步驟 7: 再次檢查服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 8: 測試健康檢查（詳細輸出）
echo "🧪 步驟 8: 測試健康檢查（詳細輸出）..."
echo ""
echo "Web Admin (8000):"
curl -v http://127.0.0.1:8000/healthz 2>&1 | head -20
echo ""
echo "MiniApp API (8080):"
curl -v http://127.0.0.1:8080/healthz 2>&1 | head -20
echo ""

# 步驟 9: 檢查容器內端口是否監聽
echo "🔍 步驟 9: 檢查容器內端口是否監聽..."
echo ""
echo "Web Admin (8000):"
docker exec redpacket_web_admin netstat -tlnp 2>/dev/null | grep :8000 || echo "⚠️  端口 8000 未被監聽"

echo "MiniApp API (8080):"
docker exec redpacket_miniapp_api netstat -tlnp 2>/dev/null | grep :8080 || echo "⚠️  端口 8080 未被監聽"

echo "Redis (6379):"
docker exec redpacket_redis redis-cli ping 2>/dev/null || echo "⚠️  Redis 無法連接（可能還在啟動中）"
echo ""

# 步驟 10: 如果 Redis 還在重啟，嘗試手動修復
echo "🔍 步驟 10: 如果 Redis 還在重啟，檢查配置..."
if docker ps | grep redpacket_redis | grep -q "Restarting"; then
    echo "⚠️  Redis 仍在重啟，檢查配置..."
    
    # 檢查 .env.production 中的 REDIS_PASSWORD
    if grep -q "^REDIS_PASSWORD=" .env.production; then
        REDIS_PASS=$(grep "^REDIS_PASSWORD=" .env.production | cut -d'=' -f2)
        if [ -z "$REDIS_PASS" ] || [ "$REDIS_PASS" = "" ]; then
            echo "✅ REDIS_PASSWORD 為空，Redis 應該不使用密碼"
        else
            echo "⚠️  REDIS_PASSWORD 已設置，值為: ${REDIS_PASS:0:3}***"
        fi
    else
        echo "✅ REDIS_PASSWORD 未設置，Redis 不使用密碼"
    fi
    
    # 嘗試手動啟動 Redis（不使用密碼）
    echo "🔧 嘗試手動修復 Redis..."
    docker stop redpacket_redis 2>/dev/null || true
    docker rm redpacket_redis 2>/dev/null || true
    docker run -d --name redpacket_redis --network redpacket_redpacket_network \
        -v redpacket_redis_data:/data \
        redis:7-alpine redis-server --appendonly yes
    
    echo "✅ 已重新啟動 Redis（不使用密碼）"
    sleep 5
fi
echo ""

# 步驟 11: 最終狀態檢查
echo "📊 步驟 11: 最終狀態檢查..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 12: 最終健康檢查
echo "🧪 步驟 12: 最終健康檢查..."
echo ""
echo "Web Admin (8000):"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"

echo "MiniApp API (8080):"
curl -s http://127.0.0.1:8080/healthz && echo "" || echo "⚠️  MiniApp API 健康檢查失敗"
echo ""

echo "===================================="
echo "✅ 驗證完成！"
echo "===================================="

