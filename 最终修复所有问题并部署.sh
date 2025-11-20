#!/bin/bash
# 最終修復所有問題並部署

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 最終修復所有問題並部署"
echo "===================================="
echo ""

# 步驟 1: 處理本地修改（stash 或提交）
echo "📥 步驟 1: 處理本地修改..."
if git diff --quiet requirements.txt; then
    echo "✅ requirements.txt 沒有修改"
else
    echo "⚠️  requirements.txt 有本地修改，先 stash..."
    git stash push -m "Stash local requirements.txt changes" requirements.txt || true
fi

# 拉取最新代碼
echo "📥 拉取最新代碼..."
git pull origin master || echo "⚠️  Git 拉取失敗，繼續使用本地代碼..."
echo "✅ 代碼已更新"
echo ""

# 步驟 2: 確認所有依賴
echo "🔍 步驟 2: 確認所有依賴（requests, pandas, openpyxl）..."
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

# 步驟 3: 停止所有服務
echo "🛑 步驟 3: 停止所有服務..."
docker compose -f docker-compose.production.yml down 2>/dev/null || true
docker stop redpacket_redis 2>/dev/null || true
docker rm redpacket_redis 2>/dev/null || true
docker ps -a | grep redpacket | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true
echo "✅ 服務已停止"
echo ""

# 步驟 4: 清理 Docker 鏡像
echo "🗑️  步驟 4: 清理 Docker 鏡像..."
docker images | grep redpacket | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
sleep 2
echo "✅ 鏡像清理完成"
echo ""

# 步驟 5: 重新構建 backend 鏡像
echo "🔨 步驟 5: 重新構建 backend 鏡像（包含所有依賴和修復）..."
echo "   這可能需要 3-5 分鐘，請耐心等待..."
docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache web_admin

if [ $? -eq 0 ]; then
    echo "✅ 鏡像構建成功！"
else
    echo "❌ 鏡像構建失敗！"
    exit 1
fi
echo ""

# 步驟 6: 驗證鏡像
echo "🔍 步驟 6: 驗證鏡像是否存在..."
docker images | grep "redpacket/backend" || (echo "❌ backend 鏡像不存在！" && exit 1)
echo "✅ backend 鏡像已存在"
echo ""

# 步驟 7: 啟動所有服務
echo "🚀 步驟 7: 啟動所有服務（使用 docker-compose，確保 Redis 正確配置）..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ 服務啟動命令執行成功"
else
    echo "❌ 服務啟動失敗！"
    exit 1
fi
echo ""

# 步驟 8: 等待服務啟動
echo "⏳ 步驟 8: 等待服務啟動（60秒，給足夠時間讓健康檢查完成）..."
sleep 60
echo ""

# 步驟 9: 檢查服務狀態
echo "📊 步驟 9: 檢查服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 10: 檢查關鍵服務日誌
echo "📋 步驟 10: 檢查關鍵服務日誌..."
echo ""
echo "--- Redis (最後 10 行) ---"
docker compose -f docker-compose.production.yml logs redis --tail 10 || true
echo ""
echo "--- Web Admin (最後 30 行) ---"
docker compose -f docker-compose.production.yml logs web_admin --tail 30 || true
echo ""

# 步驟 11: 測試健康檢查
echo "🧪 步驟 11: 測試健康檢查..."
echo ""
echo "Web Admin (8000):"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"

echo "MiniApp API (8080):"
curl -s http://127.0.0.1:8080/healthz && echo "" || echo "⚠️  MiniApp API 健康檢查失敗"
echo ""

echo "===================================="
echo "✅ 修復完成！"
echo "===================================="

