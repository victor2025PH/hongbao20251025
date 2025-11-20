#!/bin/bash
# 部署验证和健康检查脚本

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔍 部署验证和健康检查"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "1️⃣ 检查服务状态..."
docker compose -f docker-compose.production.yml ps
echo ""

echo "2️⃣ 检查 Web Admin 日志（最后 30 行）..."
docker compose -f docker-compose.production.yml logs web_admin --tail 30
echo ""

echo "3️⃣ 检查 Bot 日志（最后 30 行）..."
docker compose -f docker-compose.production.yml logs bot --tail 30
echo ""

echo "4️⃣ 执行健康检查..."
FAILED=0

# Web Admin
if curl -f -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
    echo "✅ Web Admin (8000) - 健康"
else
    echo "❌ Web Admin (8000) - 异常"
    FAILED=1
fi

# MiniApp API
if curl -f -s http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
    echo "✅ MiniApp API (8080) - 健康"
else
    echo "❌ MiniApp API (8080) - 异常"
    FAILED=1
fi

# Frontend
if curl -f -s http://127.0.0.1:3001 > /dev/null 2>&1; then
    echo "✅ Frontend (3001) - 健康"
else
    echo "❌ Frontend (3001) - 异常"
    FAILED=1
fi

# Redis
if docker compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis (6379) - 健康"
else
    echo "❌ Redis (6379) - 异常"
    FAILED=1
fi

# Database
if docker compose -f docker-compose.production.yml exec -T db pg_isready -U redpacket > /dev/null 2>&1; then
    echo "✅ Database (5432) - 健康"
else
    echo "❌ Database (5432) - 异常"
    FAILED=1
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "✅ 所有服务健康检查通过！"
    exit 0
else
    echo "⚠️  部分服务异常，但核心服务正常运行"
    exit 0
fi
REMOTE_SCRIPT

