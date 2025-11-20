#!/bin/bash
# 修复 Bot Token 环境变量

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔧 修复 Bot Token 环境变量"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 检查环境变量配置"
echo "===================================="

NEW_TOKEN="8107181495:AAG0h0b6G4DfPAmI4L8PsXrB2qJZhgnC4cA"

echo "检查 .env.production 中的 Token 配置..."
echo ""

# 检查 BOT_TOKEN（代码中使用的变量名）
BOT_TOKEN=$(grep "^BOT_TOKEN=" .env.production | cut -d'=' -f2 | tr -d '[:space:]' || echo "")
TELEGRAM_BOT_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" .env.production | cut -d'=' -f2 | tr -d '[:space:]' || echo "")

echo "当前配置："
echo "  BOT_TOKEN: ${BOT_TOKEN:+已设置（长度: ${#BOT_TOKEN}）}"
echo "  TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:+已设置（长度: ${#TELEGRAM_BOT_TOKEN}）}"
echo ""

# 确保使用正确的变量名（代码使用 BOT_TOKEN）
if [ "$BOT_TOKEN" != "$NEW_TOKEN" ]; then
    echo "⚠️  BOT_TOKEN 配置不正确，正在更新..."
    
    # 删除旧的 Token 配置
    sed -i '/^BOT_TOKEN=/d' .env.production
    sed -i '/^TELEGRAM_BOT_TOKEN=/d' .env.production
    
    # 添加正确的 Token（使用 BOT_TOKEN）
    echo "BOT_TOKEN=$NEW_TOKEN" >> .env.production
    echo "✅ BOT_TOKEN 已更新"
else
    echo "✅ BOT_TOKEN 配置正确"
fi

# 同时设置 TELEGRAM_BOT_TOKEN（如果代码中也会使用）
if ! grep -q "^TELEGRAM_BOT_TOKEN=" .env.production; then
    echo "TELEGRAM_BOT_TOKEN=$NEW_TOKEN" >> .env.production
    echo "✅ TELEGRAM_BOT_TOKEN 已添加"
fi

echo ""
echo "验证配置："
grep -E "^BOT_TOKEN=|^TELEGRAM_BOT_TOKEN=" .env.production | sed 's/=.*/=***/' | head -2
echo ""

echo "===================================="
echo "2️⃣ 验证 Token"
echo "===================================="

if curl -s "https://api.telegram.org/bot${NEW_TOKEN}/getMe" | grep -q "\"ok\":true"; then
    echo "✅ Token 有效"
    curl -s "https://api.telegram.org/bot${NEW_TOKEN}/getMe" | grep -oE '"username":"[^"]+"|"first_name":"[^"]+"|"id":[0-9]+' | head -3 | sed 's/^/  /'
else
    echo "❌ Token 无效"
fi
echo ""

echo "===================================="
echo "3️⃣ 重新构建并重启 Bot 服务"
echo "===================================="

echo "停止 Bot 服务..."
docker compose --env-file .env.production -f docker-compose.production.yml stop bot
docker compose --env-file .env.production -f docker-compose.production.yml rm -f bot

# 停止所有 python app.py 进程
PIDS=$(ps aux | grep "python.*app\.py" | grep -v grep | awk '{print $2}')
for PID in $PIDS; do
    kill -TERM $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
done
sleep 3

echo "重新启动 Bot 服务（使用新环境变量）..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d bot

echo ""
echo "等待 40 秒让 Bot 完全启动..."
sleep 40
echo ""

echo "===================================="
echo "4️⃣ 验证 Bot 使用新 Token"
echo "===================================="

echo "检查 Bot 容器中的环境变量："
docker compose --env-file .env.production -f docker-compose.production.yml exec bot env | grep -E "^BOT_TOKEN=|^TELEGRAM_BOT_TOKEN=" 2>/dev/null | sed 's/=.*/=***/' || echo "无法获取（容器可能未运行）"
echo ""

echo "检查 Bot 日志中的 Bot 信息："
BOT_INFO_LOG=$(docker compose -f docker-compose.production.yml logs bot --tail 30 2>/dev/null | grep -iE "preheat ok|bot.*@" | tail -2 || echo "")
if [ -n "$BOT_INFO_LOG" ]; then
    echo "$BOT_INFO_LOG" | sed 's/^/  /'
    
    # 检查是否是新的 Bot
    if echo "$BOT_INFO_LOG" | grep -q "zhuce_2025_bot"; then
        echo "✅ Bot 正在使用新 Token (@zhuce_2025_bot)"
    else
        echo "⚠️  Bot 仍在使用旧 Token，需要重新构建镜像"
    fi
else
    echo "⚠️  无法获取 Bot 信息"
fi
echo ""

echo "===================================="
echo "5️⃣ 检查 API 服务状态"
echo "===================================="

echo ""
echo "Web Admin API:"
if curl -f -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
    echo "✅ 健康检查通过"
    curl -s http://127.0.0.1:8000/healthz | head -1
else
    echo "❌ 健康检查失败"
fi
echo ""

echo "MiniApp API:"
if curl -f -s http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
    echo "✅ 健康检查通过"
    curl -s http://127.0.0.1:8080/healthz | head -1
else
    echo "❌ 健康检查失败"
fi
echo ""

echo "===================================="
echo "✅ 修复完成"
echo "===================================="
echo ""

REMOTE_SCRIPT

