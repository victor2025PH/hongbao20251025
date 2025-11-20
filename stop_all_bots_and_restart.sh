#!/bin/bash
# 停止所有 Bot 进程并重新启动

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🛑 停止所有 Bot 进程并重新启动"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 检查所有 Bot 相关进程"
echo "===================================="

echo "检查所有 python app.py 进程："
ps aux | grep "python.*app\.py" | grep -v grep || echo "  未发现进程"
echo ""

echo "检查所有容器中的 Bot："
docker ps -a | grep -E "bot|app\.py" || echo "  未发现其他 Bot 容器"
echo ""

echo "===================================="
echo "2️⃣ 停止所有 Bot 进程"
echo "===================================="

# 停止 Docker 容器中的 Bot
echo "停止 Docker 容器中的 Bot 服务..."
docker compose --env-file .env.production -f docker-compose.production.yml stop bot 2>/dev/null || true
docker compose --env-file .env.production -f docker-compose.production.yml rm -f bot 2>/dev/null || true
echo "✅ Docker Bot 容器已停止"
echo ""

# 查找并停止所有 python app.py 进程
echo "查找并停止所有 python app.py 进程..."
PIDS=$(ps aux | grep "python.*app\.py" | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
    echo "发现以下进程："
    ps aux | grep "python.*app\.py" | grep -v grep
    echo ""
    echo "正在停止这些进程..."
    for PID in $PIDS; do
        echo "  停止进程 $PID..."
        kill -TERM $PID 2>/dev/null || kill -9 $PID 2>/dev/null || true
    done
    sleep 2
    
    # 检查是否还有进程
    REMAINING=$(ps aux | grep "python.*app\.py" | grep -v grep | awk '{print $2}')
    if [ -n "$REMAINING" ]; then
        echo "  强制停止剩余进程..."
        for PID in $REMAINING; do
            kill -9 $PID 2>/dev/null || true
        done
    fi
    
    sleep 2
    
    # 再次检查
    FINAL_CHECK=$(ps aux | grep "python.*app\.py" | grep -v grep || echo "")
    if [ -z "$FINAL_CHECK" ]; then
        echo "✅ 所有 Bot 进程已停止"
    else
        echo "⚠️  仍有进程运行："
        echo "$FINAL_CHECK"
    fi
else
    echo "✅ 未发现 Bot 进程"
fi
echo ""

echo "===================================="
echo "3️⃣ 清理 Docker 资源"
echo "===================================="

# 清理所有与 Bot 相关的容器
echo "清理所有 Bot 相关容器..."
docker ps -a | grep -E "bot|redpacket.*backend" | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true
echo "✅ 清理完成"
echo ""

echo "===================================="
echo "4️⃣ 等待 Telegram API 更新"
echo "===================================="

echo "等待 10 秒让 Telegram API 更新..."
sleep 10
echo "✅ 等待完成"
echo ""

echo "===================================="
echo "5️⃣ 重新启动 Bot 服务"
echo "===================================="

echo "重新启动 Bot 服务..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d bot

echo ""
echo "等待 30 秒让 Bot 完全启动..."
sleep 30
echo ""

echo "===================================="
echo "6️⃣ 检查 Bot 状态"
echo "===================================="

echo "Bot 容器状态："
docker compose --env-file .env.production -f docker-compose.production.yml ps bot
echo ""

echo "Bot 日志（最后 20 行）："
docker compose -f docker-compose.production.yml logs bot --tail 20
echo ""

echo "检查 Telegram 冲突："
if docker compose -f docker-compose.production.yml logs bot --tail 30 2>/dev/null | grep -q "TelegramConflictError"; then
    echo "⚠️  仍然存在 Telegram 冲突"
    echo "   可能原因："
    echo "   1. 需要等待更长时间让 Telegram API 更新"
    echo "   2. 有其他服务器在运行 Bot"
    echo ""
    echo "   建议等待 1-2 分钟后再检查"
else
    echo "✅ Telegram 冲突已解决！"
    echo ""
    
    # 检查 Bot 是否成功启动
    if docker compose -f docker-compose.production.yml logs bot --tail 10 2>/dev/null | grep -qE "Start polling|Run polling|preheat ok"; then
        echo "✅ Bot 已成功启动并开始轮询"
    fi
fi
echo ""

echo "===================================="
echo "7️⃣ 验证所有进程"
echo "===================================="

echo "当前运行的 Bot 进程："
ps aux | grep "python.*app\.py" | grep -v grep || echo "  ✅ 无额外进程"
echo ""

echo "当前运行的 Bot 容器："
docker ps | grep bot || echo "  ✅ 无其他容器"
echo ""

echo "===================================="
echo "✅ 重启完成"
echo "===================================="
echo ""

REMOTE_SCRIPT

