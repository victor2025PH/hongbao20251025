#!/bin/bash
# 解決鏡像已存在錯誤並重新部署

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 解決鏡像已存在錯誤並重新部署"
echo "===================================="
echo ""

# 步驟 1: 停止所有服務
echo "🛑 步驟 1: 停止所有服務..."
docker compose -f docker-compose.production.yml down 2>/dev/null || true
echo "✅ 服務已停止"
echo ""

# 步驟 2: 刪除所有使用 redpacket/backend:latest 的容器
echo "🗑️  步驟 2: 刪除所有使用 backend 鏡像的容器..."
docker ps -a --filter "ancestor=redpacket/backend:latest" -q | xargs -r docker rm -f 2>/dev/null || true
echo "✅ 容器已清理"
echo ""

# 步驟 3: 強制刪除舊的 backend 鏡像
echo "🗑️  步驟 3: 強制刪除舊的 backend 鏡像..."
docker rmi -f redpacket/backend:latest 2>/dev/null || {
    echo "⚠️  鏡像不存在或正在使用，嘗試更徹底的清理..."
    # 如果直接刪除失敗，先停止所有相關容器
    docker ps -a | grep redpacket | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true
    sleep 2
    docker rmi -f redpacket/backend:latest 2>/dev/null || echo "⚠️  無法刪除鏡像，將使用 --pull always 重建"
}
echo "✅ 鏡像清理完成"
echo ""

# 步驟 4: 清理 Docker 構建緩存（可選，但可以確保乾淨構建）
echo "🧹 步驟 4: 清理 Docker 構建緩存..."
docker builder prune -f 2>/dev/null || true
echo "✅ 緩存清理完成"
echo ""

# 步驟 5: 驗證 requirements.txt 存在且格式正確
echo "🔍 步驟 5: 驗證 requirements.txt..."
if [ ! -f requirements.txt ]; then
    echo "❌ requirements.txt 不存在！"
    exit 1
fi

# 檢查文件是否為純文本
if ! file requirements.txt | grep -q "text"; then
    echo "⚠️  警告：requirements.txt 可能不是純文本格式"
    file requirements.txt
fi

# 檢查 pandas 和 openpyxl
if ! grep -q "^pandas==" requirements.txt || ! grep -q "^openpyxl==" requirements.txt; then
    echo "⚠️  pandas 或 openpyxl 缺失，正在添加..."
    if ! grep -q "^pandas==" requirements.txt; then
        echo "pandas==2.2.3" >> requirements.txt
    fi
    if ! grep -q "^openpyxl==" requirements.txt; then
        echo "openpyxl==3.1.5" >> requirements.txt
    fi
fi

echo "✅ requirements.txt 驗證完成"
echo ""

# 步驟 6: 重新構建 backend 鏡像（使用 --pull always 確保獲取最新基礎鏡像）
echo "🔨 步驟 6: 重新構建 backend 鏡像..."
echo "   這可能需要 3-5 分鐘，請耐心等待..."

# 先嘗試刪除所有相關的 dangling 鏡像
docker images "redpacket/backend" -q | xargs -r docker rmi -f 2>/dev/null || true

# 構建鏡像（不使用緩存，並強制重新拉取基礎鏡像）
docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache --pull bot web_admin miniapp_api

if [ $? -eq 0 ]; then
    echo "✅ 鏡像構建成功！"
else
    echo "❌ 鏡像構建失敗！"
    echo ""
    echo "嘗試使用簡化方式構建..."
    # 如果構建失敗，嘗試只構建一個服務來測試
    docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache web_admin
    if [ $? -eq 0 ]; then
        echo "✅ web_admin 構建成功，繼續構建其他服務..."
        docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache bot miniapp_api
    else
        echo "❌ 構建仍然失敗，請檢查錯誤信息"
        exit 1
    fi
fi
echo ""

# 步驟 7: 驗證鏡像是否存在
echo "🔍 步驟 7: 驗證鏡像是否存在..."
docker images | grep "redpacket/backend" || {
    echo "❌ backend 鏡像不存在！"
    exit 1
}
echo "✅ backend 鏡像已存在"
docker images | grep "redpacket/backend"
echo ""

# 步驟 8: 啟動所有服務
echo "🚀 步驟 8: 啟動所有服務..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ 服務啟動命令執行成功"
else
    echo "❌ 服務啟動失敗！"
    exit 1
fi
echo ""

# 步驟 9: 等待服務啟動
echo "⏳ 步驟 9: 等待服務啟動（30秒）..."
sleep 30
echo ""

# 步驟 10: 檢查服務狀態
echo "📊 步驟 10: 檢查服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 11: 檢查 web_admin 日誌
echo "📋 步驟 11: 檢查 web_admin 日誌（最後 20 行）..."
docker compose -f docker-compose.production.yml logs web_admin --tail 20
echo ""

# 步驟 12: 測試健康檢查
echo "🧪 步驟 12: 測試健康檢查..."
echo ""
echo "Web Admin (8000):"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"

echo "MiniApp API (8080):"
curl -s http://127.0.0.1:8080/healthz && echo "" || echo "⚠️  MiniApp API 健康檢查失敗"
echo ""

echo "===================================="
echo "✅ 部署完成！"
echo "===================================="

