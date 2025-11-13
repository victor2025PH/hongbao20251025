#!/bin/bash
# 数据库备份脚本
# 使用方式: ./deploy/scripts/backup.sh

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup-$TIMESTAMP.sql"

echo "🔄 开始数据库备份..."

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 检查是否使用 Docker Compose
if [ -f "docker-compose.production.yml" ]; then
    # Docker Compose 方式
    echo "📦 使用 Docker Compose 备份..."
    docker-compose -f docker-compose.production.yml exec -T db pg_dump -U ${POSTGRES_USER:-redpacket} ${POSTGRES_DB:-redpacket} > "$BACKUP_FILE"
else
    # 直接连接方式
    echo "📦 直接连接数据库备份..."
    pg_dump "$DATABASE_URL" > "$BACKUP_FILE"
fi

# 压缩备份文件
if command -v gzip &> /dev/null; then
    echo "📦 压缩备份文件..."
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"
fi

# 检查备份文件大小
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "✅ 备份完成: $BACKUP_FILE ($BACKUP_SIZE)"

# 清理旧备份（保留最近 7 天）
echo "🧹 清理旧备份（保留最近 7 天）..."
find "$BACKUP_DIR" -name "backup-*.sql*" -mtime +7 -delete

echo "✅ 备份脚本完成"

