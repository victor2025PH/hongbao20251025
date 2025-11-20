# Linux 系统服务与定时任务配置指南

> **适用于**: Ubuntu 24.04 / Debian 12+  
> **目标**: 将红包系统配置为系统服务，实现自动启动、运行和监控

---

## 📋 目录

1. [系统服务配置（systemd）](#系统服务配置systemd)
2. [定时任务配置（cron）](#定时任务配置cron)
3. [监控与告警](#监控与告警)
4. [异常处理方案](#异常处理方案)
5. [权限设置](#权限设置)

---

## 🔧 系统服务配置（systemd）

### **方案 1: Docker Compose 服务（推荐）**

将整个 Docker Compose 栈作为系统服务，实现自动启动和重启。

#### 1.1 创建 systemd 服务文件

```bash
sudo nano /etc/systemd/system/redpacket.service
```

**服务文件内容**:

```ini
[Unit]
Description=Red Packet System (Docker Compose)
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/redpacket
ExecStart=/usr/bin/docker-compose -f /opt/redpacket/docker-compose.production.yml up -d
ExecStop=/usr/bin/docker-compose -f /opt/redpacket/docker-compose.production.yml down
ExecReload=/usr/bin/docker-compose -f /opt/redpacket/docker-compose.production.yml restart
TimeoutStartSec=0
Restart=on-failure
RestartSec=10

# 环境变量（可选，如果 docker-compose.yml 中未指定）
Environment="COMPOSE_PROJECT_NAME=redpacket"
Environment="TZ=Asia/Manila"

# 日志配置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=redpacket

[Install]
WantedBy=multi-user.target
```

#### 1.2 启用并启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable redpacket.service

# 启动服务
sudo systemctl start redpacket.service

# 查看服务状态
sudo systemctl status redpacket.service

# 查看日志
sudo journalctl -u redpacket.service -f
```

#### 1.3 服务管理命令

```bash
# 启动
sudo systemctl start redpacket.service

# 停止
sudo systemctl stop redpacket.service

# 重启
sudo systemctl restart redpacket.service

# 重新加载（不中断服务）
sudo systemctl reload redpacket.service

# 查看状态
sudo systemctl status redpacket.service

# 查看日志（最近 100 行）
sudo journalctl -u redpacket.service -n 100

# 查看日志（实时）
sudo journalctl -u redpacket.service -f

# 禁用开机自启
sudo systemctl disable redpacket.service
```

---

### **方案 2: 独立服务（非 Docker）**

如果使用 PM2 或直接运行 Python/Node.js 进程。

#### 2.1 Python 后端服务（Uvicorn）

```bash
sudo nano /etc/systemd/system/redpacket-backend.service
```

**服务文件内容**:

```ini
[Unit]
Description=Red Packet System Backend (FastAPI)
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/redpacket
Environment="PATH=/opt/redpacket/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/opt/redpacket/.venv/bin/uvicorn web_admin.main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=redpacket-backend

# 资源限制（可选）
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

#### 2.2 Next.js 前端服务（PM2）

```bash
sudo nano /etc/systemd/system/redpacket-frontend.service
```

**服务文件内容**:

```ini
[Unit]
Description=Red Packet System Frontend (Next.js)
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/redpacket/frontend-next
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/pm2 start npm --name "redpacket-frontend" -- start
ExecReload=/usr/bin/pm2 reload redpacket-frontend
ExecStop=/usr/bin/pm2 stop redpacket-frontend
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=redpacket-frontend

[Install]
WantedBy=multi-user.target
```

**启用服务**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable redpacket-backend.service
sudo systemctl enable redpacket-frontend.service
sudo systemctl start redpacket-backend.service
sudo systemctl start redpacket-frontend.service
```

---

## ⏰ 定时任务配置（cron）

### **任务 1: 数据库备份**

**创建备份脚本**:
```bash
nano /opt/redpacket/scripts/cron_backup_db.sh
```

**脚本内容**:
```bash
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
source "${PROJECT_DIR}/.env.production"

# 执行备份（Docker Compose 环境）
docker exec redpacket_db pg_dump -U redpacket redpacket | gzip > "${BACKUP_FILE}"

# 清理旧备份（保留 7 天）
find "${BACKUP_DIR}" -type f -name "db_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

# 记录日志
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database backup completed: ${BACKUP_FILE}" >> "${PROJECT_DIR}/logs/backup.log"
```

**设置执行权限**:
```bash
chmod +x /opt/redpacket/scripts/cron_backup_db.sh
```

**添加到 crontab**:
```bash
crontab -e
```

**添加以下行**（每天凌晨 2 点备份）:
```
0 2 * * * /opt/redpacket/scripts/cron_backup_db.sh >> /opt/redpacket/logs/cron_backup.log 2>&1
```

---

### **任务 2: 健康检查与自动重启**

**创建健康检查脚本**:
```bash
nano /opt/redpacket/scripts/cron_healthcheck.sh
```

**脚本内容**:
```bash
#!/bin/bash
# 健康检查脚本（用于 cron）

set -e

PROJECT_DIR="/opt/redpacket"
LOG_FILE="${PROJECT_DIR}/logs/healthcheck.log"
BACKEND_URL="http://localhost:8000/healthz"
FRONTEND_URL="http://localhost:3001"

# 检查后端健康
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BACKEND_URL}" || echo "000")

if [ "${BACKEND_STATUS}" != "200" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Backend health check failed (HTTP ${BACKEND_STATUS}), restarting..." >> "${LOG_FILE}"
    cd "${PROJECT_DIR}"
    docker-compose -f docker-compose.production.yml restart backend
    # 或者使用 systemd: sudo systemctl restart redpacket-backend.service
fi

# 检查前端健康（可选）
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}" || echo "000")

if [ "${FRONTEND_STATUS}" != "200" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Frontend health check failed (HTTP ${FRONTEND_STATUS}), restarting..." >> "${LOG_FILE}"
    cd "${PROJECT_DIR}"
    docker-compose -f docker-compose.production.yml restart frontend
    # 或者使用 systemd: sudo systemctl restart redpacket-frontend.service
fi

# 如果都正常，记录成功日志（可选，避免日志过多）
# echo "[$(date +'%Y-%m-%d %H:%M:%S')] Health check passed" >> "${LOG_FILE}"
```

**设置执行权限**:
```bash
chmod +x /opt/redpacket/scripts/cron_healthcheck.sh
```

**添加到 crontab**（每 5 分钟检查一次）:
```
*/5 * * * * /opt/redpacket/scripts/cron_healthcheck.sh
```

---

### **任务 3: 日志清理**

**创建日志清理脚本**:
```bash
nano /opt/redpacket/scripts/cron_cleanup_logs.sh
```

**脚本内容**:
```bash
#!/bin/bash
# 日志清理脚本（用于 cron）

set -e

PROJECT_DIR="/opt/redpacket"
LOG_DIR="${PROJECT_DIR}/logs"
RETENTION_DAYS=30

# 清理超过 30 天的日志文件
find "${LOG_DIR}" -type f -name "*.log" -mtime +${RETENTION_DAYS} -delete

# 清理 Docker 日志（如果使用 Docker Compose）
docker system prune -f --volumes

# 记录清理日志
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Log cleanup completed" >> "${LOG_DIR}/cleanup.log"
```

**设置执行权限**:
```bash
chmod +x /opt/redpacket/scripts/cron_cleanup_logs.sh
```

**添加到 crontab**（每周日凌晨 3 点清理）:
```
0 3 * * 0 /opt/redpacket/scripts/cron_cleanup_logs.sh
```

---

### **任务 4: 监控指标收集**

**创建监控脚本**:
```bash
nano /opt/redpacket/scripts/cron_collect_metrics.sh
```

**脚本内容**:
```bash
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
    top -bn1 | grep "Cpu(s)" | awk '{print $2}'
    echo "Memory Usage:"
    free -h
    echo "Disk Usage:"
    df -h
    echo "Docker Container Status:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.CPU}}\t{{.MemUsage}}"
} > "${METRICS_DIR}/system_${TIMESTAMP}.txt"

# 收集应用指标（如果 Prometheus 可用）
# curl -s http://localhost:8000/metrics > "${METRICS_DIR}/app_${TIMESTAMP}.prom" 2>/dev/null || true

# 清理旧指标文件（保留 7 天）
find "${METRICS_DIR}" -type f -mtime +7 -delete
```

**设置执行权限**:
```bash
chmod +x /opt/redpacket/scripts/cron_collect_metrics.sh
```

**添加到 crontab**（每小时收集一次）:
```
0 * * * * /opt/redpacket/scripts/cron_collect_metrics.sh
```

---

## 📊 监控与告警

### **方案 1: 使用 systemd 监控**

**创建监控脚本**:
```bash
nano /opt/redpacket/scripts/monitor_service.sh
```

**脚本内容**:
```bash
#!/bin/bash
# systemd 服务监控脚本

SERVICE_NAME="redpacket.service"
LOG_FILE="/opt/redpacket/logs/monitor.log"
ALERT_EMAIL="admin@example.com"  # 可选：配置邮件告警

# 检查服务状态
if ! systemctl is-active --quiet "${SERVICE_NAME}"; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Service ${SERVICE_NAME} is not running!" >> "${LOG_FILE}"
    
    # 尝试重启
    systemctl restart "${SERVICE_NAME}"
    
    # 等待 10 秒后再次检查
    sleep 10
    if ! systemctl is-active --quiet "${SERVICE_NAME}"; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Service ${SERVICE_NAME} failed to restart!" >> "${LOG_FILE}"
        
        # 发送告警（需要配置邮件服务）
        # echo "Service ${SERVICE_NAME} is down!" | mail -s "Alert: Service Down" "${ALERT_EMAIL}"
    fi
fi
```

**添加到 crontab**（每 2 分钟检查一次）:
```
*/2 * * * * /opt/redpacket/scripts/monitor_service.sh
```

---

### **方案 2: 使用 Prometheus + Alertmanager**

**Prometheus 告警规则** (`deploy/prometheus/alerts.yml`):
```yaml
groups:
  - name: redpacket_alerts
    rules:
      - alert: ServiceDown
        expr: up{job="redpacket-backend"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Red Packet Backend is down"
          description: "Backend service has been down for more than 5 minutes"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 10% for 5 minutes"
```

**配置 Alertmanager** (`deploy/alertmanager/config.yml`):
```yaml
route:
  receiver: 'default-receiver'
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

receivers:
  - name: 'default-receiver'
    email_configs:
      - to: 'admin@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alertmanager@example.com'
        auth_password: 'password'
```

---

## 🚨 异常处理方案

### **1. 服务崩溃自动重启**

**systemd 配置**（已在服务文件中配置）:
```ini
Restart=always
RestartSec=10
```

**Docker Compose 配置**（`docker-compose.production.yml`）:
```yaml
services:
  backend:
    restart: unless-stopped
    # 或者
    restart: always
```

---

### **2. 数据库连接失败处理**

**创建数据库连接检查脚本**:
```bash
nano /opt/redpacket/scripts/check_db_connection.sh
```

**脚本内容**:
```bash
#!/bin/bash
# 数据库连接检查脚本

set -e

PROJECT_DIR="/opt/redpacket"
LOG_FILE="${PROJECT_DIR}/logs/db_check.log"

# 从环境变量读取数据库配置
source "${PROJECT_DIR}/.env.production"

# 检查数据库连接（Docker Compose 环境）
if docker exec redpacket_db pg_isready -U redpacket > /dev/null 2>&1; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database connection OK" >> "${LOG_FILE}"
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database connection FAILED!" >> "${LOG_FILE}"
    
    # 尝试重启数据库容器
    cd "${PROJECT_DIR}"
    docker-compose -f docker-compose.production.yml restart db
    
    # 等待 10 秒后再次检查
    sleep 10
    if ! docker exec redpacket_db pg_isready -U redpacket > /dev/null 2>&1; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database restart FAILED!" >> "${LOG_FILE}"
        # 发送告警
    fi
fi
```

**添加到 crontab**（每 5 分钟检查一次）:
```
*/5 * * * * /opt/redpacket/scripts/check_db_connection.sh
```

---

### **3. 磁盘空间不足处理**

**创建磁盘空间检查脚本**:
```bash
nano /opt/redpacket/scripts/check_disk_space.sh
```

**脚本内容**:
```bash
#!/bin/bash
# 磁盘空间检查脚本

set -e

PROJECT_DIR="/opt/redpacket"
LOG_FILE="${PROJECT_DIR}/logs/disk_check.log"
THRESHOLD=80  # 磁盘使用率阈值（%）

# 检查根分区使用率
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "${USAGE}" -gt "${THRESHOLD}" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Disk usage is ${USAGE}% (threshold: ${THRESHOLD}%)" >> "${LOG_FILE}"
    
    # 清理 Docker 未使用的资源
    docker system prune -f
    
    # 清理旧日志
    find "${PROJECT_DIR}/logs" -type f -name "*.log" -mtime +7 -delete
    
    # 清理旧备份
    find "${PROJECT_DIR}/backups" -type f -name "*.sql.gz" -mtime +7 -delete
fi
```

**添加到 crontab**（每小时检查一次）:
```
0 * * * * /opt/redpacket/scripts/check_disk_space.sh
```

---

### **4. 内存泄漏检测**

**创建内存检查脚本**:
```bash
nano /opt/redpacket/scripts/check_memory.sh
```

**脚本内容**:
```bash
#!/bin/bash
# 内存使用检查脚本

set -e

PROJECT_DIR="/opt/redpacket"
LOG_FILE="${PROJECT_DIR}/logs/memory_check.log"
THRESHOLD=90  # 内存使用率阈值（%）

# 获取内存使用率
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')

if [ "${MEMORY_USAGE}" -gt "${THRESHOLD}" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Memory usage is ${MEMORY_USAGE}% (threshold: ${THRESHOLD}%)" >> "${LOG_FILE}"
    
    # 重启服务（谨慎使用）
    # systemctl restart redpacket.service
    
    # 或者清理 Docker 缓存
    docker system prune -f
fi
```

**添加到 crontab**（每 30 分钟检查一次）:
```
*/30 * * * * /opt/redpacket/scripts/check_memory.sh
```

---

## 🔐 权限设置

### **1. 脚本执行权限**

```bash
# 为所有 cron 脚本设置执行权限
chmod +x /opt/redpacket/scripts/cron_*.sh
chmod +x /opt/redpacket/scripts/check_*.sh
chmod +x /opt/redpacket/scripts/monitor_*.sh
```

---

### **2. 日志目录权限**

```bash
# 创建日志目录
mkdir -p /opt/redpacket/logs
mkdir -p /opt/redpacket/backups
mkdir -p /opt/redpacket/metrics

# 设置目录权限
chown -R $USER:$USER /opt/redpacket/logs
chown -R $USER:$USER /opt/redpacket/backups
chown -R $USER:$USER /opt/redpacket/metrics

chmod 755 /opt/redpacket/logs
chmod 755 /opt/redpacket/backups
chmod 755 /opt/redpacket/metrics
```

---

### **3. systemd 服务权限**

**如果服务以非 root 用户运行**:
```bash
# 创建专用用户（可选）
sudo useradd -r -s /bin/false redpacket

# 修改服务文件中的 User 和 Group
# User=redpacket
# Group=redpacket

# 设置项目目录权限
sudo chown -R redpacket:redpacket /opt/redpacket
```

---

## 📝 完整 crontab 示例

**查看当前 crontab**:
```bash
crontab -l
```

**编辑 crontab**:
```bash
crontab -e
```

**完整 crontab 配置示例**:
```
# 数据库备份（每天凌晨 2 点）
0 2 * * * /opt/redpacket/scripts/cron_backup_db.sh >> /opt/redpacket/logs/cron_backup.log 2>&1

# 健康检查（每 5 分钟）
*/5 * * * * /opt/redpacket/scripts/cron_healthcheck.sh >> /opt/redpacket/logs/healthcheck.log 2>&1

# 服务监控（每 2 分钟）
*/2 * * * * /opt/redpacket/scripts/monitor_service.sh >> /opt/redpacket/logs/monitor.log 2>&1

# 数据库连接检查（每 5 分钟）
*/5 * * * * /opt/redpacket/scripts/check_db_connection.sh >> /opt/redpacket/logs/db_check.log 2>&1

# 磁盘空间检查（每小时）
0 * * * * /opt/redpacket/scripts/check_disk_space.sh >> /opt/redpacket/logs/disk_check.log 2>&1

# 内存检查（每 30 分钟）
*/30 * * * * /opt/redpacket/scripts/check_memory.sh >> /opt/redpacket/logs/memory_check.log 2>&1

# 日志清理（每周日凌晨 3 点）
0 3 * * 0 /opt/redpacket/scripts/cron_cleanup_logs.sh >> /opt/redpacket/logs/cleanup.log 2>&1

# 监控指标收集（每小时）
0 * * * * /opt/redpacket/scripts/cron_collect_metrics.sh >> /opt/redpacket/logs/metrics.log 2>&1
```

---

## ✅ 验证与测试

### **1. 测试 systemd 服务**

```bash
# 启动服务
sudo systemctl start redpacket.service

# 查看状态
sudo systemctl status redpacket.service

# 查看日志
sudo journalctl -u redpacket.service -f

# 测试重启
sudo systemctl restart redpacket.service

# 测试停止
sudo systemctl stop redpacket.service

# 测试开机自启（重启服务器）
sudo reboot
```

---

### **2. 测试 cron 任务**

```bash
# 手动执行脚本测试
/opt/redpacket/scripts/cron_backup_db.sh

# 查看 cron 日志（Ubuntu/Debian）
grep CRON /var/log/syslog

# 查看脚本输出日志
tail -f /opt/redpacket/logs/cron_backup.log
```

---

## 📚 参考资源

- **systemd 文档**: https://www.freedesktop.org/software/systemd/man/systemd.service.html
- **cron 文档**: `man crontab`
- **Docker Compose 文档**: https://docs.docker.com/compose/
- **项目部署文档**: `037_DEPLOY_GUIDE.md`

---

*最后更新: 2025-01-XX*

