#!/bin/bash
# 部署监控脚本
# 使用方法: bash deploy/scripts/monitor_deployment.sh

set -e

# 配置
DEPLOY_PATH="${DEPLOY_PATH:-/opt/redpacket}"
CHECK_INTERVAL=30  # 检查间隔（秒）
LOG_FILE="${DEPLOY_PATH}/logs/monitor.log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 健康检查函数
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=$3
    
    if curl -f -s "http://127.0.0.1:${port}${endpoint}" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 检查所有服务
check_all_services() {
    local failed=0
    
    if ! check_service "Web Admin" 8000 "/healthz"; then
        log "❌ Web Admin (8000) 健康检查失败"
        failed=1
    fi
    
    if ! check_service "MiniApp API" 8080 "/healthz"; then
        log "❌ MiniApp API (8080) 健康检查失败"
        failed=1
    fi
    
    if ! check_service "Frontend" 3001 ""; then
        log "❌ Frontend (3001) 健康检查失败"
        failed=1
    fi
    
    return $failed
}

# 发送通知（可选）
send_notification() {
    local message=$1
    # 在这里添加通知逻辑，例如：
    # - 发送邮件
    # - 发送企业微信
    # - 发送 Slack 消息
    log "通知: $message"
}

# 重启服务
restart_services() {
    log "🔄 尝试重启服务..."
    cd "$DEPLOY_PATH" || return 1
    
    docker compose -f docker-compose.production.yml restart || {
        log "⚠️  重启失败，尝试停止并重新启动..."
        docker compose -f docker-compose.production.yml down --timeout 30
        docker compose --env-file .env.production \
            -f docker-compose.production.yml \
            up -d
    }
    
    sleep 60  # 等待服务启动
    
    if check_all_services; then
        log "✅ 服务重启成功"
        send_notification "服务已自动恢复"
        return 0
    else
        log "❌ 服务重启后仍然异常"
        send_notification "服务重启失败，需要人工干预"
        return 1
    fi
}

# 主循环
log "🚀 开始监控部署..."
log "监控间隔: ${CHECK_INTERVAL}秒"
log "日志文件: $LOG_FILE"
echo ""

consecutive_failures=0
MAX_CONSECUTIVE_FAILURES=3

while true; do
    if check_all_services; then
        if [ $consecutive_failures -gt 0 ]; then
            log "✅ 所有服务恢复正常"
            consecutive_failures=0
        fi
    else
        consecutive_failures=$((consecutive_failures + 1))
        log "⚠️  服务异常 (连续失败 $consecutive_failures 次)"
        
        if [ $consecutive_failures -ge $MAX_CONSECUTIVE_FAILURES ]; then
            log "❌ 连续失败 $MAX_CONSECUTIVE_FAILURES 次，尝试重启服务..."
            if restart_services; then
                consecutive_failures=0
            else
                consecutive_failures=$MAX_CONSECUTIVE_FAILURES
            fi
        fi
    fi
    
    # 显示服务状态
    if [ $((RANDOM % 10)) -eq 0 ]; then  # 每 10 次显示一次详细状态
        echo ""
        log "📊 服务状态:"
        cd "$DEPLOY_PATH" && docker compose -f docker-compose.production.yml ps | tee -a "$LOG_FILE"
        echo ""
    fi
    
    sleep "$CHECK_INTERVAL"
done

