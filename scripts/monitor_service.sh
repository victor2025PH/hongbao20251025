#!/bin/bash
# systemd 服务监控脚本

SERVICE_NAME="redpacket.service"
LOG_FILE="/opt/redpacket/logs/monitor.log"
ALERT_EMAIL="admin@example.com"  # 可选：配置邮件告警

# 确保日志目录存在
mkdir -p "/opt/redpacket/logs"

# 检查服务状态
if ! systemctl is-active --quiet "${SERVICE_NAME}"; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Service ${SERVICE_NAME} is not running!" >> "${LOG_FILE}"
    
    # 尝试重启
    systemctl restart "${SERVICE_NAME}" 2>&1 >> "${LOG_FILE}" || true
    
    # 等待 10 秒后再次检查
    sleep 10
    if ! systemctl is-active --quiet "${SERVICE_NAME}"; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Service ${SERVICE_NAME} failed to restart!" >> "${LOG_FILE}"
        
        # 发送告警（需要配置邮件服务）
        # echo "Service ${SERVICE_NAME} is down!" | mail -s "Alert: Service Down" "${ALERT_EMAIL}"
    fi
fi

