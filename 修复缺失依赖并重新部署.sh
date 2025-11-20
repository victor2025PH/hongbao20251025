#!/bin/bash
# 修復缺失依賴並重新部署

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 修復缺失依賴並重新部署"
echo "===================================="
echo ""

# 步驟 1: 拉取最新代碼（包含修復的 requirements.txt）
echo "📥 步驟 1: 拉取最新代碼..."
git pull origin master || {
    echo "❌ Git 拉取失敗！"
    exit 1
}
echo "✅ 代碼已更新"
echo ""

# 步驟 2: 檢查 requirements.txt 是否包含 pandas
echo "🔍 步驟 2: 檢查 requirements.txt..."
if grep -q "pandas" requirements.txt; then
    echo "✅ pandas 已在 requirements.txt 中"
else
    echo "❌ pandas 不在 requirements.txt 中，手動添加..."
    echo "pandas==2.2.3" >> requirements.txt
    echo "openpyxl==3.1.5" >> requirements.txt
    echo "✅ 已添加 pandas 和 openpyxl"
fi

echo ""
grep -E "pandas|openpyxl" requirements.txt || echo "⚠️  未找到 pandas 或 openpyxl"

# 步驟 3: 停止現有服務
echo ""
echo "🛑 步驟 3: 停止現有服務..."
docker compose -f docker-compose.production.yml down
echo "✅ 服務已停止"
echo ""

# 步驟 4: 重新構建 Docker 鏡像（安裝新依賴）
echo "🔨 步驟 4: 重新構建 Docker 鏡像（安裝 pandas 和 openpyxl）..."
echo "   這可能需要幾分鐘..."
docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache web_admin || {
    echo "⚠️  構建失敗，嘗試使用緩存..."
    docker compose --env-file .env.production -f docker-compose.production.yml build web_admin
}

echo "✅ 鏡像構建完成"
echo ""

# 步驟 5: 啟動所有服務
echo "🚀 步驟 5: 啟動所有服務..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ 服務啟動命令執行成功"
else
    echo "❌ 服務啟動失敗！"
    exit 1
fi

# 步驟 6: 等待服務啟動
echo ""
echo "⏳ 步驟 6: 等待服務啟動（30秒）..."
sleep 30

# 步驟 7: 檢查服務狀態
echo ""
echo "📊 步驟 7: 檢查服務狀態..."
docker compose -f docker-compose.production.yml ps

# 步驟 8: 檢查 web_admin 日誌（確認 pandas 已安裝）
echo ""
echo "📋 步驟 8: 檢查 web_admin 日誌（最後20行）..."
docker compose -f docker-compose.production.yml logs web_admin --tail 20 | grep -i "pandas\|error\|failed\|ModuleNotFound" || echo "✅ 未發現 pandas 錯誤"

# 步驟 9: 測試健康檢查
echo ""
echo "🧪 步驟 9: 測試健康檢查..."
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
echo "如果服務正常運行，您應該看到："
echo "  - 所有容器狀態為 'Up' 或 'healthy'"
echo "  - 健康檢查返回 {'ok': true}"
echo ""

