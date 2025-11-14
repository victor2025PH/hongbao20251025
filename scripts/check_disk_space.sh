#!/bin/bash
# 磁盘空间检查脚本

set -e

PROJECT_DIR="/opt/redpacket"
LOG_FILE="${PROJECT_DIR}/logs/disk_check.log"
THRESHOLD=80  # 磁盘使用率阈值（%）

# 确保日志目录存在
mkdir -p "${PROJECT_DIR}/logs"

# 检查根分区使用率
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "${USAGE}" -gt "${THRESHOLD}" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Disk usage is ${USAGE}% (threshold: ${THRESHOLD}%)" >> "${LOG_FILE}"
    
    # 清理 Docker 未使用的资源
    docker system prune -f 2>/dev/null || true
    
    # 清理旧日志
    find "${PROJECT_DIR}/logs" -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # 清理旧备份
    if [ -d "${PROJECT_DIR}/backups" ]; then
        find "${PROJECT_DIR}/backups" -type f -name "*.sql.gz" -mtime +7 -delete 2>/dev/null || true
    fi
fi

