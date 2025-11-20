#!/bin/bash
# 清理 Telegram 更新并重新启动

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔄 清理 Telegram 更新并重新启动"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 获取 Bot Token"
echo "===================================="

# 从环境变量获取 Bot Token
BOT_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" .env.production | cut -d'=' -f2 | tr -d '[:space:]' || echo "")

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ 未找到 TELEGRAM_BOT_TOKEN"
    echo "   尝试从其他环境变量获取..."
    BOT_TOKEN=$(grep -E "^BOT_TOKEN=|^TGBOT_TOKEN=" .env.production | cut -d'=' -f2 | tr -d '[:space:]' || echo "")
fi

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ 无法获取 Bot Token"
    echo "   将直接重启服务，等待 Telegram API 自动更新"
else
    echo "✅ 已获取 Bot Token（长度: ${#BOT_TOKEN}）"
    echo ""
    
    echo "===================================="
    echo "2️⃣ 清理 Telegram 更新"
    echo "===================================="
    
    echo "使用 Telegram Bot API 清理待处理的更新..."
    
    # 删除 webhook（如果有）
    echo "删除 webhook..."
    curl -s "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook?drop_pending_updates=true" | head -3
    echo ""
    
    # 获取并丢弃所有待处理的更新
    echo "丢弃所有待处理的更新..."
    curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?offset=-1&limit=1" > /dev/null 2>&1
    echo "✅ 已清理"
    echo ""
fi

echo "===================================="
echo "3️⃣ 停止 Bot 服务"
echo "===================================="

echo "停止 Docker 容器中的 Bot..."
docker compose --env-file .env.production -f docker-compose.production.yml stop bot 2>/dev/null || true
docker compose --env-file .env.production -f docker-compose.production.yml rm -f bot 2>/dev/null || true

# 停止所有 python app.py 进程
echo "停止所有 python app.py 进程..."
PIDS=$(ps aux | grep "python.*app\.py" | grep -v grep | awk '{print $2}')
for PID in $PIDS; do
    kill -TERM $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
done
sleep 3

# 强制停止剩余进程
PIDS=$(ps aux | grep "python.*app\.py" | grep -v grep | awk '{print $2}')
for PID in $PIDS; do
    kill -9 $PID 2>/dev/null || true
done

echo "✅ 所有 Bot 进程已停止"
echo ""

echo "===================================="
echo "4️⃣ 等待 Telegram API 更新"
echo "===================================="

echo "等待 15 秒让 Telegram API 完全更新..."
sleep 15
echo "✅ 等待完成"
echo ""

echo "===================================="
echo "5️⃣ 重新启动 Bot 服务"
echo "===================================="

echo "重新启动 Bot 服务..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d bot

echo ""
echo "等待 40 秒让 Bot 完全启动..."
sleep 40
echo ""

echo "===================================="
echo "6️⃣ 检查 Bot 状态"
echo "===================================="

echo "Bot 容器状态："
docker compose --env-file .env.production -f docker-compose.production.yml ps bot
echo ""

echo "Bot 日志（最后 25 行）："
docker compose -f docker-compose.production.yml logs bot --tail 25
echo ""

echo "===================================="
echo "7️⃣ 检查 Telegram 连接状态"
echo "===================================="

# 检查是否还有冲突
CONFLICT_COUNT=$(docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -c "TelegramConflictError" || echo "0")

if [ "$CONFLICT_COUNT" -gt 0 ]; then
    echo "⚠️  仍然存在 Telegram 冲突（检测到 $CONFLICT_COUNT 次）"
    echo ""
    echo "可能的原因："
    echo "  1. Telegram API 需要更长时间更新（可能需要 1-2 分钟）"
    echo "  2. 有其他服务器或本地环境在运行 Bot"
    echo "  3. Bot Token 被其他程序使用"
    echo ""
    echo "建议："
    echo "  1. 等待 1-2 分钟后再次检查"
    echo "  2. 检查是否有其他服务器运行 Bot"
    echo "  3. 考虑使用 Webhook 模式替代长轮询"
else
    echo "✅ Telegram 冲突已解决！"
    echo ""
    
    # 检查 Bot 是否成功启动
    if docker compose -f docker-compose.production.yml logs bot --tail 20 2>/dev/null | grep -qE "Start polling|Run polling|preheat ok"; then
        echo "✅ Bot 已成功启动并开始轮询"
        echo ""
        
        # 检查是否有成功获取更新的日志
        if docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -qE "Updates|Fetched"; then
            echo "✅ Bot 已成功获取 Telegram 更新"
        fi
    fi
fi
echo ""

echo "===================================="
echo "8️⃣ 验证进程状态"
echo "===================================="

echo "当前运行的 Bot 进程："
ps aux | grep "python.*app\.py" | grep -v grep || echo "  ✅ 无额外进程（只有容器内进程）"
echo ""

echo "当前运行的 Bot 容器："
docker ps | grep bot | head -1 || echo "  ❌ 无容器"
echo ""

REMOTE_SCRIPT

