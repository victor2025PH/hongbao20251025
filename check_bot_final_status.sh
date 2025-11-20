#!/bin/bash
# 检查 Bot 最终状态

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "📊 检查 Bot 最终状态"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ Bot 服务状态"
echo "===================================="

docker compose --env-file .env.production -f docker-compose.production.yml ps bot
echo ""

echo "===================================="
echo "2️⃣ Bot 日志（最后 30 行）"
echo "===================================="

docker compose -f docker-compose.production.yml logs bot --tail 30
echo ""

echo "===================================="
echo "3️⃣ 检查 Telegram 冲突"
echo "===================================="

# 检查最近的错误
CONFLICT_COUNT=$(docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -c "TelegramConflictError" || echo "0")
LAST_ERROR_TIME=$(docker compose -f docker-compose.production.yml logs bot --tail 100 2>/dev/null | grep "TelegramConflictError" | tail -1 | cut -d'|' -f1 | xargs || echo "")

if [ "$CONFLICT_COUNT" -gt 0 ]; then
    echo "⚠️  仍然存在 Telegram 冲突"
    echo "   冲突次数: $CONFLICT_COUNT"
    if [ -n "$LAST_ERROR_TIME" ]; then
        echo "   最后错误时间: $LAST_ERROR_TIME"
    fi
    echo ""
    
    # 检查最近的日志是否有成功连接
    SUCCESS_LOGS=$(docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -iE "successfully|connected|received.*update" | tail -3 || echo "")
    
    if [ -n "$SUCCESS_LOGS" ]; then
        echo "   但最近有成功连接："
        echo "$SUCCESS_LOGS" | sed 's/^/     /'
    fi
else
    echo "✅ Telegram 冲突已解决！"
fi
echo ""

echo "===================================="
echo "4️⃣ 检查 Bot 是否正常运行"
echo "===================================="

# 检查 Bot 是否成功启动
if docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -qE "Start polling|Run polling|preheat ok"; then
    echo "✅ Bot 已成功启动并开始轮询"
    
    # 检查是否有成功获取更新的日志
    if docker compose -f docker-compose.production.yml logs bot --tail 100 2>/dev/null | grep -qiE "fetched.*update|received.*update|update.*received"; then
        echo "✅ Bot 已成功获取 Telegram 更新"
    else
        echo "⚠️  Bot 尚未获取到更新（可能仍在等待或冲突中）"
    fi
else
    echo "❌ Bot 未成功启动"
fi
echo ""

echo "===================================="
echo "5️⃣ 检查所有进程"
echo "===================================="

echo "所有 Bot 相关进程："
ps aux | grep -E "python.*app\.py|bot" | grep -v grep || echo "  ✅ 无额外进程"
echo ""

echo "所有 Bot 相关容器："
docker ps -a | grep -E "bot|backend" | head -5 || echo "  ✅ 无其他容器"
echo ""

echo "===================================="
echo "6️⃣ 最终状态总结"
echo "===================================="

STATUS=$(docker compose -f docker-compose.production.yml ps bot | tail -1 | awk '{print $(NF-1), $NF}')

if echo "$STATUS" | grep -qE "Up|running"; then
    if [ "$CONFLICT_COUNT" -eq 0 ] || docker compose -f docker-compose.production.yml logs bot --tail 20 2>/dev/null | grep -qiE "fetched.*update|received.*update"; then
        echo "✅ Bot 服务正常运行，Telegram 连接成功！"
        echo ""
        echo "状态: 可以开始测试 Bot 功能"
    else
        echo "⚠️  Bot 服务运行中，但 Telegram 仍有冲突"
        echo ""
        echo "状态: 需要继续等待或检查其他 Bot 实例"
    fi
else
    echo "❌ Bot 服务未正常运行"
    echo "   状态: $STATUS"
fi
echo ""

REMOTE_SCRIPT

