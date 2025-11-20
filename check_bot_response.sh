#!/bin/bash
# 检查 Bot 无响应原因并修复

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔍 检查 Bot 无响应原因"
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
echo "2️⃣ Bot 日志（最后 50 行）"
echo "===================================="

docker compose -f docker-compose.production.yml logs bot --tail 50
echo ""

echo "===================================="
echo "3️⃣ 检查错误"
echo "===================================="

ERRORS=$(docker compose -f docker-compose.production.yml logs bot --tail 100 2>/dev/null | grep -iE "error|fatal|exception|failed" | grep -v "TelegramConflictError" | tail -10 || echo "")

if [ -n "$ERRORS" ]; then
    echo "发现错误："
    echo "$ERRORS" | sed 's/^/  /'
else
    echo "✅ 未发现严重错误"
fi
echo ""

echo "===================================="
echo "4️⃣ 检查 Bot 是否接收到消息"
echo "===================================="

# 检查是否有处理消息的日志
if docker compose -f docker-compose.production.yml logs bot --tail 100 2>/dev/null | grep -qiE "update.*received|handling.*update|message.*received|/start"; then
    echo "✅ Bot 已接收到消息"
    docker compose -f docker-compose.production.yml logs bot --tail 100 2>/dev/null | grep -iE "update.*received|handling.*update|message.*received|/start" | tail -5 | sed 's/^/  /'
else
    echo "⚠️  Bot 未接收到消息"
    echo "   可能原因："
    echo "   1. Bot 未成功启动轮询"
    echo "   2. Telegram API 连接问题"
    echo "   3. Bot Token 不正确"
fi
echo ""

echo "===================================="
echo "5️⃣ 检查 Bot 配置"
echo "===================================="

# 检查环境变量
echo "检查 Bot Token 配置..."
BOT_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" .env.production | cut -d'=' -f2 | tr -d '[:space:]' || grep "^BOT_TOKEN=" .env.production | cut -d'=' -f2 | tr -d '[:space:]' || echo "")
if [ -n "$BOT_TOKEN" ]; then
    echo "✅ Bot Token 已配置（长度: ${#BOT_TOKEN}）"
    
    # 验证 Token 是否有效
    BOT_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe" 2>/dev/null)
    if echo "$BOT_INFO" | grep -q "\"ok\":true"; then
        echo "✅ Bot Token 有效"
        echo "$BOT_INFO" | grep -oE '"username":"[^"]+"|"first_name":"[^"]+"' | head -2 | sed 's/^/  /'
    else
        echo "❌ Bot Token 无效"
        echo "$BOT_INFO" | head -3
    fi
else
    echo "❌ Bot Token 未配置"
fi
echo ""

echo "===================================="
echo "6️⃣ 修复建议"
echo "===================================="

# 检查 Bot 是否在运行
BOT_RUNNING=$(docker compose -f docker-compose.production.yml ps bot | grep -c "Up\|running" || echo "0")

if [ "$BOT_RUNNING" -eq 0 ]; then
    echo "❌ Bot 服务未运行"
    echo "   修复：重启 Bot 服务"
    docker compose --env-file .env.production -f docker-compose.production.yml restart bot
    sleep 10
elif docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -q "TelegramConflictError"; then
    echo "⚠️  Telegram 冲突"
    echo "   修复：重启 Bot 服务"
    docker compose --env-file .env.production -f docker-compose.production.yml restart bot
    sleep 10
elif ! docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -q "Run polling"; then
    echo "⚠️  Bot 未启动轮询"
    echo "   修复：重启 Bot 服务"
    docker compose --env-file .env.production -f docker-compose.production.yml restart bot
    sleep 10
fi
echo ""

echo "===================================="
echo "7️⃣ 验证修复"
echo "===================================="

echo "等待 20 秒让 Bot 完全启动..."
sleep 20

echo "检查 Bot 状态："
docker compose -f docker-compose.production.yml logs bot --tail 20
echo ""

REMOTE_SCRIPT

