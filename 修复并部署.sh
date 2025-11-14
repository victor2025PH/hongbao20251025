#!/bin/bash
# 修復並部署腳本
# 在服務器上執行此腳本

set -e

echo "===================================="
echo "🔧 修復並部署紅包系統"
echo "===================================="
echo ""

cd /opt/redpacket

# 步驟 1: 檢查並修復 .env.production
echo "📝 步驟 1: 檢查並修復 .env.production 配置..."
if [ -f .env.production ]; then
    # 修復 NOWPAYMENTS_IPN_URL 缺少等號的問題
    sed -i 's/NOWPAYMENTS_IPN_URLhttps/NOWPAYMENTS_IPN_URL=https/g' .env.production
    echo "✅ 已修復 .env.production 配置"
else
    echo "❌ 錯誤: .env.production 文件不存在！"
    exit 1
fi

# 步驟 2: 檢查項目文件是否完整
echo ""
echo "📂 步驟 2: 檢查項目文件..."
if [ ! -f "docker-compose.production.yml" ]; then
    echo "⚠️  項目文件不完整，重新拉取代碼..."
    git fetch origin
    git reset --hard origin/master
    echo "✅ 代碼已更新"
else
    echo "✅ 項目文件完整"
fi

# 步驟 3: 檢查 deploy 目錄
echo ""
echo "📂 步驟 3: 檢查 deploy 目錄..."
if [ ! -d "deploy" ]; then
    echo "⚠️  deploy 目錄不存在，重新拉取代碼..."
    git pull origin master
    echo "✅ 代碼已更新"
else
    echo "✅ deploy 目錄存在"
fi

# 步驟 4: 構建 Docker 鏡像
echo ""
echo "🔨 步驟 4: 構建 Docker 鏡像..."
docker compose -f docker-compose.production.yml build --no-cache frontend || {
    echo "⚠️  前端構建失敗，嘗試使用緩存..."
    docker compose -f docker-compose.production.yml build frontend
}

# 步驟 5: 啟動所有服務
echo ""
echo "🚀 步驟 5: 啟動所有服務..."
docker compose -f docker-compose.production.yml up -d

echo ""
echo "⏳ 等待服務啟動（30秒）..."
sleep 30

# 步驟 6: 檢查服務狀態
echo ""
echo "📊 步驟 6: 檢查服務狀態..."
docker compose -f docker-compose.production.yml ps

echo ""
echo "===================================="
echo "✅ 部署完成！"
echo "===================================="
echo ""
echo "下一步驗證："
echo "  1. 查看服務狀態: docker compose -f docker-compose.production.yml ps"
echo "  2. 查看日誌: docker compose -f docker-compose.production.yml logs -f"
echo "  3. 測試健康檢查: curl http://127.0.0.1:8000/healthz"
echo ""

