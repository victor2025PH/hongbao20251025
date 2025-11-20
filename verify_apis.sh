#!/bin/bash
# 验证 API 服务

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔍 验证 API 服务状态"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "等待 20 秒让 API 服务完全启动..."
sleep 20

echo "===================================="
echo "1️⃣ Web Admin API 测试"
echo "===================================="

echo ""
echo "1.1 健康检查"
HEALTH_WEB=$(curl -s -f http://127.0.0.1:8000/healthz 2>&1)
if echo "$HEALTH_WEB" | grep -q "ok"; then
    echo "✅ Web Admin API 健康检查通过"
    echo "响应: $HEALTH_WEB"
else
    echo "❌ Web Admin API 健康检查失败"
    echo "错误: $HEALTH_WEB"
fi
echo ""

echo "1.2 API 文档"
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/docs 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API 文档可访问 (HTTP $HTTP_CODE)"
    echo "   地址: http://127.0.0.1:8000/docs"
else
    echo "⚠️  API 文档不可访问 (HTTP $HTTP_CODE)"
fi
echo ""

echo "1.3 服务日志"
docker compose -f docker-compose.production.yml logs web_admin --tail 10 | tail -5
echo ""

echo "===================================="
echo "2️⃣ MiniApp API 测试"
echo "===================================="

echo ""
echo "2.1 健康检查"
HEALTH_MINI=$(curl -s -f http://127.0.0.1:8080/healthz 2>&1)
if echo "$HEALTH_MINI" | grep -q "ok"; then
    echo "✅ MiniApp API 健康检查通过"
    echo "响应: $HEALTH_MINI"
else
    echo "❌ MiniApp API 健康检查失败"
    echo "错误: $HEALTH_MINI"
fi
echo ""

echo "2.2 API 文档"
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/docs 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API 文档可访问 (HTTP $HTTP_CODE)"
    echo "   地址: http://127.0.0.1:8080/docs"
else
    echo "⚠️  API 文档不可访问 (HTTP $HTTP_CODE)"
fi
echo ""

echo "2.3 服务日志"
docker compose -f docker-compose.production.yml logs miniapp_api --tail 10 | tail -5
echo ""

echo "===================================="
echo "3️⃣ 总结"
echo "===================================="

echo ""
echo "✅ API 测试完成"
echo ""
echo "访问地址："
echo "  Web Admin API:"
echo "    健康检查: curl http://127.0.0.1:8000/healthz"
echo "    API 文档: http://127.0.0.1:8000/docs"
echo ""
echo "  MiniApp API:"
echo "    健康检查: curl http://127.0.0.1:8080/healthz"
echo "    API 文档: http://127.0.0.1:8080/docs"
echo ""

REMOTE_SCRIPT

