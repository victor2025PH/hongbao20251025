#!/bin/bash
# 修復 requirements.txt 編碼問題

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 修復 requirements.txt 編碼問題"
echo "===================================="
echo ""

# 步驟 1: 備份現有的 requirements.txt
echo "📋 步驟 1: 備份現有的 requirements.txt..."
cp requirements.txt requirements.txt.bak.$(date +%Y%m%d_%H%M%S)
echo "✅ 備份完成"
echo ""

# 步驟 2: 從 GitHub 重新拉取 requirements.txt（覆蓋本地文件）
echo "📥 步驟 2: 從 GitHub 重新拉取 requirements.txt..."
git checkout HEAD -- requirements.txt || {
    echo "⚠️  無法從 Git 恢復，將手動修復..."
}

# 如果 Git 恢復失敗，手動修復
if [ $? -ne 0 ] || [ ! -f requirements.txt ]; then
    echo "⚠️  Git 恢復失敗，手動創建 requirements.txt..."
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
fi

echo "✅ requirements.txt 已修復"
echo ""

# 步驟 3: 驗證文件編碼和內容
echo "🔍 步驟 3: 驗證文件編碼和內容..."
file requirements.txt
echo ""
echo "文件內容（最後 10 行）："
tail -10 requirements.txt
echo ""

# 步驟 4: 檢查是否有亂碼
echo "🔍 步驟 4: 檢查是否有亂碼..."
if grep -qP '[^\x00-\x7F]' requirements.txt; then
    echo "⚠️  發現非 ASCII 字符，正在清理..."
    # 移除非 ASCII 字符（保留換行符）
    sed -i 's/[^\x00-\x7F]//g' requirements.txt
    echo "✅ 已清理非 ASCII 字符"
else
    echo "✅ 未發現亂碼"
fi
echo ""

# 步驟 5: 驗證 pandas 和 openpyxl 是否存在
echo "🔍 步驟 5: 驗證 pandas 和 openpyxl 是否存在..."
if grep -q "^pandas==" requirements.txt && grep -q "^openpyxl==" requirements.txt; then
    echo "✅ pandas 和 openpyxl 已正確添加"
    grep -E "^pandas==|^openpyxl==" requirements.txt
else
    echo "⚠️  pandas 或 openpyxl 缺失，正在添加..."
    if ! grep -q "^pandas==" requirements.txt; then
        echo "pandas==2.2.3" >> requirements.txt
    fi
    if ! grep -q "^openpyxl==" requirements.txt; then
        echo "openpyxl==3.1.5" >> requirements.txt
    fi
    echo "✅ 已添加 pandas 和 openpyxl"
fi
echo ""

# 步驟 6: 驗證文件格式（確保每行都是有效的包名）
echo "🔍 步驟 6: 驗證文件格式..."
echo "檢查是否有無效的行..."
invalid_lines=$(grep -v -E '^[a-zA-Z0-9_-]+==[0-9.]+$|^$' requirements.txt | wc -l)
if [ "$invalid_lines" -gt 0 ]; then
    echo "⚠️  發現 $invalid_lines 行無效內容："
    grep -v -E '^[a-zA-Z0-9_-]+==[0-9.]+$|^$' requirements.txt
    echo ""
    echo "正在清理無效行..."
    grep -E '^[a-zA-Z0-9_-]+==[0-9.]+$|^$' requirements.txt > requirements.txt.tmp
    mv requirements.txt.tmp requirements.txt
    echo "✅ 已清理無效行"
else
    echo "✅ 所有行格式正確"
fi
echo ""

# 步驟 7: 顯示最終文件內容
echo "📋 步驟 7: 顯示最終文件內容..."
echo "文件總行數："
wc -l requirements.txt
echo ""
echo "最後 10 行："
tail -10 requirements.txt
echo ""

echo "===================================="
echo "✅ requirements.txt 修復完成！"
echo "===================================="
echo ""
echo "下一步：重新構建 Docker 鏡像"
echo ""

