#!/bin/bash
# 检查服务器上的服务状态

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔍 检查服务状态"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "检查 Docker 服务状态："
docker compose -f docker-compose.production.yml ps
echo ""

echo "检查端口监听："
netstat -tlnp 2>/dev/null | grep -E ":8000|:8080" || ss -tlnp 2>/dev/null | grep -E ":8000|:8080"
echo ""

echo "测试本地访问："
echo "Web Admin API:"
curl -s http://127.0.0.1:8000/healthz || echo "本地访问失败"
echo ""
echo "MiniApp API:"
curl -s http://127.0.0.1:8080/healthz || echo "本地访问失败"
echo ""

REMOTE_SCRIPT

