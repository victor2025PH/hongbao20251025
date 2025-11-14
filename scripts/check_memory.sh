#!/bin/bash
# 内存使用检查脚本

set -e

PROJECT_DIR="/opt/redpacket"
LOG_FILE="${PROJECT_DIR}/logs/memory_check.log"
THRESHOLD=90  # 内存使用率阈值（%）

# 确保日志目录存在
mkdir -p "${PROJECT_DIR}/logs"

# 获取内存使用率
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')

if [ "${MEMORY_USAGE}" -gt "${THRESHOLD}" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Memory usage is ${MEMORY_USAGE}% (threshold: ${THRESHOLD}%)" >> "${LOG_FILE}"
    
    # 重启服务（谨慎使用，取消注释以启用）
    # systemctl restart redpacket.service
    
    # 或者清理 Docker 缓存
    docker system prune -f 2>/dev/null || true
fi

