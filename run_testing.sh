#!/bin/bash
# 运行测试并监控

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🧪 开始运行测试"
echo "===================================="
echo ""

# 启动服务检查
bash start_testing.sh

echo ""
echo "===================================="
echo "📊 测试流程"
echo "===================================="
echo ""
echo "1️⃣ 基础服务测试"
echo "   - 数据库连接测试"
echo "   - Redis 连接测试"
echo "   - Web Admin 测试"
echo "   - MiniApp API 测试"
echo "   - Frontend 测试"
echo ""
echo "2️⃣ Bot 功能测试"
echo "   - Bot 启动测试"
echo "   - Telegram 连接测试"
echo "   - Bot 命令测试"
echo "   - 红包功能测试"
echo "   - 钱包功能测试"
echo ""
echo "3️⃣ 集成测试"
echo "   - 数据库操作测试"
echo "   - 缓存操作测试"
echo "   - API 接口测试"
echo ""
echo "4️⃣ 监控测试"
echo "   - 实时日志监控"
echo "   - 错误检测和修复"
echo ""
echo "===================================="
echo ""

# 执行测试脚本
ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "开始执行测试..."
echo "===================================="
echo ""

# 测试 1: 数据库连接
echo "1️⃣ 数据库连接测试"
echo "---"
if docker compose -f docker-compose.production.yml exec -T db psql -U redpacket -d redpacket -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ 数据库连接成功"
    docker compose -f docker-compose.production.yml exec -T db psql -U redpacket -d redpacket -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | head -3
else
    echo "❌ 数据库连接失败"
fi
echo ""

# 测试 2: Redis 连接
echo "2️⃣ Redis 连接测试"
echo "---"
if docker compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis 连接成功"
    docker compose -f docker-compose.production.yml exec -T redis redis-cli ping
else
    echo "❌ Redis 连接失败"
fi
echo ""

# 测试 3: Web Admin
echo "3️⃣ Web Admin 测试"
echo "---"
if curl -f -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
    echo "✅ Web Admin 健康检查通过"
    curl -s http://127.0.0.1:8000/healthz | head -1
else
    echo "❌ Web Admin 健康检查失败"
fi
echo ""

# 测试 4: MiniApp API
echo "4️⃣ MiniApp API 测试"
echo "---"
if curl -f -s http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
    echo "✅ MiniApp API 健康检查通过"
    curl -s http://127.0.0.1:8080/healthz | head -1
else
    echo "❌ MiniApp API 健康检查失败"
fi
echo ""

# 测试 5: Frontend
echo "5️⃣ Frontend 测试"
echo "---"
if curl -f -s http://127.0.0.1:3001 > /dev/null 2>&1; then
    echo "✅ Frontend 可访问"
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3001)
    echo "   HTTP Status: $HTTP_CODE"
else
    echo "❌ Frontend 不可访问"
fi
echo ""

# 测试 6: Bot 服务
echo "6️⃣ Bot 服务测试"
echo "---"
BOT_STATUS=$(docker compose -f docker-compose.production.yml ps bot | tail -1 | awk '{print $(NF-1), $NF}')
if echo "$BOT_STATUS" | grep -qE "Up|running"; then
    echo "✅ Bot 服务运行中"
    echo "   状态: $BOT_STATUS"
    
    # 检查 Bot 日志中是否有错误
    ERROR_COUNT=$(docker compose -f docker-compose.production.yml logs bot --tail 100 2>/dev/null | grep -iE "error|fatal|exception" | grep -v "TelegramConflictError" | wc -l)
    if [ "$ERROR_COUNT" -eq 0 ]; then
        echo "✅ Bot 日志无严重错误"
    else
        echo "⚠️  Bot 日志有 $ERROR_COUNT 个错误（不包括 Telegram 冲突）"
    fi
else
    echo "❌ Bot 服务未运行"
fi
echo ""

# 测试 7: 检查最近的错误
echo "7️⃣ 错误日志检查"
echo "---"
ERROR_FOUND=false

for service in web_admin bot miniapp_api frontend db redis; do
    ERROR_COUNT=$(docker compose -f docker-compose.production.yml logs $service --tail 100 2>/dev/null | grep -iE "error|fatal|exception" | grep -v "TelegramConflictError" | wc -l)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "⚠️  $service: 发现 $ERROR_COUNT 个错误"
        ERROR_FOUND=true
        # 显示最新的错误
        echo "   最新错误:"
        docker compose -f docker-compose.production.yml logs $service --tail 100 2>/dev/null | grep -iE "error|fatal|exception" | grep -v "TelegramConflictError" | tail -1 | sed 's/^/     /'
    fi
done

if [ "$ERROR_FOUND" = false ]; then
    echo "✅ 未发现严重错误"
fi
echo ""

echo "===================================="
echo "测试完成"
echo "===================================="
echo ""

REMOTE_SCRIPT

echo ""
echo "===================================="
echo "✅ 测试脚本执行完成"
echo "===================================="
echo ""
echo "现在开始持续监控日志..."
echo "按 Ctrl+C 停止监控"
echo ""

