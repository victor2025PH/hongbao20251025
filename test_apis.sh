#!/bin/bash
# API 接口测试脚本

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔌 API 接口测试"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ Web Admin API 测试"
echo "===================================="

BASE_URL_WEB="http://127.0.0.1:8000"

echo ""
echo "1.1 健康检查"
echo "---"
HEALTH_WEB=$(curl -s "$BASE_URL_WEB/healthz" 2>/dev/null || echo "")
if [ -n "$HEALTH_WEB" ]; then
    echo "✅ Web Admin API 健康检查通过"
    echo "响应: $HEALTH_WEB"
else
    echo "❌ Web Admin API 健康检查失败"
fi
echo ""

echo "1.2 API 文档"
echo "---"
echo "Swagger UI: $BASE_URL_WEB/docs"
if curl -s -o /dev/null -w '%{http_code}' "$BASE_URL_WEB/docs" | grep -q "200"; then
    echo "✅ API 文档可访问"
else
    echo "⚠️  API 文档不可访问"
fi
echo ""

echo "1.3 测试统计端点"
echo "---"

# 测试用户统计
echo "用户统计 API:"
curl -s "$BASE_URL_WEB/api/stats/users?start_date=2025-01-01&end_date=2025-11-15" 2>/dev/null | head -10 || echo "  端点不存在或需要认证"
echo ""

# 测试红包统计
echo "红包统计 API:"
curl -s "$BASE_URL_WEB/api/stats/hongbao?start_date=2025-01-01&end_date=2025-11-15" 2>/dev/null | head -10 || echo "  端点不存在或需要认证"
echo ""

echo "===================================="
echo "2️⃣ MiniApp API 测试"
echo "===================================="

BASE_URL_MINI="http://127.0.0.1:8080"

echo ""
echo "2.1 健康检查"
echo "---"
HEALTH_MINI=$(curl -s "$BASE_URL_MINI/healthz" 2>/dev/null || echo "")
if [ -n "$HEALTH_MINI" ]; then
    echo "✅ MiniApp API 健康检查通过"
    echo "响应: $HEALTH_MINI"
else
    echo "❌ MiniApp API 健康检查失败"
fi
echo ""

echo "2.2 API 文档"
echo "---"
echo "Swagger UI: $BASE_URL_MINI/docs"
if curl -s -o /dev/null -w '%{http_code}' "$BASE_URL_MINI/docs" | grep -q "200"; then
    echo "✅ API 文档可访问"
else
    echo "⚠️  API 文档不可访问"
fi
echo ""

echo "2.3 测试常用端点"
echo "---"

# 测试用户信息
echo "用户信息 API:"
curl -s "$BASE_URL_MINI/api/user/info?user_id=123456" 2>/dev/null | head -10 || echo "  端点不存在或需要认证"
echo ""

# 测试余额查询
echo "余额查询 API:"
curl -s "$BASE_URL_MINI/api/user/balance?user_id=123456" 2>/dev/null | head -10 || echo "  端点不存在或需要认证"
echo ""

echo "===================================="
echo "3️⃣ 服务状态检查"
echo "===================================="

echo ""
echo "Web Admin 服务状态:"
docker compose -f docker-compose.production.yml ps web_admin | tail -1
echo ""

echo "MiniApp API 服务状态:"
docker compose -f docker-compose.production.yml ps miniapp_api | tail -1
echo ""

echo "===================================="
echo "4️⃣ 测试总结"
echo "===================================="

PASS_COUNT=0
TOTAL_COUNT=0

# 检查 Web Admin
if [ -n "$HEALTH_WEB" ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
fi
TOTAL_COUNT=$((TOTAL_COUNT + 1))

# 检查 MiniApp API
if [ -n "$HEALTH_MINI" ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
fi
TOTAL_COUNT=$((TOTAL_COUNT + 1))

echo ""
echo "测试结果: $PASS_COUNT/$TOTAL_COUNT 通过"

if [ "$PASS_COUNT" -eq "$TOTAL_COUNT" ]; then
    echo "✅ 所有 API 健康检查通过"
else
    echo "⚠️  部分 API 测试失败"
fi
echo ""

echo "===================================="
echo "5️⃣ 访问信息"
echo "===================================="

echo ""
echo "Web Admin API:"
echo "  健康检查: $BASE_URL_WEB/healthz"
echo "  API 文档: $BASE_URL_WEB/docs"
echo ""

echo "MiniApp API:"
echo "  健康检查: $BASE_URL_MINI/healthz"
echo "  API 文档: $BASE_URL_MINI/docs"
echo ""

REMOTE_SCRIPT

