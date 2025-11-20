#!/bin/bash
# 启动测试并监控

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🚀 启动测试并监控"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 检查所有服务状态"
echo "===================================="
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

echo "===================================="
echo "2️⃣ 确保所有服务正在运行"
echo "===================================="

# 检查并启动所有服务
docker compose --env-file .env.production -f docker-compose.production.yml up -d
echo ""

echo "等待 10 秒让服务完全启动..."
sleep 10
echo ""

echo "===================================="
echo "3️⃣ 服务健康检查"
echo "===================================="

# Web Admin
echo -n "Web Admin (8000): "
if curl -f -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
    echo "✅ 健康"
else
    echo "❌ 异常"
fi

# MiniApp API
echo -n "MiniApp API (8080): "
if curl -f -s http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
    echo "✅ 健康"
else
    echo "❌ 异常"
fi

# Frontend
echo -n "Frontend (3001): "
if curl -f -s http://127.0.0.1:3001 > /dev/null 2>&1; then
    echo "✅ 健康"
else
    echo "❌ 异常"
fi

# Database
echo -n "Database (5432): "
if docker compose -f docker-compose.production.yml exec -T db pg_isready -U redpacket > /dev/null 2>&1; then
    echo "✅ 健康"
else
    echo "❌ 异常"
fi

# Redis
echo -n "Redis (6379): "
if docker compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ 健康"
else
    echo "❌ 异常"
fi
echo ""

echo "===================================="
echo "4️⃣ 检查 Bot 服务状态"
echo "===================================="
docker compose --env-file .env.production -f docker-compose.production.yml ps bot
echo ""

echo "===================================="
echo "5️⃣ 检查最近的错误日志"
echo "===================================="

# 检查所有服务的错误日志
echo "检查各服务的错误（ERROR/FATAL/Exception）："
echo ""

for service in web_admin bot miniapp_api frontend db redis; do
    echo "--- $service 服务错误 ---"
    docker compose -f docker-compose.production.yml logs $service --tail 50 2>/dev/null | grep -iE "error|fatal|exception|failed" | tail -3 || echo "  无错误"
    echo ""
done

echo "===================================="
echo "✅ 服务检查完成"
echo "===================================="
echo ""

REMOTE_SCRIPT

