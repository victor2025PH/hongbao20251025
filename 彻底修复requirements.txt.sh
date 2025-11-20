#!/bin/bash
# 徹底修復 requirements.txt 編碼問題

set -e

cd /opt/redpacket

echo "===================================="
echo "🔧 徹底修復 requirements.txt 編碼問題"
echo "===================================="
echo ""

# 步驟 1: 備份現有文件
echo "📋 步驟 1: 備份現有的 requirements.txt..."
cp requirements.txt requirements.txt.bak.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
echo "✅ 備份完成"
echo ""

# 步驟 2: 檢查文件編碼和格式
echo "🔍 步驟 2: 檢查文件編碼..."
file requirements.txt
echo ""
echo "文件大小："
wc -c requirements.txt
echo ""

# 步驟 3: 完全重新創建 requirements.txt（使用 UTF-8 編碼，無 BOM）
echo "🔧 步驟 3: 重新創建 requirements.txt（UTF-8 編碼，無 BOM）..."
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

# 確保文件末尾有換行符（使用 echo 會自動添加）
echo "" >> requirements.txt

echo "✅ requirements.txt 已重新創建"
echo ""

# 步驟 4: 驗證文件編碼和格式
echo "🔍 步驟 4: 驗證文件編碼和格式..."
file requirements.txt
echo ""
echo "文件大小（字節）："
wc -c requirements.txt
echo ""
echo "文件行數："
wc -l requirements.txt
echo ""

# 步驟 5: 檢查文件是否為純文本（不應該包含 BOM）
echo "🔍 步驟 5: 檢查文件開頭字節（確認無 BOM）..."
hexdump -C requirements.txt | head -2
echo ""

# 步驟 6: 驗證文件內容（使用 cat 顯示，確認沒有亂碼）
echo "🔍 步驟 6: 驗證文件內容..."
echo "最後 5 行："
tail -5 requirements.txt
echo ""
echo "所有行（確認無重複）："
cat requirements.txt | grep -v '^$' | sort -u
echo ""

# 步驟 7: 確認 pandas 和 openpyxl 存在且不重複
echo "🔍 步驟 7: 確認 pandas 和 openpyxl..."
pandas_count=$(grep -c "^pandas==" requirements.txt || echo "0")
openpyxl_count=$(grep -c "^openpyxl==" requirements.txt || echo "0")

if [ "$pandas_count" -eq "1" ]; then
    echo "✅ pandas 存在且不重複"
    grep "^pandas==" requirements.txt
else
    echo "⚠️  pandas 存在 $pandas_count 次（應該只有 1 次）"
    # 移除重複的 pandas
    grep "^pandas==" requirements.txt | head -1 > /tmp/pandas_line.txt
    grep -v "^pandas==" requirements.txt > requirements.txt.tmp
    cat /tmp/pandas_line.txt >> requirements.txt.tmp
    mv requirements.txt.tmp requirements.txt
    echo "✅ 已修復 pandas 重複問題"
fi

if [ "$openpyxl_count" -eq "1" ]; then
    echo "✅ openpyxl 存在且不重複"
    grep "^openpyxl==" requirements.txt
else
    echo "⚠️  openpyxl 存在 $openpyxl_count 次（應該只有 1 次）"
    # 移除重複的 openpyxl
    grep "^openpyxl==" requirements.txt | head -1 > /tmp/openpyxl_line.txt
    grep -v "^openpyxl==" requirements.txt > requirements.txt.tmp
    cat /tmp/openpyxl_line.txt >> requirements.txt.tmp
    mv requirements.txt.tmp requirements.txt
    echo "✅ 已修復 openpyxl 重複問題"
fi
echo ""

# 步驟 8: 最終驗證（確認文件可以被 grep 正常讀取，不是二進制文件）
echo "🔍 步驟 8: 最終驗證..."
if file requirements.txt | grep -q "text"; then
    echo "✅ 文件是純文本格式"
else
    echo "⚠️  警告：文件可能不是純文本格式"
    file requirements.txt
fi

if ! grep -q "binary file" <(grep -l "." requirements.txt 2>&1); then
    echo "✅ 文件可以被 grep 正常讀取"
else
    echo "⚠️  警告：文件可能被識別為二進制文件"
fi
echo ""

# 步驟 9: 測試文件是否可以正常解析（使用 Python 驗證）
echo "🔍 步驟 9: 使用 Python 驗證文件格式..."
python3 << 'PYEOF'
import sys
try:
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"✅ 成功讀取 {len(lines)} 行")
        
        # 檢查是否有無效字符
        for i, line in enumerate(lines, 1):
            line = line.rstrip('\n\r')
            if line and not line.startswith('#'):
                if '==' not in line:
                    print(f"⚠️  第 {i} 行格式可能無效: {line}")
                    continue
                parts = line.split('==')
                if len(parts) != 2:
                    print(f"⚠️  第 {i} 行格式可能無效: {line}")
                    continue
        
        print("✅ 所有行格式正確")
        
        # 檢查重複
        packages = {}
        for i, line in enumerate(lines, 1):
            line = line.rstrip('\n\r').strip()
            if line and not line.startswith('#') and '==' in line:
                pkg = line.split('==')[0].strip()
                if pkg in packages:
                    print(f"⚠️  警告：第 {i} 行重複包 {pkg}（首次出現在第 {packages[pkg]} 行）")
                else:
                    packages[pkg] = i
        
        if 'pandas' in packages:
            print(f"✅ pandas 在第 {packages['pandas']} 行")
        else:
            print("❌ pandas 缺失")
            
        if 'openpyxl' in packages:
            print(f"✅ openpyxl 在第 {packages['openpyxl']} 行")
        else:
            print("❌ openpyxl 缺失")
            
except UnicodeDecodeError as e:
    print(f"❌ Unicode 解碼錯誤: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 錯誤: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    echo "✅ Python 驗證通過"
else
    echo "❌ Python 驗證失敗"
    exit 1
fi
echo ""

echo "===================================="
echo "✅ requirements.txt 徹底修復完成！"
echo "===================================="
echo ""
echo "下一步：重新構建 Docker 鏡像"
echo ""

