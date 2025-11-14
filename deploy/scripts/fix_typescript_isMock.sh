#!/bin/bash
# 修复 TypeScript isMock 属性缺失问题
# 使用方法: bash deploy/scripts/fix_typescript_isMock.sh

set -e

PROJECT_DIR="/opt/redpacket"
FRONTEND_DIR="${PROJECT_DIR}/frontend-next"

echo "🔧 修复 TypeScript isMock 属性缺失问题..."
echo ""

# 检查目录是否存在
if [ ! -d "${FRONTEND_DIR}" ]; then
    echo "❌ frontend-next 目录不存在: ${FRONTEND_DIR}"
    exit 1
fi

cd "${FRONTEND_DIR}"

# 修复 src/lib/api.ts
echo "1️⃣  修复 src/lib/api.ts..."
API_FILE="src/lib/api.ts"
if [ -f "${API_FILE}" ]; then
    # 检查是否已经修复
    if grep -q "isMock?: boolean" "${API_FILE}"; then
        echo "   ✅ 已包含 isMock 属性，跳过"
    else
        # 在 DashboardData 接口的最后一个 } 前添加 isMock 属性
        # 查找 "  }[]" 或 "  }" 在 DashboardData 接口内
        sed -i '/export interface DashboardData {/,/^}/ {
            /^  }\]$/a\
  isMock?: boolean  // 标识是否使用 mock 数据
        }' "${API_FILE}" 2>/dev/null || {
            # 如果 sed 失败，使用更简单的方法
            echo "   使用备用方法修复..."
            # 在 "  }[]" 后添加
            perl -i -pe 's/(  \}\])/  isMock?: boolean  \/\/ 标识是否使用 mock 数据\n$1/ if /export interface DashboardData/../^}/' "${API_FILE}" 2>/dev/null || {
                echo "   ⚠️  自动修复失败，请手动修复"
                echo "   在 DashboardData 接口中添加: isMock?: boolean"
            }
        }
        echo "   ✅ 已修复"
    fi
else
    echo "   ❌ 文件不存在: ${API_FILE}"
fi
echo ""

# 修复 src/mock/dashboard.ts
echo "2️⃣  修复 src/mock/dashboard.ts..."
MOCK_FILE="src/mock/dashboard.ts"
if [ -f "${MOCK_FILE}" ]; then
    # 检查是否已经修复
    if grep -q "isMock?: boolean" "${MOCK_FILE}"; then
        echo "   ✅ 已包含 isMock 属性，跳过"
    else
        # 在 DashboardData 接口的最后一个 } 前添加 isMock 属性
        sed -i '/export interface DashboardData {/,/^}/ {
            /^  }\]$/a\
  isMock?: boolean  // 标识是否使用 mock 数据
        }' "${MOCK_FILE}" 2>/dev/null || {
            # 如果 sed 失败，使用更简单的方法
            echo "   使用备用方法修复..."
            perl -i -pe 's/(  \}\])/  isMock?: boolean  \/\/ 标识是否使用 mock 数据\n$1/ if /export interface DashboardData/../^}/' "${MOCK_FILE}" 2>/dev/null || {
                echo "   ⚠️  自动修复失败，请手动修复"
                echo "   在 DashboardData 接口中添加: isMock?: boolean"
            }
        }
        echo "   ✅ 已修复"
    fi
else
    echo "   ❌ 文件不存在: ${MOCK_FILE}"
fi
echo ""

# 验证修复
echo "3️⃣  验证修复..."
if grep -q "isMock?: boolean" "${API_FILE}" && grep -q "isMock?: boolean" "${MOCK_FILE}"; then
    echo "   ✅ 修复验证成功"
    echo "   - src/lib/api.ts 包含 isMock 属性"
    echo "   - src/mock/dashboard.ts 包含 isMock 属性"
else
    echo "   ⚠️  修复验证失败，请手动检查"
    echo "   检查命令:"
    echo "   grep 'isMock' ${API_FILE}"
    echo "   grep 'isMock' ${MOCK_FILE}"
    exit 1
fi
echo ""

# 重新构建
echo "4️⃣  重新构建前端..."
cd "${PROJECT_DIR}"
if docker compose -f docker-compose.production.yml build frontend; then
    echo "   ✅ 前端构建成功"
    echo ""
    echo "5️⃣  启动服务..."
    docker compose -f docker-compose.production.yml up -d
    echo "   ✅ 服务已启动"
else
    echo "   ❌ 前端构建失败，请查看上面的错误信息"
    exit 1
fi
echo ""

echo "=========================================="
echo "🎉 修复完成！"
echo "=========================================="
echo ""
echo "📋 验证服务:"
echo "   docker compose -f docker-compose.production.yml ps"
echo "   curl http://localhost:8000/healthz"
echo ""

