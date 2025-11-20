#!/bin/bash
# 修復 Git 克隆問題 - 最終方案
# 完全清空目錄（保留 .env.production）然後重新克隆

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 修復 Git 克隆問題"
echo "===================================="
echo ""

# 步驟 1: 備份 .env.production
echo "📝 步驟 1: 備份 .env.production..."
if [ -f .env.production ]; then
    cp .env.production /tmp/.env.production.bak
    echo "✅ 已備份 .env.production"
else
    echo "⚠️  .env.production 不存在，跳過備份"
fi
echo ""

# 步驟 2: 完全清空目錄（保留 .env.production）
echo "🗑️  步驟 2: 清空目錄..."
# 移動 .env.production 到臨時位置
if [ -f .env.production ]; then
    mv .env.production /tmp/.env.production.tmp
fi

# 刪除所有文件和目錄（包括隱藏文件）
rm -rf .[^.]* *
rm -rf *

# 恢復 .env.production
if [ -f /tmp/.env.production.tmp ]; then
    mv /tmp/.env.production.tmp .env.production
    echo "✅ 已恢復 .env.production"
fi

echo "✅ 目錄已清空"
echo ""

# 步驟 3: 重新克隆完整代碼
echo "📥 步驟 3: 重新克隆完整代碼..."
git clone https://github.com/victor2025PH/hongbao20251025.git .

if [ $? -eq 0 ]; then
    echo "✅ 代碼克隆成功"
else
    echo "❌ 代碼克隆失敗！"
    exit 1
fi
echo ""

# 步驟 4: 恢復並修復 .env.production
echo "🔧 步驟 4: 恢復並修復 .env.production..."
if [ -f /tmp/.env.production.bak ]; then
    cp /tmp/.env.production.bak .env.production
    # 修復缺少等號的問題
    sed -i 's/NOWPAYMENTS_IPN_URLhttps/NOWPAYMENTS_IPN_URL=https/g' .env.production
    echo "✅ 已恢復並修復 .env.production"
else
    echo "⚠️  未找到備份文件，使用現有 .env.production"
    sed -i 's/NOWPAYMENTS_IPN_URLhttps/NOWPAYMENTS_IPN_URL=https/g' .env.production
fi
echo ""

# 步驟 5: 檢查關鍵文件
echo "📋 步驟 5: 檢查關鍵文件..."
echo ""

[ -f docker-compose.production.yml ] && echo "✅ docker-compose.production.yml 存在" || echo "❌ docker-compose.production.yml 不存在"
[ -d deploy ] && echo "✅ deploy/ 目錄存在" || echo "❌ deploy/ 目錄不存在"
[ -f .env.production ] && echo "✅ .env.production 存在" || echo "❌ .env.production 不存在"
[ -d frontend-next ] && echo "✅ frontend-next/ 目錄存在" || echo "❌ frontend-next/ 目錄不存在"
[ -d web_admin ] && echo "✅ web_admin/ 目錄存在" || echo "❌ web_admin/ 目錄不存在"

echo ""
echo "===================================="
echo "✅ 修復完成！"
echo "===================================="
echo ""
echo "下一步執行部署："
echo "  docker compose -f docker-compose.production.yml build"
echo "  docker compose -f docker-compose.production.yml up -d"
echo ""

