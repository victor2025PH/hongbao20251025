#!/bin/bash
# 修复 Bot Token 并检查 API 服务

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔧 修复 Bot Token 并检查 API 服务"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 检查当前 Bot Token 配置"
echo "===================================="

echo "检查 .env.production 中的 Token:"
grep -E "^TELEGRAM_BOT_TOKEN=|^BOT_TOKEN=" .env.production | head -1 | sed 's/=.*/=***/'
echo ""

# 验证正确的 Token
CORRECT_TOKEN="8107181495:AAG0h0b6G4DfPAmI4L8PsXrB2qJZhgnC4cA"
CURRENT_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" .env.production | cut -d'=' -f2 | tr -d '[:space:]' || grep "^BOT_TOKEN=" .env.production | cut -d'=' -f2 | tr -d '[:space:]' || echo "")

if [ "$CURRENT_TOKEN" != "$CORRECT_TOKEN" ]; then
    echo "⚠️  Token 不匹配，更新为正确 Token..."
    # 删除旧的 Token 配置
    sed -i '/^TELEGRAM_BOT_TOKEN=/d' .env.production
    sed -i '/^BOT_TOKEN=/d' .env.production
    # 添加正确的 Token
    echo "TELEGRAM_BOT_TOKEN=$CORRECT_TOKEN" >> .env.production
    echo "✅ Token 已更新"
else
    echo "✅ Token 配置正确"
fi
echo ""

echo "===================================="
echo "2️⃣ 验证 Token"
echo "===================================="

NEW_TOKEN=$(grep "^TELEGRAM_BOT_TOKEN=" .env.production | cut -d'=' -f2 | tr -d '[:space:]')
if [ -n "$NEW_TOKEN" ]; then
    BOT_INFO=$(curl -s "https://api.telegram.org/bot${NEW_TOKEN}/getMe" 2>/dev/null)
    if echo "$BOT_INFO" | grep -q "\"ok\":true"; then
        echo "✅ Token 有效"
        echo "$BOT_INFO" | grep -oE '"username":"[^"]+"|"first_name":"[^"]+"|"id":[0-9]+' | head -3 | sed 's/^/  /'
    else
        echo "❌ Token 无效"
    fi
fi
echo ""

echo "===================================="
echo "3️⃣ 重启 Bot 服务以应用新 Token"
echo "===================================="

echo "停止并删除 Bot 容器..."
docker compose --env-file .env.production -f docker-compose.production.yml stop bot
docker compose --env-file .env.production -f docker-compose.production.yml rm -f bot

# 停止所有 python app.py 进程
PIDS=$(ps aux | grep "python.*app\.py" | grep -v grep | awk '{print $2}')
for PID in $PIDS; do
    kill -TERM $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
done
sleep 3

echo "重新启动 Bot 服务..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d bot

echo ""
echo "等待 30 秒让 Bot 完全启动..."
sleep 30
echo ""

echo "===================================="
echo "4️⃣ 验证 Bot 使用新 Token"
echo "===================================="

echo "检查 Bot 日志中的 Bot 信息："
BOT_INFO_LOG=$(docker compose -f docker-compose.production.yml logs bot --tail 30 2>/dev/null | grep -iE "preheat ok|bot.*@|username" | tail -3 || echo "")
if [ -n "$BOT_INFO_LOG" ]; then
    echo "$BOT_INFO_LOG" | sed 's/^/  /'
    
    # 检查是否是新的 Bot
    if echo "$BOT_INFO_LOG" | grep -q "zhuce_2025_bot"; then
        echo "✅ Bot 正在使用新 Token (@zhuce_2025_bot)"
    else
        echo "⚠️  Bot 可能仍在使用旧 Token"
    fi
else
    echo "⚠️  无法获取 Bot 信息"
fi
echo ""

echo "===================================="
echo "5️⃣ 检查 API 服务状态"
echo "===================================="

echo "检查所有服务状态："
docker compose --env-file .env.production -f docker-compose.production.yml ps
echo ""

echo "检查 Web Admin 服务："
WEB_STATUS=$(docker compose --env-file .env.production -f docker-compose.production.yml ps web_admin | tail -1 | awk '{print $(NF-1), $NF}')
echo "状态: $WEB_STATUS"

if echo "$WEB_STATUS" | grep -qE "Up|running"; then
    echo "✅ Web Admin 服务运行中"
    
    # 测试健康检查
    echo "测试健康检查..."
    sleep 5
    if curl -f -s http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
        echo "✅ Web Admin API 健康检查通过"
        curl -s http://127.0.0.1:8000/healthz | head -1
    else
        echo "⚠️  Web Admin API 健康检查失败"
        echo "查看日志："
        docker compose -f docker-compose.production.yml logs web_admin --tail 10 | tail -5
    fi
else
    echo "❌ Web Admin 服务未运行，正在启动..."
    docker compose --env-file .env.production -f docker-compose.production.yml up -d web_admin
    sleep 10
fi
echo ""

echo "检查 MiniApp API 服务："
MINI_STATUS=$(docker compose --env-file .env.production -f docker-compose.production.yml ps miniapp_api | tail -1 | awk '{print $(NF-1), $NF}')
echo "状态: $MINI_STATUS"

if echo "$MINI_STATUS" | grep -qE "Up|running"; then
    echo "✅ MiniApp API 服务运行中"
    
    # 测试健康检查
    echo "测试健康检查..."
    sleep 5
    if curl -f -s http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
        echo "✅ MiniApp API 健康检查通过"
        curl -s http://127.0.0.1:8080/healthz | head -1
    else
        echo "⚠️  MiniApp API 健康检查失败"
        echo "查看日志："
        docker compose -f docker-compose.production.yml logs miniapp_api --tail 10 | tail -5
    fi
else
    echo "❌ MiniApp API 服务未运行，正在启动..."
    docker compose --env-file .env.production -f docker-compose.production.yml up -d miniapp_api
    sleep 10
fi
echo ""

echo "===================================="
echo "6️⃣ 最终验证"
echo "===================================="

echo "检查 Bot 是否接收到消息（发送 /start 测试）:"
if docker compose -f docker-compose.production.yml logs bot --tail 50 2>/dev/null | grep -qiE "/start|update.*received|handling.*update"; then
    echo "✅ Bot 已开始处理消息"
    docker compose -f docker-compose.production.yml logs bot --tail 20 2>/dev/null | grep -iE "/start|update.*received|handling.*update" | tail -3 | sed 's/^/  /'
else
    echo "ℹ️  Bot 等待接收消息..."
    echo "   请向 Bot 发送 /start 命令测试"
fi
echo ""

echo "API 访问地址："
echo "  Web Admin API:"
echo "    健康检查: http://127.0.0.1:8000/healthz"
echo "    API 文档: http://127.0.0.1:8000/docs"
echo ""
echo "  MiniApp API:"
echo "    健康检查: http://127.0.0.1:8080/healthz"
echo "    API 文档: http://127.0.0.1:8080/docs"
echo ""

REMOTE_SCRIPT

