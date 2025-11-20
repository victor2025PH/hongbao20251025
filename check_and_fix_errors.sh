#!/bin/bash
# 检查并修复错误

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔍 检查错误并修复"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 检查 Bot 服务状态"
echo "===================================="

BOT_STATUS=$(docker compose -f docker-compose.production.yml ps bot --format json 2>/dev/null | jq -r '.[0].State' 2>/dev/null || echo "unknown")
HEALTH_STATUS=$(docker compose -f docker-compose.production.yml ps bot | tail -1 | grep -oE "unhealthy|healthy" || echo "")

echo "Bot 状态: $BOT_STATUS"
echo "健康状态: ${HEALTH_STATUS:-未设置}"
echo ""

if [ "$HEALTH_STATUS" = "unhealthy" ]; then
    echo "⚠️  Bot 服务显示 unhealthy"
    echo ""
    echo "检查 Bot 日志（最后 30 行）:"
    docker compose -f docker-compose.production.yml logs bot --tail 30
    echo ""
fi

echo "===================================="
echo "2️⃣ 检查所有服务的错误"
echo "===================================="

ERROR_FOUND=false

for service in web_admin bot miniapp_api frontend db redis; do
    echo ""
    echo "--- $service 服务错误检查 ---"
    
    # 获取最近 50 行的错误日志
    ERRORS=$(docker compose -f docker-compose.production.yml logs $service --tail 50 2>/dev/null | grep -iE "error|fatal|exception|failed" | grep -v "TelegramConflictError" | grep -v "WARNING" || true)
    
    if [ -n "$ERRORS" ]; then
        ERROR_FOUND=true
        ERROR_COUNT=$(echo "$ERRORS" | wc -l)
        echo "发现 $ERROR_COUNT 个错误："
        echo "$ERRORS" | head -5 | sed 's/^/  /'
        
        # 分析错误类型
        if echo "$ERRORS" | grep -qi "connection.*refused\|connection.*failed"; then
            echo "  ⚠️  连接错误：可能是服务未启动或网络问题"
        fi
        
        if echo "$ERRORS" | grep -qi "database.*connection.*failed\|password.*authentication.*failed"; then
            echo "  ⚠️  数据库连接错误：检查数据库配置"
        fi
        
        if echo "$ERRORS" | grep -qi "timeout"; then
            echo "  ⚠️  超时错误：可能是服务响应慢"
        fi
    else
        echo "✅ 未发现错误"
    fi
done

echo ""

if [ "$ERROR_FOUND" = false ]; then
    echo "✅ 所有服务未发现严重错误"
else
    echo "⚠️  发现了一些错误，需要检查"
fi
echo ""

echo "===================================="
echo "3️⃣ 服务健康检查"
echo "===================================="

# 检查所有服务的健康状态
for service in web_admin miniapp_api frontend db redis bot; do
    STATUS=$(docker compose -f docker-compose.production.yml ps $service --format json 2>/dev/null | jq -r '.[0].State' 2>/dev/null || echo "unknown")
    HEALTH=$(docker compose -f docker-compose.production.yml ps $service | tail -1 | grep -oE "unhealthy|healthy" || echo "")
    
    if [ "$STATUS" = "running" ] || [ "$STATUS" = "Up" ]; then
        if [ -z "$HEALTH" ]; then
            echo "  ✅ $service: 运行中（无健康检查）"
        elif [ "$HEALTH" = "healthy" ]; then
            echo "  ✅ $service: 健康"
        else
            echo "  ⚠️  $service: 运行中但 $HEALTH"
        fi
    else
        echo "  ❌ $service: $STATUS"
    fi
done
echo ""

echo "===================================="
echo "4️⃣ 自动修复建议"
echo "===================================="

# 如果 Bot 服务 unhealthy，尝试修复
if [ "$HEALTH_STATUS" = "unhealthy" ]; then
    echo "尝试修复 Bot 服务..."
    
    # 检查是否是 Telegram 冲突
    TELEGRAM_CONFLICT=$(docker compose -f docker-compose.production.yml logs bot --tail 20 2>/dev/null | grep -i "TelegramConflictError" | wc -l)
    
    if [ "$TELEGRAM_CONFLICT" -gt 0 ]; then
        echo "  ⚠️  检测到 Telegram 冲突（多个 Bot 实例）"
        echo "  💡 建议：停止其他运行的 Bot 实例"
    else
        echo "  🔄 重启 Bot 服务..."
        docker compose --env-file .env.production -f docker-compose.production.yml restart bot
        echo "  ✅ Bot 服务已重启，等待 20 秒..."
        sleep 20
        
        # 再次检查状态
        NEW_STATUS=$(docker compose -f docker-compose.production.yml ps bot | tail -1 | grep -oE "unhealthy|healthy" || echo "")
        if [ "$NEW_STATUS" = "healthy" ]; then
            echo "  ✅ Bot 服务已恢复健康"
        else
            echo "  ⚠️  Bot 服务仍异常，需要进一步检查"
        fi
    fi
fi
echo ""

echo "===================================="
echo "✅ 检查完成"
echo "===================================="
echo ""

REMOTE_SCRIPT

