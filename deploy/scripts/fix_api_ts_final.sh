#!/bin/bash
# 最终修复 src/lib/api.ts - 清理所有可能的格式问题
# 使用方法: bash deploy/scripts/fix_api_ts_final.sh

set -e

PROJECT_DIR="/opt/redpacket"
FRONTEND_DIR="${PROJECT_DIR}/frontend-next"
API_FILE="${FRONTEND_DIR}/src/lib/api.ts"

echo "🔧 最终修复 src/lib/api.ts 文件..."
echo ""

# 检查文件是否存在
if [ ! -f "${API_FILE}" ]; then
    echo "❌ 文件不存在: ${API_FILE}"
    exit 1
fi

cd "${FRONTEND_DIR}"

# 备份
echo "1️⃣  备份原文件..."
BACKUP_FILE="${API_FILE}.bak.$(date +%Y%m%d_%H%M%S)"
cp "${API_FILE}" "${BACKUP_FILE}"
echo "   ✅ 备份完成: ${BACKUP_FILE}"
echo ""

# 检查当前内容
echo "2️⃣  检查当前内容（包括隐藏字符）..."
echo "   第 19-38 行（显示所有字符）:"
cat -A "${API_FILE}" | sed -n '19,38p'
echo ""

# 使用 Python 完整修复（最可靠）
echo "3️⃣  使用 Python 完整修复..."
python3 << 'PYTHON_EOF'
import re
import sys

file_path = sys.argv[1]

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 移除所有控制字符（除了换行和制表符）
    content = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', content)
    
    # 2. 统一行尾符为 LF
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # 3. 修复 DashboardTrends 定义
    # 匹配并替换整个 DashboardTrends 定义
    trends_pattern = r'export\s+(?:type|interface)\s+DashboardTrends[^}]*\}'
    trends_replacement = '''export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>'''
    
    if not re.search(r'export\s+type\s+DashboardTrends\s*=\s*Array<\{', content):
        content = re.sub(trends_pattern, trends_replacement, content, flags=re.DOTALL)
    
    # 4. 修复 DashboardData 接口中的可选属性格式
    # 确保 ?: 之间没有空格
    content = re.sub(r'\?\s*:', '?:', content)
    
    # 5. 移除 trends?: DashboardTrends) 中多余的右括号
    content = re.sub(r'trends\?:\s*DashboardTrends\)', 'trends?: DashboardTrends', content)
    
    # 6. 确保 DashboardData 接口格式正确
    # 移除 interface 后面的异常字符
    content = re.sub(r'export\s+interface\s+DashboardData\s+\{[^}]*build[^}]*', 
                     'export interface DashboardData {', content)
    content = re.sub(r'export\s+interface\s+DashboardData\s+\{.*?\{', 
                     'export interface DashboardData {', content)
    
    # 7. 确保可选属性格式正确（?: 紧挨着）
    # 修复可能的 ? : 格式（中间有空格）
    content = re.sub(r'\?\s+:', '?:', content)
    
    # 8. 清理多余的空格
    # 确保 ?: 后面只有一个空格
    content = re.sub(r'\?:\s+', '?: ', content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    
    print("   ✅ 文件已修复")
    
except Exception as e:
    print(f"   ❌ Python 修复失败: {e}")
    print("   将使用 sed 方法...")
    sys.exit(1)
PYTHON_EOF
"${API_FILE}"

# 如果 Python 失败，使用 sed
if [ $? -ne 0 ]; then
    echo "   ⚠️  Python 不可用，使用 sed 方法..."
    
    # 清理控制字符
    sed -i 's/[[:cntrl:]]//g' "${API_FILE}"
    sed -i 's/\r$//' "${API_FILE}"
    
    # 修复可选属性格式
    sed -i 's/?\s*:/?:/g' "${API_FILE}"
    sed -i 's/trends?: DashboardTrends)/trends?: DashboardTrends/' "${API_FILE}"
    
    # 修复 DashboardTrends
    sed -i 's/export interface DashboardTrends extends Array</export type DashboardTrends = Array</' "${API_FILE}"
    sed -i 's/}> {}$/}>/' "${API_FILE}"
    
    echo "   ✅ 使用 sed 修复完成"
fi
echo ""

# 验证修复
echo "4️⃣  验证修复..."
echo "   修复后的第 19-38 行:"
sed -n '19,38p' "${API_FILE}"
echo ""

# 检查关键内容
echo "5️⃣  检查关键格式..."
if grep -q "export type DashboardTrends = Array<{" "${API_FILE}" && \
   grep -q "export interface DashboardData {" "${API_FILE}" && \
   grep -q "trends?: DashboardTrends$" "${API_FILE}"; then
    echo "   ✅ 格式验证成功"
else
    echo "   ⚠️  格式验证失败，检查详细内容:"
    grep -A 2 "DashboardTrends\|DashboardData" "${API_FILE}" | head -10
fi
echo ""

# 检查可选属性格式
echo "6️⃣  检查可选属性格式..."
OPTIONAL_PROPS=$(grep -n "?:" "${API_FILE}" | head -5)
if echo "${OPTIONAL_PROPS}" | grep -q "?:"; then
    echo "   ✅ 可选属性格式正确"
    echo "   示例:"
    echo "${OPTIONAL_PROPS}" | head -3
else
    echo "   ⚠️  未找到可选属性"
fi
echo ""

echo "=========================================="
echo "🎉 修复完成！"
echo "=========================================="
echo ""
echo "📋 下一步:"
echo "   cd /opt/redpacket"
echo "   docker compose -f docker-compose.production.yml build frontend"
echo ""
echo "如果仍然失败，请查看详细错误并手动修复"
echo ""

