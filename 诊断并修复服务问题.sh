#!/bin/bash
# 診斷並修復服務問題

set -e

cd /opt/redpacket

echo "===================================="
echo "🔍 診斷並修復服務問題"
echo "===================================="
echo ""

# 步驟 1: 檢查所有服務狀態
echo "📊 步驟 1: 檢查所有服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 2: 檢查 redis 日誌（為什麼在重啟）
echo "📋 步驟 2: 檢查 redis 日誌（最後 30 行）..."
docker compose -f docker-compose.production.yml logs redis --tail 30
echo ""

# 步驟 3: 檢查 web_admin 日誌（為什麼健康檢查失敗）
echo "📋 步驟 3: 檢查 web_admin 日誌（最後 50 行）..."
docker compose -f docker-compose.production.yml logs web_admin --tail 50
echo ""

# 步驟 4: 檢查 bot 日誌
echo "📋 步驟 4: 檢查 bot 日誌（最後 30 行）..."
docker compose -f docker-compose.production.yml logs bot --tail 30
echo ""

# 步驟 5: 測試健康檢查（詳細輸出）
echo "🧪 步驟 5: 測試健康檢查（詳細輸出）..."
echo ""
echo "Web Admin (8000):"
curl -v http://127.0.0.1:8000/healthz 2>&1 || echo "⚠️  Web Admin 健康檢查失敗"
echo ""
echo "MiniApp API (8080):"
curl -v http://127.0.0.1:8080/healthz 2>&1 || echo "⚠️  MiniApp API 健康檢查失敗"
echo ""

# 步驟 6: 檢查 redis 容器詳細狀態
echo "🔍 步驟 6: 檢查 redis 容器詳細狀態..."
docker inspect redpacket_redis | grep -A 10 "State" || echo "⚠️  無法獲取 redis 狀態"
echo ""

# 步驟 7: 等待更長時間並再次檢查
echo "⏳ 步驟 7: 等待服務完全啟動（再等 30 秒）..."
sleep 30
echo ""

# 步驟 8: 再次檢查服務狀態
echo "📊 步驟 8: 再次檢查服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 9: 再次測試健康檢查
echo "🧪 步驟 9: 再次測試健康檢查..."
echo ""
echo "Web Admin (8000):"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"

echo "MiniApp API (8080):"
curl -s http://127.0.0.1:8080/healthz && echo "" || echo "⚠️  MiniApp API 健康檢查失敗"
echo ""

# 步驟 10: 檢查端口是否被監聽
echo "🔍 步驟 10: 檢查端口是否被監聽..."
echo ""
echo "端口 8000 (Web Admin):"
docker exec redpacket_web_admin netstat -tlnp 2>/dev/null | grep :8000 || echo "⚠️  端口 8000 未被監聽"

echo "端口 8080 (MiniApp API):"
docker exec redpacket_miniapp_api netstat -tlnp 2>/dev/null | grep :8080 || echo "⚠️  端口 8080 未被監聽"

echo "端口 6379 (Redis):"
docker exec redpacket_redis redis-cli ping 2>/dev/null || echo "⚠️  Redis 無法連接"
echo ""

echo "===================================="
echo "✅ 診斷完成"
echo "===================================="

