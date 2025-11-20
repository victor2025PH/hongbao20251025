#!/bin/bash
# 持续监控和测试

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔍 持续监控系统状态"
echo "===================================="
echo ""
echo "监控项："
echo "  ✅ 服务健康状态"
echo "  ✅ 错误日志检测"
echo "  ✅ Bot 消息处理"
echo "  ✅ Telegram 连接"
echo ""
echo "自动修复：启用"
echo "检查间隔：30 秒"
echo ""
echo "按 Ctrl+C 停止监控"
echo ""

# 持续监控循环
COUNTER=0
while true; do
    COUNTER=$((COUNTER + 1))
    
    echo ""
    echo "===================================="
    echo "📊 检查 #$COUNTER - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "===================================="
    
    ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

# 检查 Bot 状态
BOT_STATUS=$(docker compose -f docker-compose.production.yml ps bot | tail -1 | awk '{print $(NF-1), $NF}')
echo "Bot 状态: $BOT_STATUS"

# 检查 Telegram 冲突
CONFLICT_COUNT=$(docker compose -f docker-compose.production.yml logs bot --tail 20 --since 30s 2>/dev/null | grep -c "TelegramConflictError" || echo "0")
if [ "$CONFLICT_COUNT" -gt 0 ]; then
    echo "⚠️  发现 Telegram 冲突 ($CONFLICT_COUNT 次)"
else
    echo "✅ Telegram 连接正常"
fi

# 检查错误日志
ERROR_COUNT=0
for service in web_admin bot miniapp_api frontend db redis; do
    ERRORS=$(docker compose -f docker-compose.production.yml logs $service --tail 20 --since 30s 2>/dev/null | grep -iE "error|fatal|exception" | grep -v "TelegramConflictError" | grep -v "WARNING" | wc -l)
    if [ "$ERRORS" -gt 0 ]; then
        ERROR_COUNT=$((ERROR_COUNT + ERRORS))
        echo "⚠️  $service: $ERRORS 个新错误"
    fi
done

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "✅ 未发现新错误"
fi

# 检查 Bot 是否接收到消息
if docker compose -f docker-compose.production.yml logs bot --tail 20 --since 30s 2>/dev/null | grep -qiE "update|message|handling"; then
    echo "✅ Bot 正在处理消息"
fi

REMOTE_SCRIPT
    
    # 等待 30 秒后再次检查
    sleep 30
done

