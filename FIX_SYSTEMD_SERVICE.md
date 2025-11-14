# 修复 systemd 服务启动失败

> **错误**: `status=203/EXEC` - 执行文件未找到

---

## 🔍 问题诊断

错误 `status=203/EXEC` 表示 systemd 无法找到或执行 `ExecStart` 中指定的命令。

常见原因：
1. `docker-compose` 命令路径不正确
2. `docker-compose.production.yml` 文件不存在
3. 权限问题

---

## ✅ 解决方案

### **步骤 1: 检查 docker-compose 路径**

在服务器上执行：

```bash
# 查找 docker-compose 的实际路径
which docker-compose
# 或者
whereis docker-compose

# 检查 docker compose (新版本，作为 docker 的子命令)
docker compose version
```

**可能的结果**：
- `/usr/local/bin/docker-compose` (旧版本)
- `/usr/bin/docker-compose` (系统安装)
- 或者使用 `docker compose` (新版本，作为子命令)

---

### **步骤 2: 检查 docker-compose.production.yml 文件**

```bash
cd /opt/redpacket
ls -la docker-compose.production.yml
```

如果文件不存在，检查是否有其他名称：
```bash
ls -la docker-compose*.yml
```

---

### **步骤 3: 修复 systemd 服务文件**

根据检查结果，更新服务文件：

#### 情况 A: docker-compose 在 `/usr/local/bin/`

```bash
sudo nano /etc/systemd/system/redpacket.service
```

修改 `ExecStart` 行：
```ini
ExecStart=/usr/local/bin/docker-compose -f /opt/redpacket/docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f /opt/redpacket/docker-compose.production.yml down
ExecReload=/usr/local/bin/docker-compose -f /opt/redpacket/docker-compose.production.yml restart
```

#### 情况 B: 使用 docker compose (新版本)

```bash
sudo nano /etc/systemd/system/redpacket.service
```

修改为：
```ini
ExecStart=/usr/bin/docker compose -f /opt/redpacket/docker-compose.production.yml up -d
ExecStop=/usr/bin/docker compose -f /opt/redpacket/docker-compose.production.yml down
ExecReload=/usr/bin/docker compose -f /opt/redpacket/docker-compose.production.yml restart
```

#### 情况 C: docker-compose.production.yml 文件不存在

如果文件不存在，检查是否有其他名称，或者使用默认的 `docker-compose.yml`：

```bash
sudo nano /etc/systemd/system/redpacket.service
```

修改为：
```ini
ExecStart=/usr/bin/docker-compose -f /opt/redpacket/docker-compose.yml up -d
ExecStop=/usr/bin/docker-compose -f /opt/redpacket/docker-compose.yml down
ExecReload=/usr/bin/docker-compose -f /opt/redpacket/docker-compose.yml restart
```

---

### **步骤 4: 重新加载并启动服务**

```bash
sudo systemctl daemon-reload
sudo systemctl start redpacket.service
sudo systemctl status redpacket.service
```

---

## 🔧 快速修复脚本

在服务器上执行以下命令（自动检测并修复）：

```bash
cd /opt/redpacket

# 检测 docker-compose 路径
DOCKER_COMPOSE_PATH=$(which docker-compose 2>/dev/null || echo "/usr/bin/docker compose")

# 检测 docker-compose 文件
COMPOSE_FILE="docker-compose.production.yml"
if [ ! -f "${COMPOSE_FILE}" ]; then
    COMPOSE_FILE="docker-compose.yml"
fi

# 更新服务文件
sudo tee /etc/systemd/system/redpacket.service > /dev/null << EOF
[Unit]
Description=Red Packet System (Docker Compose)
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/redpacket
ExecStart=${DOCKER_COMPOSE_PATH} -f /opt/redpacket/${COMPOSE_FILE} up -d
ExecStop=${DOCKER_COMPOSE_PATH} -f /opt/redpacket/${COMPOSE_FILE} down
ExecReload=${DOCKER_COMPOSE_PATH} -f /opt/redpacket/${COMPOSE_FILE} restart
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
EOF

# 重新加载并启动
sudo systemctl daemon-reload
sudo systemctl enable redpacket.service
sudo systemctl start redpacket.service
sudo systemctl status redpacket.service
```

---

## 🔍 详细诊断

如果问题仍然存在，执行以下诊断命令：

```bash
# 1. 检查 docker-compose 是否可用
docker-compose --version
# 或者
docker compose version

# 2. 检查 docker-compose 文件
cd /opt/redpacket
ls -la docker-compose*.yml

# 3. 手动测试 docker-compose 命令
docker-compose -f docker-compose.production.yml config
# 或者
docker compose -f docker-compose.production.yml config

# 4. 查看详细错误日志
sudo journalctl -xeu redpacket.service -n 50

# 5. 检查 Docker 服务状态
sudo systemctl status docker
```

---

## 📝 常见问题

### Q: docker-compose 命令找不到

**A**: 安装 docker-compose 或使用新版本的 `docker compose`：

```bash
# 安装 docker-compose (旧版本)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 或者使用新版本（Docker 20.10+ 内置）
# 直接使用: docker compose
```

### Q: docker-compose.production.yml 文件不存在

**A**: 检查文件名称，或创建符号链接：

```bash
cd /opt/redpacket
# 如果存在 docker-compose.yml
ln -s docker-compose.yml docker-compose.production.yml
```

### Q: 权限问题

**A**: 确保 systemd 服务有权限访问 Docker：

```bash
# 检查当前用户是否在 docker 组
groups

# 如果不在，添加到 docker 组
sudo usermod -aG docker $USER
# 需要重新登录生效
```

---

*最后更新: 2025-01-XX*

