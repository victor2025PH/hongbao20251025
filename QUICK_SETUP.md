# 一键配置 systemd 和 Cron 任务

> **快速部署指南** - 自动配置系统服务和定时任务

---

## 🚀 一键执行

在服务器上执行以下命令：

```bash
cd /opt/redpacket
sudo bash deploy/scripts/setup_systemd_and_cron.sh
```

---

## 📋 脚本功能

脚本会自动执行以下步骤：

1. **更新代码** - 从 Git 仓库拉取最新代码
2. **验证前端构建** - 运行 `npm run build` 验证 TypeScript 修复
3. **创建必要目录** - 创建 `logs/`, `backups/`, `metrics/` 目录
4. **设置脚本权限** - 为所有 cron 和检查脚本设置执行权限
5. **配置 systemd 服务** - 安装并启动 `redpacket.service`
6. **配置 Cron 任务** - 交互式添加定时任务
7. **验证配置** - 检查服务状态和配置

---

## ⚙️ 配置内容

### Systemd 服务

- **服务名称**: `redpacket.service`
- **功能**: 管理 Docker Compose 栈（自动启动、重启）
- **开机自启**: 已启用

### Cron 任务

脚本会自动添加以下定时任务：

| 任务 | 频率 | 脚本 |
|------|------|------|
| 数据库备份 | 每天 02:00 | `cron_backup_db.sh` |
| 健康检查 | 每 5 分钟 | `cron_healthcheck.sh` |
| 服务监控 | 每 2 分钟 | `monitor_service.sh` |
| 数据库连接检查 | 每 5 分钟 | `check_db_connection.sh` |
| 磁盘空间检查 | 每小时 | `check_disk_space.sh` |
| 内存检查 | 每 30 分钟 | `check_memory.sh` |
| 日志清理 | 每周日 03:00 | `cron_cleanup_logs.sh` |
| 监控指标收集 | 每小时 | `cron_collect_metrics.sh` |

---

## 🔍 验证配置

### 检查 systemd 服务

```bash
# 查看服务状态
sudo systemctl status redpacket.service

# 查看服务日志
sudo journalctl -u redpacket.service -f

# 重启服务
sudo systemctl restart redpacket.service
```

### 检查 Cron 任务

```bash
# 查看当前用户的 crontab
crontab -l

# 编辑 crontab
crontab -e
```

### 查看日志

```bash
# 健康检查日志
tail -f /opt/redpacket/logs/healthcheck.log

# 服务监控日志
tail -f /opt/redpacket/logs/monitor.log

# 数据库备份日志
tail -f /opt/redpacket/logs/cron_backup.log
```

### 测试健康检查

```bash
# 后端健康检查
curl http://localhost:8000/healthz

# 前端健康检查（如果实现了）
curl http://localhost:3001
```

---

## 🛠️ 手动配置（如果脚本失败）

如果一键脚本执行失败，可以手动执行以下步骤：

### 1. 设置脚本权限

```bash
cd /opt/redpacket
chmod +x scripts/cron_*.sh
chmod +x scripts/check_*.sh
chmod +x scripts/monitor_*.sh
```

### 2. 配置 systemd 服务

```bash
sudo cp deploy/systemd/redpacket.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable redpacket.service
sudo systemctl start redpacket.service
```

### 3. 配置 Cron 任务

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

## 📚 相关文档

- **详细配置指南**: `docs/SYSTEMD_AND_CRON_GUIDE.md`
- **项目进度报告**: `PROJECT_STATUS_REPORT.md`
- **部署指南**: `037_DEPLOY_GUIDE.md`

---

## ❓ 常见问题

### Q: 脚本执行时提示 "权限被拒绝"

**A**: 确保使用 `sudo` 执行脚本：
```bash
sudo bash deploy/scripts/setup_systemd_and_cron.sh
```

### Q: systemd 服务启动失败

**A**: 检查服务日志：
```bash
sudo journalctl -u redpacket.service -n 50
```

常见原因：
- Docker 未运行
- `docker-compose.production.yml` 文件不存在
- 端口被占用

### Q: Cron 任务没有执行

**A**: 检查：
1. Cron 服务是否运行：`sudo systemctl status cron`
2. 脚本是否有执行权限：`ls -l /opt/redpacket/scripts/`
3. 查看 Cron 日志：`grep CRON /var/log/syslog`

### Q: 如何修改 Cron 任务频率

**A**: 编辑 crontab：
```bash
crontab -e
```

修改对应行的时间表达式（格式：`分钟 小时 日 月 星期`）

---

*最后更新: 2025-01-XX*

