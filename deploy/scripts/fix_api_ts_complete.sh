#!/bin/bash
# 完整修复 src/lib/api.ts 文件
# 使用方法: bash deploy/scripts/fix_api_ts_complete.sh

set -e

PROJECT_DIR="/opt/redpacket"
FRONTEND_DIR="${PROJECT_DIR}/frontend-next"
API_FILE="${FRONTEND_DIR}/src/lib/api.ts"

echo "🔧 完整修复 src/lib/api.ts 文件..."
echo ""

# 检查文件是否存在
if [ ! -f "${API_FILE}" ]; then
    echo "❌ 文件不存在: ${API_FILE}"
    exit 1
fi

cd "${FRONTEND_DIR}"

# 备份
echo "1️⃣  备份原文件..."
cp "${API_FILE}" "${API_FILE}.bak.$(date +%Y%m%d_%H%M%S)"
echo "   ✅ 备份完成"
echo ""

# 检查当前内容
echo "2️⃣  检查当前内容..."
echo "   第 19-30 行:"
sed -n '19,30p' "${API_FILE}" | cat -A
echo ""

# 使用 Python 完整修复（最可靠）
echo "3️⃣  使用 Python 修复文件..."
python3 << 'PYTHON_EOF'
import re
import sys

file_path = sys.argv[1]

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 修复 DashboardTrends 定义（第 19-24 行）
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 修复 DashboardTrends
        if 'export' in line and 'DashboardTrends' in line:
            # 替换为正确的定义
            fixed_lines.append('export type DashboardTrends = Array<{\n')
            fixed_lines.append('  date: string\n')
            fixed_lines.append('  users: number\n')
            fixed_lines.append('  envelopes: number\n')
            fixed_lines.append('  amount: number\n')
            fixed_lines.append('}>\n')
            # 跳过原来的定义行（直到找到 }> 或类似）
            i += 1
            while i < len(lines) and not ('}>' in lines[i] or '}]' in lines[i]):
                i += 1
            i += 1
            # 确保下一行是空行
            if i < len(lines) and lines[i].strip():
                fixed_lines.append('\n')
        # 修复 DashboardData（确保格式正确）
        elif 'export interface DashboardData' in line:
            # 清理行，移除异常字符
            clean_line = re.sub(r'\{[^}]*build[^}]*', '{', line)
            clean_line = re.sub(r'\{.*?\{', '{', clean_line)
            if not clean_line.endswith('{\n') and '{' in clean_line:
                clean_line = re.sub(r'\{.*', '{\n', clean_line)
            fixed_lines.append(clean_line)
            i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
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
    
    # 方法：找到 DashboardTrends 和 DashboardData 的行号，然后精确替换
    TRENDS_LINE=$(grep -n "export.*DashboardTrends" "${API_FILE}" | head -1 | cut -d: -f1)
    DATA_LINE=$(grep -n "export interface DashboardData" "${API_FILE}" | head -1 | cut -d: -f1)
    
    if [ -n "${TRENDS_LINE}" ] && [ -n "${DATA_LINE}" ]; then
        # 创建临时文件
        TMP_FILE=$(mktemp)
        
        # 复制前 18 行
        head -n $((TRENDS_LINE - 1)) "${API_FILE}" > "${TMP_FILE}"
        
        # 添加修复后的 DashboardTrends
        cat >> "${TMP_FILE}" << 'EOF'
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>

EOF
        
        # 添加修复后的 DashboardData（从原文件复制，但清理异常字符）
        sed -n "${DATA_LINE},$"p "${API_FILE}" | sed 's/{.*{/{/' | sed 's/{build/{/' >> "${TMP_FILE}"
        
        # 替换原文件
        mv "${TMP_FILE}" "${API_FILE}"
        
        echo "   ✅ 使用 sed 修复完成"
    else
        echo "   ❌ 无法找到 DashboardTrends 或 DashboardData 定义"
        exit 1
    fi
fi
echo ""

# 验证修复
echo "4️⃣  验证修复..."
echo "   修复后的第 19-30 行:"
sed -n '19,30p' "${API_FILE}"
echo ""

# 检查关键内容
if grep -q "export type DashboardTrends = Array<{" "${API_FILE}" && \
   grep -q "export interface DashboardData {" "${API_FILE}"; then
    echo "   ✅ 修复验证成功"
else
    echo "   ❌ 修复验证失败"
    echo "   恢复备份..."
    cp "${API_FILE}.bak."* "${API_FILE}" 2>/dev/null || true
    exit 1
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

