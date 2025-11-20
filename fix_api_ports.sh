#!/bin/bash
# 修复 API 端口绑定，允许外部访问

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔧 修复 API 端口绑定"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 拉取最新代码"
echo "===================================="

git pull origin master
echo ""

echo "===================================="
echo "2️⃣ 更新端口绑定配置"
echo "===================================="

# 更新 Web Admin 端口
sed -i 's/"127.0.0.1:8000:8000"/"0.0.0.0:8000:8000"/g' docker-compose.production.yml

# 更新 MiniApp API 端口
sed -i 's/"127.0.0.1:8080:8080"/"0.0.0.0:8080:8080"/g' docker-compose.production.yml

echo "✅ 端口绑定已更新"
echo ""

echo "验证配置："
grep -A 1 "web_admin:" docker-compose.production.yml | grep "ports:" -A 1
grep -A 1 "miniapp_api:" docker-compose.production.yml | grep "ports:" -A 1
echo ""

echo "===================================="
echo "3️⃣ 重启 API 服务"
echo "===================================="

echo "重新创建并启动服务..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d web_admin miniapp_api

echo ""
echo "等待 15 秒让服务完全启动..."
sleep 15
echo ""

echo "===================================="
echo "4️⃣ 验证端口绑定"
echo "===================================="

echo "检查端口监听："
netstat -tlnp 2>/dev/null | grep -E ":8000|:8080" || ss -tlnp 2>/dev/null | grep -E ":8000|:8080"
echo ""

echo "===================================="
echo "5️⃣ 测试外部访问"
echo "===================================="

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "165.154.233.55")

echo "测试 Web Admin API..."
echo "  本地访问: curl http://127.0.0.1:8000/healthz"
curl -s http://127.0.0.1:8000/healthz | head -1
echo ""

echo "测试 MiniApp API..."
echo "  本地访问: curl http://127.0.0.1:8080/healthz"
curl -s http://127.0.0.1:8080/healthz | head -1
echo ""

echo "===================================="
echo "6️⃣ 访问地址"
echo "===================================="

echo ""
echo "服务器公网 IP: $PUBLIC_IP"
echo ""
echo "Web Admin API:"
echo "  健康检查: http://$PUBLIC_IP:8000/healthz"
echo "  API 文档: http://$PUBLIC_IP:8000/docs"
echo ""
echo "MiniApp API:"
echo "  健康检查: http://$PUBLIC_IP:8080/healthz"
echo "  API 文档: http://$PUBLIC_IP:8080/docs"
echo ""
echo "⚠️  注意："
echo "  • 如果无法访问，请检查服务器防火墙设置"
echo "  • 确保防火墙允许 8000 和 8080 端口的访问"
echo ""

REMOTE_SCRIPT

