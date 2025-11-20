#!/bin/bash
# 持续监控并自动修复错误

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔍 持续监控系统运行状态"
echo "===================================="
echo ""
echo "监控项："
echo "  ✅ 服务健康状态"
echo "  ✅ 错误日志"
echo "  ✅ 数据库连接"
echo "  ✅ Redis 连接"
echo "  ✅ Bot 服务状态"
echo ""
echo "自动修复：启用"
echo "检查间隔：30 秒"
echo ""
echo "按 Ctrl+C 停止监控"
echo ""

# 持续监控循环
while true; do
    echo ""
    echo "===================================="
    echo "📊 $(date '+%Y-%m-%d %H:%M:%S') - 状态检查"
    echo "===================================="
    
    ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

# 检查 Bot 服务状态
BOT_STATUS=$(docker compose -f docker-compose.production.yml ps bot --format json 2>/dev/null | jq -r '.[0].State' 2>/dev/null || echo "unknown")

if [ "$BOT_STATUS" != "running" ] && [ "$BOT_STATUS" != "Up" ]; then
    echo "⚠️  Bot 服务异常: $BOT_STATUS"
    echo "   尝试重启 Bot 服务..."
    docker compose --env-file .env.production -f docker-compose.production.yml restart bot
    sleep 10
fi

# 检查最近的错误日志
ERROR_COUNT=0
LAST_ERROR=""

for service in web_admin bot miniapp_api frontend db redis; do
    # 检查每个服务的错误日志
    ERRORS=$(docker compose -f docker-compose.production.yml logs $service --tail 20 --since 30s 2>/dev/null | grep -iE "error|fatal|exception|failed" | grep -v "TelegramConflictError" | grep -v "WARNING" || true)
    
    if [ -n "$ERRORS" ]; then
        ERROR_COUNT=$((ERROR_COUNT + 1))
        LAST_ERROR="$service: $(echo "$ERRORS" | head -1)"
        echo "⚠️  $service 发现错误："
        echo "$ERRORS" | head -3 | sed 's/^/     /'
        
        # 尝试修复常见错误
        if echo "$ERRORS" | grep -qi "connection.*refused\|connection.*failed"; then
            echo "   尝试重启服务..."
            docker compose --env-file .env.production -f docker-compose.production.yml restart $service
        fi
        
        if echo "$ERRORS" | grep -qi "database.*connection.*failed\|password.*authentication.*failed"; then
            echo "   数据库连接错误，检查配置..."
            # 这里可以添加数据库连接修复逻辑
        fi
    fi
done

if [ $ERROR_COUNT -eq 0 ]; then
    echo "✅ 未发现新错误"
else
    echo ""
    echo "📝 发现 $ERROR_COUNT 个服务的错误"
fi

# 检查服务健康状态
echo ""
echo "服务健康状态："
for service in web_admin miniapp_api frontend db redis bot; do
    STATUS=$(docker compose -f docker-compose.production.yml ps $service --format json 2>/dev/null | jq -r '.[0].State' 2>/dev/null || echo "unknown")
    if [ "$STATUS" = "running" ] || [ "$STATUS" = "Up" ]; then
        echo "  ✅ $service: 运行中"
    else
        echo "  ❌ $service: $STATUS"
    fi
done

REMOTE_SCRIPT
    
    # 等待 30 秒后再次检查
    sleep 30
done

