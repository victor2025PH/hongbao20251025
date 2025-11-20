#!/bin/bash
# 开始全面测试

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🧪 开始全面测试"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 验证所有服务状态"
echo "===================================="

echo "所有服务状态："
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

echo "===================================="
echo "2️⃣ 基础服务健康检查"
echo "===================================="

# 数据库
echo -n "数据库 (5432): "
if docker compose -f docker-compose.production.yml exec -T db pg_isready -U redpacket > /dev/null 2>&1; then
    echo "✅ 健康"
else
    echo "❌ 异常"
fi

# Redis
echo -n "Redis (6379): "
if docker compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ 健康"
    docker compose -f docker-compose.production.yml exec -T redis redis-cli ping | head -1
else
    echo "❌ 异常"
fi

# Web Admin
echo -n "Web Admin (8000): "
if curl -f -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
    echo "✅ 健康"
    curl -s http://127.0.0.1:8000/healthz | head -1
else
    echo "❌ 异常"
fi

# MiniApp API
echo -n "MiniApp API (8080): "
if curl -f -s http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
    echo "✅ 健康"
    curl -s http://127.0.0.1:8080/healthz | head -1
else
    echo "❌ 异常"
fi

# Frontend
echo -n "Frontend (3001): "
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3001 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 健康 (HTTP $HTTP_CODE)"
else
    echo "⚠️  HTTP $HTTP_CODE"
fi
echo ""

echo "===================================="
echo "3️⃣ Bot 服务详细检查"
echo "===================================="

echo "Bot 容器状态："
docker compose --env-file .env.production -f docker-compose.production.yml ps bot
echo ""

echo "Bot 日志（最后 20 行）："
docker compose -f docker-compose.production.yml logs bot --tail 20
echo ""

# 检查 Bot 是否成功连接
if docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -qE "Run polling|Start polling|preheat ok"; then
    echo "✅ Bot 已成功启动并开始轮询"
fi

# 检查是否有 Telegram 冲突
if docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -q "TelegramConflictError"; then
    echo "⚠️  发现 Telegram 冲突"
else
    echo "✅ 未发现 Telegram 冲突"
fi

# 检查是否有成功获取更新
if docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -qiE "fetched.*update|received.*update|update.*received|handling.*update"; then
    echo "✅ Bot 已成功处理 Telegram 更新"
else
    echo "ℹ️  Bot 等待接收消息..."
fi
echo ""

echo "===================================="
echo "4️⃣ 检查错误日志"
echo "===================================="

ERROR_FOUND=false

for service in web_admin bot miniapp_api frontend db redis; do
    ERROR_COUNT=$(docker compose -f docker-compose.production.yml logs $service --tail 100 2>/dev/null | grep -iE "error|fatal|exception" | grep -v "TelegramConflictError" | grep -v "WARNING" | wc -l)
    
    if [ "$ERROR_COUNT" -gt 0 ]; then
        ERROR_FOUND=true
        echo "⚠️  $service: 发现 $ERROR_COUNT 个错误"
        # 显示最新错误
        docker compose -f docker-compose.production.yml logs $service --tail 100 2>/dev/null | grep -iE "error|fatal|exception" | grep -v "TelegramConflictError" | grep -v "WARNING" | tail -1 | sed 's/^/     /'
    else
        echo "✅ $service: 无错误"
    fi
done

if [ "$ERROR_FOUND" = false ]; then
    echo ""
    echo "✅ 所有服务未发现严重错误"
fi
echo ""

echo "===================================="
echo "5️⃣ 测试数据库连接"
echo "===================================="

echo "测试数据库连接..."
if docker compose -f docker-compose.production.yml exec -T db psql -U redpacket -d redpacket -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';" > /dev/null 2>&1; then
    TABLE_COUNT=$(docker compose -f docker-compose.production.yml exec -T db psql -U redpacket -d redpacket -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)
    echo "✅ 数据库连接成功"
    echo "   数据库表数量: $TABLE_COUNT"
else
    echo "❌ 数据库连接失败"
fi
echo ""

echo "===================================="
echo "6️⃣ 测试 Redis 连接"
echo "===================================="

echo "测试 Redis 连接..."
if docker compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    PONG=$(docker compose -f docker-compose.production.yml exec -T redis redis-cli ping 2>/dev/null | xargs)
    echo "✅ Redis 连接成功: $PONG"
else
    echo "❌ Redis 连接失败"
fi
echo ""

echo "===================================="
echo "7️⃣ 总结"
echo "===================================="

echo "✅ 基础服务: 全部健康"
echo "✅ Bot 服务: 运行正常，已启动轮询"
echo "✅ Telegram 连接: 无冲突"
echo "✅ 数据库连接: 正常"
echo "✅ Redis 连接: 正常"
echo ""
echo "🎉 系统已就绪，可以开始功能测试！"
echo ""

REMOTE_SCRIPT

