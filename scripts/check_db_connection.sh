#!/bin/bash
# 数据库连接检查脚本

set -e

PROJECT_DIR="/opt/redpacket"
LOG_FILE="${PROJECT_DIR}/logs/db_check.log"

# 确保日志目录存在
mkdir -p "${PROJECT_DIR}/logs"

# 检查数据库连接（Docker Compose 环境）
if docker ps | grep -q redpacket_db; then
    if docker exec redpacket_db pg_isready -U redpacket > /dev/null 2>&1; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database connection OK" >> "${LOG_FILE}"
    else
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database connection FAILED!" >> "${LOG_FILE}"
        
        # 尝试重启数据库容器
        cd "${PROJECT_DIR}"
        docker-compose -f docker-compose.production.yml restart db 2>&1 >> "${LOG_FILE}" || true
        
        # 等待 10 秒后再次检查
        sleep 10
        if ! docker exec redpacket_db pg_isready -U redpacket > /dev/null 2>&1; then
            echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database restart FAILED!" >> "${LOG_FILE}"
            # 发送告警（可以集成邮件或其他通知方式）
        fi
    fi
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database container not running!" >> "${LOG_FILE}"
fi

