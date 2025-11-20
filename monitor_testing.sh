#!/bin/bash
# 监控测试过程

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "📊 启动测试监控"
echo "===================================="
echo ""
echo "监控模式：实时监控所有服务日志"
echo "按 Ctrl+C 停止监控"
echo ""

# 在后台启动日志监控
ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

# 创建日志监控函数
monitor_logs() {
    echo "===================================="
    echo "开始监控日志（实时）"
    echo "===================================="
    echo ""
    
    # 监控所有服务的日志，实时显示错误
    docker compose -f docker-compose.production.yml logs -f --tail=0 2>&1 | while IFS= read -r line; do
        # 检查是否是错误日志
        if echo "$line" | grep -qiE "error|fatal|exception|failed|critical"; then
            # 高亮显示错误
            echo -e "\033[31m[ERROR] $line\033[0m"
        elif echo "$line" | grep -qiE "warning|warn"; then
            # 黄色显示警告
            echo -e "\033[33m[WARN]  $line\033[0m"
        elif echo "$line" | grep -qiE "info|starting|started|connected|success"; then
            # 绿色显示成功信息
            echo -e "\033[32m[INFO]  $line\033[0m"
        else
            # 普通日志
            echo "[LOG]   $line"
        fi
    done
}

# 在后台启动监控
monitor_logs &
MONITOR_PID=$!

echo "监控进程 PID: $MONITOR_PID"
echo ""

# 等待用户中断
trap "kill $MONITOR_PID 2>/dev/null; exit" INT TERM

# 保持脚本运行
wait $MONITOR_PID

REMOTE_SCRIPT

