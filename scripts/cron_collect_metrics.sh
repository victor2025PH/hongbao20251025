#!/bin/bash
# 监控指标收集脚本（用于 cron）

set -e

PROJECT_DIR="/opt/redpacket"
METRICS_DIR="${PROJECT_DIR}/metrics"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 确保目录存在
mkdir -p "${METRICS_DIR}"

# 收集系统资源使用情况
{
    echo "=== System Metrics at $(date) ==="
    echo "CPU Usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' || echo "N/A"
    echo "Memory Usage:"
    free -h || echo "N/A"
    echo "Disk Usage:"
    df -h || echo "N/A"
    echo "Docker Container Status:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.CPU}}\t{{.MemUsage}}" || echo "N/A"
} > "${METRICS_DIR}/system_${TIMESTAMP}.txt" 2>&1

# 收集应用指标（如果 Prometheus 可用）
# curl -s http://localhost:8000/metrics > "${METRICS_DIR}/app_${TIMESTAMP}.prom" 2>/dev/null || true

# 清理旧指标文件（保留 7 天）
find "${METRICS_DIR}" -type f -mtime +7 -delete 2>/dev/null || true

