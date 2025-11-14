#!/bin/bash
# 健康检查脚本（用于 cron）

set -e

PROJECT_DIR="/opt/redpacket"
LOG_FILE="${PROJECT_DIR}/logs/healthcheck.log"
BACKEND_URL="http://localhost:8000/healthz"
FRONTEND_URL="http://localhost:3001"

# 确保日志目录存在
mkdir -p "${PROJECT_DIR}/logs"

# 检查后端健康
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BACKEND_URL}" || echo "000")

if [ "${BACKEND_STATUS}" != "200" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Backend health check failed (HTTP ${BACKEND_STATUS}), restarting..." >> "${LOG_FILE}"
    cd "${PROJECT_DIR}"
    docker-compose -f docker-compose.production.yml restart backend 2>&1 >> "${LOG_FILE}" || true
    # 或者使用 systemd: sudo systemctl restart redpacket-backend.service
fi

# 检查前端健康（可选）
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}" || echo "000")

if [ "${FRONTEND_STATUS}" != "200" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Frontend health check failed (HTTP ${FRONTEND_STATUS}), restarting..." >> "${LOG_FILE}"
    cd "${PROJECT_DIR}"
    docker-compose -f docker-compose.production.yml restart frontend 2>&1 >> "${LOG_FILE}" || true
    # 或者使用 systemd: sudo systemctl restart redpacket-frontend.service
fi

