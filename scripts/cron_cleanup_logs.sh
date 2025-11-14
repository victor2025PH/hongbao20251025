#!/bin/bash
# 日志清理脚本（用于 cron）

set -e

PROJECT_DIR="/opt/redpacket"
LOG_DIR="${PROJECT_DIR}/logs"
RETENTION_DAYS=30

# 确保日志目录存在
mkdir -p "${LOG_DIR}"

# 清理超过 30 天的日志文件
find "${LOG_DIR}" -type f -name "*.log" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

# 清理 Docker 日志（如果使用 Docker Compose）
docker system prune -f --volumes 2>/dev/null || true

# 记录清理日志
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Log cleanup completed" >> "${LOG_DIR}/cleanup.log"

