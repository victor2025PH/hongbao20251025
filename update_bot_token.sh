#!/bin/bash
# 更新 Bot Token 并重新启动

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

NEW_TOKEN="8107181495:AAG0h0b6G4DfPAmI4L8PsXrB2qJZhgnC4cA"

echo ""
echo "===================================="
echo "🔄 更新 Bot Token 并重新启动"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << REMOTE_SCRIPT
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 备份当前配置"
echo "===================================="

if [ -f .env.production ]; then
    cp .env.production .env.production.bak.\$(date +%Y%m%d-%H%M%S)
    echo "✅ 已备份 .env.production"
else
    echo "⚠️  .env.production 文件不存在"
fi
echo ""

echo "===================================="
echo "2️⃣ 更新 Bot Token"
echo "===================================="

# 检查并更新各种可能的 Token 变量名
TOKEN_VARS=("TELEGRAM_BOT_TOKEN" "BOT_TOKEN" "TGBOT_TOKEN" "TG_BOT_TOKEN")

UPDATED=false

for VAR in "\${TOKEN_VARS[@]}"; do
    if grep -q "^${VAR}=" .env.production 2>/dev/null; then
        # 更新现有变量
        sed -i "s|^${VAR}=.*|${VAR}=${NEW_TOKEN}|g" .env.production
        echo "✅ 已更新 ${VAR}"
        UPDATED=true
        break
    fi
done

# 如果没有找到现有变量，添加新变量
if [ "\$UPDATED" = false ]; then
    echo "TELEGRAM_BOT_TOKEN=${NEW_TOKEN}" >> .env.production
    echo "✅ 已添加 TELEGRAM_BOT_TOKEN"
    UPDATED=true
fi

if [ "\$UPDATED" = true ]; then
    echo ""
    echo "验证更新："
    grep -E "^TELEGRAM_BOT_TOKEN=|^BOT_TOKEN=|^TGBOT_TOKEN=" .env.production | sed 's/=.*/=***/' | head -1
fi
echo ""

echo "===================================="
echo "3️⃣ 停止当前 Bot 服务"
echo "===================================="

echo "停止 Docker 容器中的 Bot..."
docker compose --env-file .env.production -f docker-compose.production.yml stop bot 2>/dev/null || true
docker compose --env-file .env.production -f docker-compose.production.yml rm -f bot 2>/dev/null || true

# 停止所有 python app.py 进程
echo "停止所有 python app.py 进程..."
PIDS=\$(ps aux | grep "python.*app\.py" | grep -v grep | awk '{print \$2}')
for PID in \$PIDS; do
    kill -TERM \$PID 2>/dev/null || kill -9 \$PID 2>/dev/null || true
done
sleep 3

# 强制停止剩余进程
PIDS=\$(ps aux | grep "python.*app\.py" | grep -v grep | awk '{print \$2}')
for PID in \$PIDS; do
    kill -9 \$PID 2>/dev/null || true
done

echo "✅ 所有 Bot 进程已停止"
echo ""

echo "===================================="
echo "4️⃣ 清理 Telegram Webhook"
echo "===================================="

echo "清理旧 Token 的 Webhook..."
curl -s "https://api.telegram.org/bot\${NEW_TOKEN}/deleteWebhook?drop_pending_updates=true" | head -3
echo ""

echo "等待 5 秒让 Telegram API 更新..."
sleep 5
echo "✅ 清理完成"
echo ""

echo "===================================="
echo "5️⃣ 重新启动 Bot 服务"
echo "===================================="

echo "使用新 Token 重新启动 Bot 服务..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d bot

echo ""
echo "等待 40 秒让 Bot 完全启动..."
sleep 40
echo ""

echo "===================================="
echo "6️⃣ 验证新 Token 和 Bot 状态"
echo "===================================="

echo "Bot 容器状态："
docker compose --env-file .env.production -f docker-compose.production.yml ps bot
echo ""

echo "Bot 日志（最后 30 行）："
docker compose -f docker-compose.production.yml logs bot --tail 30
echo ""

echo "===================================="
echo "7️⃣ 检查 Telegram 连接状态"
echo "===================================="

# 检查是否有 Telegram 冲突
if docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -q "TelegramConflictError"; then
    echo "⚠️  仍然存在 Telegram 冲突"
else
    echo "✅ 未发现 Telegram 冲突"
fi

# 检查 Bot 是否成功启动
if docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -qE "Start polling|Run polling|preheat ok"; then
    echo "✅ Bot 已成功启动并开始轮询"
    
    # 获取 Bot 信息验证 Token
    BOT_INFO=\$(curl -s "https://api.telegram.org/bot${NEW_TOKEN}/getMe" 2>/dev/null | grep -oE '"username":"[^"]+"|"first_name":"[^"]+"' | head -2)
    if [ -n "\$BOT_INFO" ]; then
        echo "✅ Token 验证成功，Bot 信息："
        echo "\$BOT_INFO" | sed 's/^/     /'
    else
        echo "⚠️  无法验证 Token，但 Bot 已启动"
    fi
fi
echo ""

echo "===================================="
echo "✅ Bot Token 更新完成"
echo "===================================="
echo ""

REMOTE_SCRIPT

