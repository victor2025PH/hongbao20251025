# 修复缺失文件问题

> **问题**: 服务器上找不到 `deploy/scripts/setup_systemd_and_cron.sh` 文件

---

## 🔍 问题原因

服务器上的代码可能还没有更新，新创建的文件还没有同步到服务器。

---

## ✅ 解决方案

### **方案 1: 更新代码（推荐）**

如果使用 Git 管理代码：

```bash
cd /opt/redpacket
git pull origin master
# 或者
git pull origin main
```

然后再次执行：
```bash
sudo bash deploy/scripts/setup_systemd_and_cron.sh
```

---

### **方案 2: 手动创建文件**

如果无法使用 Git，可以手动创建文件：

#### 2.1 创建脚本目录

```bash
cd /opt/redpacket
mkdir -p deploy/scripts
```

#### 2.2 创建脚本文件

```bash
nano deploy/scripts/setup_systemd_and_cron.sh
```

然后复制以下内容（完整脚本内容请参考 `deploy/scripts/setup_systemd_and_cron.sh`）：

```bash
#!/bin/bash
# 一键配置 systemd 服务和 cron 任务脚本
# ... (完整内容)
```

或者使用 `curl` 或 `wget` 从 GitHub 下载（如果已推送到仓库）：

```bash
curl -o deploy/scripts/setup_systemd_and_cron.sh \
  https://raw.githubusercontent.com/YOUR_REPO/master/deploy/scripts/setup_systemd_and_cron.sh
```

#### 2.3 设置执行权限

```bash
chmod +x deploy/scripts/setup_systemd_and_cron.sh
```

---

### **方案 3: 直接手动执行步骤**

如果脚本文件暂时无法获取，可以手动执行各个步骤：

#### 步骤 1: 创建必要目录

```bash
cd /opt/redpacket
mkdir -p logs backups metrics
chmod 755 logs backups metrics
```

#### 步骤 2: 设置脚本权限（如果脚本已存在）

```bash
chmod +x scripts/cron_*.sh scripts/check_*.sh scripts/monitor_*.sh
```

#### 步骤 3: 配置 systemd 服务

```bash
# 检查服务文件是否存在
ls -la deploy/systemd/redpacket.service

# 如果存在，复制到系统目录
sudo cp deploy/systemd/redpacket.service /etc/systemd/system/

# 如果不存在，手动创建
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

Environment="COMPOSE_PROJECT_NAME=redpacket"
Environment="TZ=Asia/Manila"

StandardOutput=journal
StandardError=journal
SyslogIdentifier=redpacket

[Install]
WantedBy=multi-user.target
```

然后启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable redpacket.service
sudo systemctl start redpacket.service
```

#### 步骤 4: 配置 Cron 任务

```bash
crontab -e
```

添加以下内容：

```
# Red Packet System - Cron 任务
0 2 * * * /opt/redpacket/scripts/cron_backup_db.sh >> /opt/redpacket/logs/cron_backup.log 2>&1
*/5 * * * * /opt/redpacket/scripts/cron_healthcheck.sh >> /opt/redpacket/logs/healthcheck.log 2>&1
*/2 * * * * /opt/redpacket/scripts/monitor_service.sh >> /opt/redpacket/logs/monitor.log 2>&1
*/5 * * * * /opt/redpacket/scripts/check_db_connection.sh >> /opt/redpacket/logs/db_check.log 2>&1
0 * * * * /opt/redpacket/scripts/check_disk_space.sh >> /opt/redpacket/logs/disk_check.log 2>&1
*/30 * * * * /opt/redpacket/scripts/check_memory.sh >> /opt/redpacket/logs/memory_check.log 2>&1
0 3 * * 0 /opt/redpacket/scripts/cron_cleanup_logs.sh >> /opt/redpacket/logs/cleanup.log 2>&1
0 * * * * /opt/redpacket/scripts/cron_collect_metrics.sh >> /opt/redpacket/logs/metrics.log 2>&1
```

---

## 🔍 验证文件是否存在

执行以下命令检查文件：

```bash
cd /opt/redpacket

# 检查脚本文件
ls -la deploy/scripts/setup_systemd_and_cron.sh

# 检查 systemd 服务文件
ls -la deploy/systemd/redpacket.service

# 检查 cron 脚本
ls -la scripts/cron_*.sh
ls -la scripts/check_*.sh
```

---

## 📝 快速检查清单

- [ ] 代码已更新（`git pull` 或手动同步）
- [ ] `deploy/scripts/setup_systemd_and_cron.sh` 文件存在
- [ ] `deploy/systemd/redpacket.service` 文件存在
- [ ] `scripts/cron_*.sh` 文件存在
- [ ] 所有脚本有执行权限（`chmod +x`）

---

## 🚀 推荐操作流程

1. **首先尝试更新代码**:
   ```bash
   cd /opt/redpacket
   git pull origin master
   ```

2. **检查文件是否存在**:
   ```bash
   ls -la deploy/scripts/setup_systemd_and_cron.sh
   ```

3. **如果文件存在，执行脚本**:
   ```bash
   sudo bash deploy/scripts/setup_systemd_and_cron.sh
   ```

4. **如果文件不存在，使用方案 3 手动执行**

---

*最后更新: 2025-01-XX*

