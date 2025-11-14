#!/bin/bash
# 数据库备份脚本（用于 cron）

set -e

PROJECT_DIR="/opt/redpacket"
BACKUP_DIR="/opt/redpacket/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=7

# 确保备份目录存在
mkdir -p "${BACKUP_DIR}"

# 从环境变量读取数据库配置
if [ -f "${PROJECT_DIR}/.env.production" ]; then
    source "${PROJECT_DIR}/.env.production"
fi

# 执行备份（Docker Compose 环境）
if docker ps | grep -q redpacket_db; then
    docker exec redpacket_db pg_dump -U redpacket redpacket | gzip > "${BACKUP_FILE}"
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database container not running, skipping backup" >> "${PROJECT_DIR}/logs/backup.log"
    exit 1
fi

# 清理旧备份（保留 7 天）
find "${BACKUP_DIR}" -type f -name "db_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

# 记录日志
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database backup completed: ${BACKUP_FILE}" >> "${PROJECT_DIR}/logs/backup.log"

