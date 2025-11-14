#!/bin/bash
# 安全修复 DashboardTrends 类型定义
# 使用方法: bash deploy/scripts/fix_dashboard_trends_safe.sh

set -e

PROJECT_DIR="/opt/redpacket"
FRONTEND_DIR="${PROJECT_DIR}/frontend-next"
API_FILE="${FRONTEND_DIR}/src/lib/api.ts"

echo "🔧 安全修复 DashboardTrends 类型定义..."
echo ""

# 检查文件是否存在
if [ ! -f "${API_FILE}" ]; then
    echo "❌ 文件不存在: ${API_FILE}"
    exit 1
fi

cd "${FRONTEND_DIR}"

# 备份原文件
echo "1️⃣  备份原文件..."
cp "${API_FILE}" "${API_FILE}.bak"
echo "   ✅ 备份完成: ${API_FILE}.bak"
echo ""

# 检查当前内容
echo "2️⃣  检查当前内容..."
if grep -q "export.*DashboardTrends" "${API_FILE}"; then
    echo "   当前 DashboardTrends 定义:"
    grep -A 6 "export.*DashboardTrends" "${API_FILE}" | head -7
else
    echo "   ⚠️  未找到 DashboardTrends 定义"
fi
echo ""

# 修复方法：使用 Python 脚本（更可靠）
echo "3️⃣  修复类型定义..."
python3 << 'PYTHON_EOF'
import re
import sys

file_path = sys.argv[1]

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换 DashboardTrends 定义
    # 匹配多种可能的格式
    patterns = [
        (r'export\s+interface\s+DashboardTrends\s+extends\s+Array<\{[^}]*\}\>\s*\{\}', 
         'export type DashboardTrends = Array<{\n  date: string\n  users: number\n  envelopes: number\n  amount: number\n}>'),
        (r'export\s+interface\s+DashboardTrends\s+extends\s+Array<', 
         'export type DashboardTrends = Array<'),
        (r'export\s+type\s+DashboardTrends\s*=\s*Array<d', 
         'export type DashboardTrends = Array<{'),
    ]
    
    original_content = content
    
    # 尝试修复
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # 确保格式正确
    if 'export type DashboardTrends = Array<' in content:
        # 检查是否缺少 {
        if 'export type DashboardTrends = Array<{' not in content:
            content = content.replace(
                'export type DashboardTrends = Array<',
                'export type DashboardTrends = Array<{'
            )
        # 确保有正确的结束
        if 'export type DashboardTrends = Array<{' in content:
            # 查找并修复可能的格式问题
            lines = content.split('\n')
            new_lines = []
            in_trends = False
            for i, line in enumerate(lines):
                if 'export type DashboardTrends = Array<' in line:
                    in_trends = True
                    if '{' not in line:
                        new_lines.append('export type DashboardTrends = Array<{')
                    else:
                        new_lines.append(line)
                elif in_trends:
                    if 'date: string' in line or 'users: number' in line or 'envelopes: number' in line or 'amount: number' in line:
                        new_lines.append(line)
                    elif '}>' in line or '}>' in line:
                        new_lines.append('}>')
                        in_trends = False
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   ✅ 文件已修复")
    else:
        print("   ℹ️  文件无需修复（可能已经是正确格式）")
        
except Exception as e:
    print(f"   ❌ 修复失败: {e}")
    sys.exit(1)
PYTHON_EOF
"${API_FILE}"

# 如果 Python 不可用，使用 sed 方法
if [ $? -ne 0 ]; then
    echo "   ⚠️  Python 修复失败，使用 sed 方法..."
    
    # 更安全的 sed 方法：先找到行号，然后替换
    LINE_NUM=$(grep -n "export.*DashboardTrends" "${API_FILE}" | head -1 | cut -d: -f1)
    
    if [ -n "${LINE_NUM}" ]; then
        # 删除旧的定义（5行）
        sed -i "${LINE_NUM},$((LINE_NUM+4))d" "${API_FILE}"
        
        # 插入新的定义
        sed -i "${LINE_NUM}i\\
export type DashboardTrends = Array<{\\
  date: string\\
  users: number\\
  envelopes: number\\
  amount: number\\
}>" "${API_FILE}"
        
        echo "   ✅ 使用 sed 修复完成"
    else
        echo "   ❌ 无法找到 DashboardTrends 定义"
        exit 1
    fi
fi
echo ""

# 验证修复
echo "4️⃣  验证修复..."
if grep -q "export type DashboardTrends = Array<{" "${API_FILE}"; then
    echo "   ✅ 修复验证成功"
    echo "   修复后的定义:"
    grep -A 6 "export type DashboardTrends" "${API_FILE}" | head -7
else
    echo "   ❌ 修复验证失败"
    echo "   恢复备份文件..."
    cp "${API_FILE}.bak" "${API_FILE}"
    echo "   ⚠️  已恢复备份，请手动修复"
    exit 1
fi
echo ""

# 检查语法（如果 TypeScript 可用）
if command -v npx &> /dev/null; then
    echo "5️⃣  检查 TypeScript 语法..."
    cd "${FRONTEND_DIR}"
    if npx tsc --noEmit src/lib/api.ts 2>&1 | grep -q "error"; then
        echo "   ⚠️  TypeScript 语法检查发现错误"
        npx tsc --noEmit src/lib/api.ts 2>&1 | head -5
    else
        echo "   ✅ TypeScript 语法检查通过"
    fi
else
    echo "5️⃣  跳过 TypeScript 语法检查（npx 不可用）"
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

