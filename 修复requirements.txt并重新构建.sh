#!/bin/bash
# 修復 requirements.txt 編碼問題並重新構建

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 修復 requirements.txt 並重新構建"
echo "===================================="
echo ""

# 步驟 1: 備份現有文件
echo "📋 步驟 1: 備份現有的 requirements.txt..."
cp requirements.txt requirements.txt.bak.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
echo "✅ 備份完成"
echo ""

# 步驟 2: 從 Git 恢復 requirements.txt（清除所有本地修改）
echo "📥 步驟 2: 從 Git 恢復 requirements.txt（清除亂碼）..."
git checkout HEAD -- requirements.txt 2>/dev/null || {
    echo "⚠️  Git 恢復失敗，手動修復..."
    # 如果 Git 恢復失敗，手動創建一個乾淨的文件
    cat > requirements.txt << 'EOF'
aiofiles==24.1.0
aiogram==3.22.0
aiohappyeyeballs==2.6.1
aiohttp==3.12.15
aiosignal==1.4.0
annotated-types==0.7.0
attrs==25.4.0
certifi==2025.10.5
fastapi==0.115.0
httpx==0.27.2
frozenlist==1.8.0
greenlet==3.2.4
idna==3.11
magic-filter==1.0.12
multidict==6.7.0
propcache==0.4.1
psycopg2-binary==2.9.11
pydantic==2.11.10
pydantic_core==2.33.2
SQLAlchemy==2.0.44
typing-inspection==0.4.2
typing_extensions==4.15.0
uvicorn==0.32.0
itsdangerous==2.2.0
python-multipart==0.0.19
Jinja2==3.1.5
yarl==1.22.0
openai==1.58.1
PyJWT==2.9.0
pandas==2.2.3
openpyxl==3.1.5
EOF
}

echo "✅ requirements.txt 已恢復"
echo ""

# 步驟 3: 檢查 pandas 和 openpyxl（如果不存在則添加）
echo "🔍 步驟 3: 檢查 pandas 和 openpyxl..."
if ! grep -q "^pandas==" requirements.txt; then
    echo "⚠️  pandas 缺失，正在添加..."
    # 使用 printf 避免編碼問題
    printf "pandas==2.2.3\n" >> requirements.txt
fi

if ! grep -q "^openpyxl==" requirements.txt; then
    echo "⚠️  openpyxl 缺失，正在添加..."
    printf "openpyxl==3.1.5\n" >> requirements.txt
fi

echo "✅ 依賴檢查完成"
echo ""

# 步驟 4: 清理所有非 ASCII 字符（除了換行符）
echo "🔍 步驟 4: 清理亂碼字符..."
# 移除非 ASCII 字符，但保留換行符
sed -i 's/[^\x00-\x7F\x0A]//g' requirements.txt
# 移除空行（如果有的話）
sed -i '/^$/d' requirements.txt
# 確保文件末尾有換行符
echo "" >> requirements.txt
sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' requirements.txt
echo "" >> requirements.txt

echo "✅ 清理完成"
echo ""

# 步驟 5: 驗證文件格式
echo "🔍 步驟 5: 驗證文件格式..."
echo "文件總行數："
wc -l requirements.txt
echo ""
echo "最後 5 行："
tail -5 requirements.txt | cat -A
echo ""
echo "檢查是否有無效行..."
invalid_count=$(grep -v -E '^[a-zA-Z0-9_.-]+==[0-9.]+$' requirements.txt | grep -v '^$' | wc -l)
if [ "$invalid_count" -gt 0 ]; then
    echo "⚠️  發現 $invalid_count 行無效內容："
    grep -v -E '^[a-zA-Z0-9_.-]+==[0-9.]+$' requirements.txt | grep -v '^$'
    echo ""
    echo "正在清理無效行..."
    grep -E '^[a-zA-Z0-9_.-]+==[0-9.]+$' requirements.txt > requirements.txt.tmp
    mv requirements.txt.tmp requirements.txt
    echo "✅ 已清理無效行"
else
    echo "✅ 所有行格式正確"
fi
echo ""

# 步驟 6: 最終驗證 pandas 和 openpyxl
echo "🔍 步驟 6: 最終驗證..."
echo "pandas 和 openpyxl 行："
grep -E "^pandas==|^openpyxl==" requirements.txt || echo "⚠️  未找到 pandas 或 openpyxl"
echo ""

# 步驟 7: 停止服務
echo "🛑 步驟 7: 停止所有服務..."
docker compose -f docker-compose.production.yml down 2>/dev/null || true
echo "✅ 服務已停止"
echo ""

# 步驟 8: 重新構建
echo "🔨 步驟 8: 重新構建 backend 鏡像..."
echo "   這可能需要 3-5 分鐘，請耐心等待..."
docker compose --env-file .env.production -f docker-compose.production.yml build --no-cache bot web_admin miniapp_api

if [ $? -eq 0 ]; then
    echo "✅ 鏡像構建成功！"
else
    echo "❌ 鏡像構建失敗！"
    echo ""
    echo "請檢查 requirements.txt 內容："
    cat requirements.txt
    exit 1
fi
echo ""

# 步驟 9: 啟動服務
echo "🚀 步驟 9: 啟動所有服務..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d
echo "✅ 服務啟動命令執行成功"
echo ""

# 步驟 10: 等待服務啟動
echo "⏳ 步驟 10: 等待服務啟動（30秒）..."
sleep 30
echo ""

# 步驟 11: 檢查服務狀態
echo "📊 步驟 11: 檢查服務狀態..."
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

# 步驟 12: 檢查 web_admin 日誌
echo "📋 步驟 12: 檢查 web_admin 日誌（最後 20 行）..."
docker compose -f docker-compose.production.yml logs web_admin --tail 20
echo ""

# 步驟 13: 測試健康檢查
echo "🧪 步驟 13: 測試健康檢查..."
echo ""
echo "Web Admin (8000):"
curl -s http://127.0.0.1:8000/healthz && echo "" || echo "⚠️  Web Admin 健康檢查失敗"
echo ""

echo "===================================="
echo "✅ 修復完成！"
echo "===================================="

