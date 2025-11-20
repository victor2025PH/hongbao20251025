#!/bin/bash
# 診斷服務失敗原因

set -e

cd /opt/redpacket

echo "===================================="
echo "🔍 診斷服務失敗原因"
echo "===================================="
echo ""

# 步驟 1: 檢查容器狀態
echo "📊 步驟 1: 檢查容器狀態..."
echo ""
docker compose -f docker-compose.production.yml ps
echo ""

# 步驟 2: 檢查 web_admin 容器狀態
echo "📋 步驟 2: 檢查 web_admin 容器詳細狀態..."
echo ""
docker ps -a | grep web_admin || echo "⚠️  未找到 web_admin 容器"
echo ""

# 步驟 3: 檢查 web_admin 日誌（最後 30 行）
echo "📋 步驟 3: 檢查 web_admin 日誌（最後 30 行）..."
echo ""
docker compose -f docker-compose.production.yml logs web_admin --tail 30
echo ""

# 步驟 4: 檢查構建是否成功
echo "🔍 步驟 4: 檢查 web_admin 鏡像是否存在..."
echo ""
docker images | grep web_admin || echo "⚠️  web_admin 鏡像不存在"
echo ""

# 步驟 5: 檢查 requirements.txt 是否包含 pandas
echo "🔍 步驟 5: 檢查 requirements.txt 是否包含 pandas 和 openpyxl..."
echo ""
grep -E "pandas|openpyxl" requirements.txt || echo "⚠️  未找到 pandas 或 openpyxl"
echo ""

# 步驟 6: 檢查端口是否被占用
echo "🔍 步驟 6: 檢查端口 8000 是否被占用..."
echo ""
sudo netstat -tlnp | grep :8000 || echo "✅ 端口 8000 未被占用"
echo ""

# 步驟 7: 測試健康檢查（詳細輸出）
echo "🧪 步驟 7: 測試健康檢查（詳細輸出）..."
echo ""
curl -v http://127.0.0.1:8000/healthz || echo "⚠️  健康檢查失敗"
echo ""

echo "===================================="
echo "✅ 診斷完成"
echo "===================================="

