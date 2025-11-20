#!/bin/bash
# 修复 Telegram 冲突

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔧 修复 Telegram 冲突"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 检查所有 Bot 进程"
echo "===================================="

echo "检查是否有其他 Bot 实例运行..."
echo ""

# 检查所有容器
echo "所有容器："
docker ps -a | grep -E "bot|redpacket.*app\.py|python.*app\.py" | grep -v "redpacket_bot" || echo "  未发现其他 Bot 容器"
echo ""

# 检查进程
echo "检查系统进程："
ps aux | grep -E "python.*app\.py|bot" | grep -v grep || echo "  未发现其他 Bot 进程"
echo ""

echo "===================================="
echo "2️⃣ 检查当前 Bot 服务"
echo "===================================="

docker compose -f docker-compose.production.yml ps bot
echo ""

echo "Bot 日志（最近 5 行）："
docker compose -f docker-compose.production.yml logs bot --tail 5
echo ""

echo "===================================="
echo "3️⃣ 尝试修复 Telegram 冲突"
echo "===================================="

echo "方案 1: 停止并重启 Bot 服务..."
docker compose --env-file .env.production -f docker-compose.production.yml stop bot
sleep 5
docker compose --env-file .env.production -f docker-compose.production.yml rm -f bot
sleep 5
docker compose --env-file .env.production -f docker-compose.production.yml up -d bot

echo ""
echo "等待 20 秒让 Bot 完全启动..."
sleep 20

echo ""
echo "检查 Bot 状态："
docker compose -f docker-compose.production.yml ps bot
echo ""

echo "检查 Telegram 冲突是否解决："
if docker compose -f docker-compose.production.yml logs bot --tail 10 2>/dev/null | grep -q "TelegramConflictError"; then
    echo "⚠️  仍然存在 Telegram 冲突"
    echo "   可能原因："
    echo "   1. 有其他 Bot 实例在其他服务器或本地运行"
    echo "   2. 需要等待 Telegram API 更新"
    echo ""
    echo "   建议："
    echo "   1. 检查是否有其他服务器或本地运行 Bot"
    echo "   2. 等待 1-2 分钟后再次检查"
    echo "   3. 如果仍然冲突，可能需要使用 Webhook 模式替代长轮询"
else
    echo "✅ Telegram 冲突已解决"
fi
echo ""

REMOTE_SCRIPT

