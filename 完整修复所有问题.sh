#!/bin/bash
# 完整修復所有問題

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 完整修復所有問題"
echo "===================================="
echo ""

# 步驟 1: 拉取最新代碼
echo "📥 步驟 1: 拉取最新代碼..."
git pull origin master || echo "⚠️  Git 拉取失敗，繼續使用本地代碼..."
echo "✅ 代碼已更新"
echo ""

# 步驟 2: 停止所有服務（包括手動啟動的 Redis）
echo "🛑 步驟 2: 停止所有服務（包括手動啟動的 Redis）..."
docker compose -f docker-compose.production.yml down 2>/dev/null || true

# 強制停止手動啟動的 Redis 容器（如果存在）
docker stop redpacket_redis 2>/dev/null || true
docker rm redpacket_redis 2>/dev/null || true

# 清理所有容器
docker ps -a | grep redpacket | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true

echo "✅ 服務已停止"
echo ""

# 步驟 3: 驗證 Redis 配置
echo "🔍 步驟 3: 驗證 Redis 配置..."
if grep -q "^REDIS_PASSWORD=" .env.production 2>/dev/null; then
    REDIS_PASS=$(grep "^REDIS_PASSWORD=" .env.production | cut -d'=' -f2)
    if [ -z "$REDIS_PASS" ] || [ "$REDIS_PASS" = "" ]; then
        echo "✅ REDIS_PASSWORD 為空，Redis 將不使用密碼"
    else
        echo "⚠️  REDIS_PASSWORD 已設置，值為: ${REDIS_PASS:0:3}***"
    fi
else
    echo "✅ REDIS_PASSWORD 未設置，Redis 不使用密碼"
fi
echo ""

# 步驟 4: 確認 requirements.txt 包含所有依賴
echo "🔍 步驟 4: 確認 requirements.txt 包含所有依賴..."
if ! grep -q "^requests==" requirements.txt; then
    echo "⚠️  requests 缺失，正在添加..."
    echo "requests==2.32.3" >> requirements.txt
fi
if ! grep -q "^pandas==" requirements.txt; then
    echo "⚠️  pandas 缺失，正在添加..."
    echo "pandas==2.2.3" >> requirements.txt
fi
if ! grep -q "^openpyxl==" requirements.txt; then
    echo "⚠️  openpyxl 缺失，正在添加..."
    echo "openpyxl==3.1.5" >> requirements.txt
fi
echo "✅ 依賴檢查完成"
grep -E "^requests==|^pandas==|^openpyxl==" requirements.txt
echo ""

# 步驟 5: 清理 Docker 鏡像（確保使用最新代碼）
echo "🗑️  步驟 5: 清理 Docker 鏡像..."
docker images | grep redpacket | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
sleep 2
echo "✅ 鏡像清理完成"
echo ""

# 步驟 6: 重新構建 backend 鏡像
echo "🔨 步驟 6: 重新構建 backend 鏡像（包含所有依賴）..."
echo "   這可能需要 3-5 分鐘，請耐心等待..."
docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache web_admin

if [ $? -eq 0 ]; then
    echo "✅ 鏡像構建成功！"
else
    echo "❌ 鏡像構建失敗！"
    exit 1
fi
echo ""

# 步驟 7: 驗證鏡像是否存在
echo "🔍 步驟 7: 驗證鏡像是否存在..."
docker images | grep "redpacket/backend" || (echo "❌ backend 鏡像不存在！" && exit 1)
echo "✅ backend 鏡像已存在"
echo ""

# 步驟 8: 啟動所有服務（使用 docker-compose，確保正確配置）
echo "🚀 步驟 8: 啟動所有服務（使用 docker-compose，確保 Redis 正確配置）..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ 服務啟動命令執行成功"
else
    echo "❌ 服務啟動失敗！"
    exit 1
fi
echo ""

# 步驟 9: 等待服務啟動
echo "⏳ 步驟 9: 等待服務啟動（60秒，給足夠時間讓健康檢查完成）..."
sleep 60
echo ""

# 步驟 10: 檢查服務狀態
echo "📊 步驟 10: 檢查服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 11: 檢查關鍵服務日誌
echo "📋 步驟 11: 檢查關鍵服務日誌..."
echo ""
echo "--- Redis (最後 10 行) ---"
docker compose -f docker-compose.production.yml logs redis --tail 10 || true
echo ""
echo "--- Web Admin (最後 30 行) ---"
docker compose -f docker-compose.production.yml logs web_admin --tail 30 || true
echo ""

# 步驟 12: 驗證關鍵依賴是否已安裝
echo "🔍 步驟 12: 驗證關鍵依賴是否已安裝..."
echo ""
echo "Web Admin 容器中的 requests:"
docker exec redpacket_web_admin python3 -c "import requests; print(f'✅ requests: {requests.__version__}')" 2>&1 || echo "❌ requests 未安裝"

echo ""
echo "Web Admin 容器中的 pandas:"
docker exec redpacket_web_admin python3 -c "import pandas; print(f'✅ pandas: {pandas.__version__}')" 2>&1 || echo "❌ pandas 未安裝"
echo ""

# 步驟 13: 測試健康檢查
echo "🧪 步驟 13: 測試健康檢查..."
echo ""
echo "Web Admin (8000):"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"

echo "MiniApp API (8080):"
curl -s http://127.0.0.1:8080/healthz && echo "" || echo "⚠️  MiniApp API 健康檢查失敗"
echo ""

# 步驟 14: 如果 Web Admin 仍有問題，檢查完整日誌
if ! curl -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
    echo "⚠️  Web Admin 健康檢查失敗，查看完整日誌..."
    echo ""
    echo "--- Web Admin 完整啟動日誌 ---"
    docker compose -f docker-compose.production.yml logs web_admin | tail -50
    echo ""
fi

echo "===================================="
echo "✅ 修復完成！"
echo "===================================="
echo ""
echo "如果服務仍有問題，請檢查上面的日誌輸出"

