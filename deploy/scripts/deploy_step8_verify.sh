#!/bin/bash
# 部署步骤 8: 验证部署

set -e

echo "🔍 开始验证部署..."
echo ""

# 等待服务启动
echo "⏳ 等待服务启动（10秒）..."
sleep 10
echo ""

# 检查后端服务
echo "🔍 检查后端服务 (端口 8000)..."
if curl -f -s http://localhost:8000/healthz > /dev/null 2>&1; then
    echo "✅ 后端服务健康检查通过"
    curl -s http://localhost:8000/healthz | python3 -m json.tool
else
    echo "❌ 后端服务健康检查失败"
    echo "   请检查日志: tail -f logs/web_admin.log"
fi
echo ""

# 检查 MiniApp API
echo "🔍 检查 MiniApp API (端口 8080)..."
if curl -f -s http://localhost:8080/healthz > /dev/null 2>&1; then
    echo "✅ MiniApp API 健康检查通过"
    curl -s http://localhost:8080/healthz | python3 -m json.tool
else
    echo "❌ MiniApp API 健康检查失败"
    echo "   请检查日志: tail -f logs/miniapp_api.log"
fi
echo ""

# 检查前端服务
echo "🔍 检查前端服务 (端口 3001)..."
if curl -f -s http://localhost:3001 > /dev/null 2>&1; then
    echo "✅ 前端服务响应正常"
else
    echo "❌ 前端服务响应异常"
    echo "   请检查日志: tail -f logs/frontend.log"
fi
echo ""

# 检查 Nginx
echo "🔍 检查 Nginx..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx 服务运行中"
else
    echo "❌ Nginx 服务未运行"
    echo "   启动命令: sudo systemctl start nginx"
fi
echo ""

# 检查端口占用
echo "🔍 检查端口占用..."
PORTS=(8000 8080 3001)
for PORT in "${PORTS[@]}"; do
    if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
        echo "✅ 端口 $PORT 正在监听"
    else
        echo "❌ 端口 $PORT 未监听"
    fi
done
echo ""

# 测试 API 端点
echo "🔍 测试 API 端点..."
if curl -f -s http://localhost:8000/admin/api/v1/dashboard/public > /dev/null 2>&1; then
    echo "✅ Dashboard API 可访问"
else
    echo "⚠️  Dashboard API 不可访问（可能需要认证）"
fi
echo ""

echo "✅ 验证完成"
echo ""
echo "📊 部署总结:"
echo "============"
echo "后端服务: http://localhost:8000"
echo "MiniApp API: http://localhost:8080"
echo "前端控制台: http://localhost:3001"
echo ""
echo "如果配置了域名和 Nginx，可以通过以下地址访问:"
echo "前端控制台: https://yourdomain.com"
echo "Web Admin: https://yourdomain.com/admin/dashboard"
echo ""
echo "📝 查看日志:"
echo "tail -f logs/web_admin.log"
echo "tail -f logs/miniapp_api.log"
echo "tail -f logs/frontend.log"

