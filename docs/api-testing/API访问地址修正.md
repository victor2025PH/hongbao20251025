# 🔌 API 访问地址修正

## ✅ 问题修复

### 问题描述
之前的 API 地址使用 `127.0.0.1`，只能从服务器本地访问，无法从外部访问。

### 解决方案
已修改 `docker-compose.production.yml`，将端口绑定从 `127.0.0.1` 改为 `0.0.0.0`，允许外部访问。

---

## 🌐 正确的 API 访问地址

### 服务器信息
- **公网 IP**: `165.154.233.55`
- **内网 IP**: `10.56.130.4`

### Web Admin API (8000)

#### 健康检查
```bash
curl http://165.154.233.55:8000/healthz
```

或者使用浏览器访问：
```
http://165.154.233.55:8000/healthz
```

#### API 文档（Swagger UI）
```
http://165.154.233.55:8000/docs
```

#### 预期响应
```json
{"ok":true,"ts":"2025-11-14T17:58:13.662815"}
```

---

### MiniApp API (8080)

#### 健康检查
```bash
curl http://165.154.233.55:8080/healthz
```

或者使用浏览器访问：
```
http://165.154.233.55:8080/healthz
```

#### API 文档（Swagger UI）
```
http://165.154.233.55:8080/docs
```

#### 预期响应
```json
{"ok":true}
```

---

## 🔒 防火墙配置

如果无法访问，需要检查服务器防火墙：

### 检查防火墙状态
```bash
# Ubuntu/Debian
sudo ufw status

# CentOS/RHEL
sudo firewall-cmd --list-all
```

### 开放端口（如果需要）
```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 8000/tcp
sudo ufw allow 8080/tcp

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

---

## 📝 测试命令

### Windows PowerShell
```powershell
# Web Admin API
Invoke-WebRequest -Uri "http://165.154.233.55:8000/healthz" | Select-Object -ExpandProperty Content

# MiniApp API
Invoke-WebRequest -Uri "http://165.154.233.55:8080/healthz" | Select-Object -ExpandProperty Content
```

### Linux/Mac/Windows Git Bash
```bash
# Web Admin API
curl http://165.154.233.55:8000/healthz

# MiniApp API
curl http://165.154.233.55:8080/healthz
```

### 浏览器访问
直接访问：
- Web Admin API: http://165.154.233.55:8000/healthz
- MiniApp API: http://165.154.233.55:8080/healthz

---

## 🔍 故障排除

### 问题 1: 连接超时
- 检查服务器防火墙是否开放端口
- 检查云服务商安全组规则
- 确认服务正在运行

### 问题 2: 连接被拒绝
- 检查服务是否正常运行：`docker compose ps`
- 检查端口是否监听：`netstat -tlnp | grep -E ":8000|:8080"`
- 查看服务日志：`docker compose logs web_admin` 或 `docker compose logs miniapp_api`

### 问题 3: 返回 404
- API 文档路径可能不同
- 检查服务日志了解可用路由

---

## ✅ 验证清单

- [ ] Web Admin API 健康检查可通过公网 IP 访问
- [ ] MiniApp API 健康检查可通过公网 IP 访问
- [ ] 防火墙已正确配置
- [ ] 可以测试其他 API 端点

