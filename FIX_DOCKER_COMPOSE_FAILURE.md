# 修复 Docker Compose 启动失败

> **错误**: `status=1/FAILURE` - `docker compose up -d` 执行失败

---

## 🔍 问题诊断

服务文件配置正确，但 `docker compose up -d` 命令执行失败。需要查看详细错误日志。

---

## ✅ 诊断步骤

### **步骤 1: 查看详细错误日志**

```bash
# 查看 systemd 服务日志
sudo journalctl -xeu redpacket.service -n 100

# 或者查看最近的错误
sudo journalctl -u redpacket.service --since "5 minutes ago" -n 50
```

### **步骤 2: 手动测试 docker compose 命令**

```bash
cd /opt/redpacket

# 测试配置文件是否有效
docker compose -f docker-compose.production.yml config

# 尝试启动（查看详细输出）
docker compose -f docker-compose.production.yml up -d
```

### **步骤 3: 检查 Docker 服务状态**

```bash
# 检查 Docker 是否运行
sudo systemctl status docker

# 检查 Docker Compose 版本
docker compose version
```

---

## 🔧 常见问题及解决方案

### **问题 1: 环境变量缺失**

**症状**: 日志显示环境变量未定义

**解决**:
```bash
cd /opt/redpacket

# 检查 .env.production 文件是否存在
ls -la .env.production

# 如果不存在，创建它
cp .env.example .env.production
nano .env.production  # 配置必要的环境变量
```

### **问题 2: 端口被占用**

**症状**: 日志显示 "port is already allocated"

**解决**:
```bash
# 检查端口占用
sudo netstat -tulpn | grep -E ':(8000|3001|5432)'

# 或者使用 ss
sudo ss -tulpn | grep -E ':(8000|3001|5432)'

# 停止占用端口的进程或修改 docker-compose.production.yml 中的端口
```

### **问题 3: 镜像构建失败**

**症状**: 日志显示 "failed to build" 或 "image not found"

**解决**:
```bash
cd /opt/redpacket

# 手动构建镜像
docker compose -f docker-compose.production.yml build

# 查看构建日志
docker compose -f docker-compose.production.yml build --no-cache 2>&1 | tee build.log
```

### **问题 4: 数据库连接失败**

**症状**: 日志显示数据库连接错误

**解决**:
```bash
# 检查数据库配置
grep DATABASE_URL .env.production

# 测试数据库连接（如果使用 PostgreSQL）
docker exec -it redpacket_db psql -U redpacket -d redpacket
```

### **问题 5: 权限问题**

**症状**: 日志显示 "permission denied"

**解决**:
```bash
# 检查目录权限
ls -la /opt/redpacket

# 修复权限
sudo chown -R $USER:$USER /opt/redpacket
chmod -R 755 /opt/redpacket
```

### **问题 6: 磁盘空间不足**

**症状**: 日志显示 "no space left on device"

**解决**:
```bash
# 检查磁盘空间
df -h

# 清理 Docker 未使用的资源
docker system prune -a -f

# 清理未使用的镜像
docker image prune -a -f
```

---

## 🚀 快速诊断脚本

在服务器上执行以下脚本，自动诊断问题：

```bash
cd /opt/redpacket

cat > /tmp/diagnose.sh << 'EOF'
#!/bin/bash
echo "🔍 Docker Compose 启动失败诊断..."
echo ""

echo "1. 检查 Docker 服务状态:"
sudo systemctl status docker --no-pager -l | head -10
echo ""

echo "2. 检查 Docker Compose 版本:"
docker compose version
echo ""

echo "3. 检查配置文件:"
docker compose -f docker-compose.production.yml config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ 配置文件有效"
else
    echo "   ❌ 配置文件有错误"
    docker compose -f docker-compose.production.yml config
fi
echo ""

echo "4. 检查环境变量文件:"
if [ -f ".env.production" ]; then
    echo "   ✅ .env.production 存在"
    echo "   关键变量:"
    grep -E "^(DATABASE_URL|POSTGRES_|DOMAIN|NOWPAYMENTS_)" .env.production | head -5
else
    echo "   ❌ .env.production 不存在"
fi
echo ""

echo "5. 检查端口占用:"
for port in 8000 3001 5432; do
    if sudo ss -tulpn | grep -q ":${port} "; then
        echo "   ⚠️  端口 ${port} 被占用"
        sudo ss -tulpn | grep ":${port} "
    else
        echo "   ✅ 端口 ${port} 可用"
    fi
done
echo ""

echo "6. 检查磁盘空间:"
df -h / | tail -1
echo ""

echo "7. 尝试手动启动（查看详细错误）:"
docker compose -f docker-compose.production.yml up -d 2>&1 | tail -20
echo ""

echo "8. 查看服务日志:"
sudo journalctl -u redpacket.service -n 20 --no-pager
EOF

chmod +x /tmp/diagnose.sh
bash /tmp/diagnose.sh
```

---

## 📝 手动启动和调试

如果自动诊断无法解决问题，手动启动并查看详细输出：

```bash
cd /opt/redpacket

# 1. 停止可能存在的容器
docker compose -f docker-compose.production.yml down

# 2. 检查配置文件
docker compose -f docker-compose.production.yml config > /tmp/compose-config.txt
cat /tmp/compose-config.txt

# 3. 尝试启动（前台运行，查看详细输出）
docker compose -f docker-compose.production.yml up

# 4. 如果前台启动成功，按 Ctrl+C 停止，然后后台启动
docker compose -f docker-compose.production.yml up -d

# 5. 查看容器状态
docker compose -f docker-compose.production.yml ps

# 6. 查看容器日志
docker compose -f docker-compose.production.yml logs
```

---

## 🔄 修复 systemd 服务

一旦手动启动成功，systemd 服务应该也能正常工作。如果还有问题，可以：

### **方案 1: 使用 Type=simple（如果 docker compose 命令能成功）**

修改服务文件，使用 `Type=simple` 并直接运行 docker compose：

```bash
sudo nano /etc/systemd/system/redpacket.service
```

修改为：
```ini
[Service]
Type=simple
ExecStart=/usr/bin/docker compose -f /opt/redpacket/docker-compose.production.yml up
ExecStop=/usr/bin/docker compose -f /opt/redpacket/docker-compose.production.yml down
Restart=always
RestartSec=10
```

然后：
```bash
sudo systemctl daemon-reload
sudo systemctl restart redpacket.service
```

### **方案 2: 使用启动脚本**

创建一个启动脚本，在脚本中处理错误：

```bash
cat > /opt/redpacket/start_services.sh << 'EOF'
#!/bin/bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml up -d
EOF

chmod +x /opt/redpacket/start_services.sh
```

然后修改服务文件：
```ini
ExecStart=/opt/redpacket/start_services.sh
```

---

## 📚 相关文档

- systemd 服务修复: `FIX_SYSTEMD_SERVICE.md`
- 部署指南: `037_DEPLOY_GUIDE.md`

---

*最后更新: 2025-01-XX*

