#!/bin/bash
# 检查 API 访问地址

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔍 检查 API 访问地址"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 检查端口绑定配置"
echo "===================================="

echo "检查 docker-compose.production.yml 中的端口配置："
echo ""

echo "Web Admin 端口配置："
grep -A 2 "web_admin:" docker-compose.production.yml | grep "ports:" -A 1 || echo "未找到"
echo ""

echo "MiniApp API 端口配置："
grep -A 2 "miniapp_api:" docker-compose.production.yml | grep "ports:" -A 1 || echo "未找到"
echo ""

echo "===================================="
echo "2️⃣ 检查实际监听的端口"
echo "===================================="

echo "检查服务器监听的端口："
netstat -tlnp 2>/dev/null | grep -E ":8000|:8080" || ss -tlnp 2>/dev/null | grep -E ":8000|:8080" || echo "无法获取端口信息"
echo ""

echo "===================================="
echo "3️⃣ 检查容器端口映射"
echo "===================================="

echo "Web Admin 容器端口："
docker compose -f docker-compose.production.yml ps web_admin | grep -oE "[0-9]+->[0-9]+" || docker compose -f docker-compose.production.yml ps web_admin
echo ""

echo "MiniApp API 容器端口："
docker compose -f docker-compose.production.yml ps miniapp_api | grep -oE "[0-9]+->[0-9]+" || docker compose -f docker-compose.production.yml ps miniapp_api
echo ""

echo "===================================="
echo "4️⃣ 测试本地访问"
echo "===================================="

echo "测试 Web Admin API (127.0.0.1:8000):"
curl -s http://127.0.0.1:8000/healthz 2>&1 | head -3 || echo "无法访问"
echo ""

echo "测试 MiniApp API (127.0.0.1:8080):"
curl -s http://127.0.0.1:8080/healthz 2>&1 | head -3 || echo "无法访问"
echo ""

echo "===================================="
echo "5️⃣ 获取服务器公网 IP"
echo "===================================="

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "165.154.233.55")
echo "服务器公网 IP: $PUBLIC_IP"
echo ""

REMOTE_SCRIPT

