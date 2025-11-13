# 修复部署问题

> 解决 Docker 权限和 .env.production 语法错误

---

## 🔍 发现的问题

1. **Docker 权限问题**: `permission denied while trying to connect to the Docker daemon socket`
2. **.env.production 语法错误**: `line 64: unexpected character "/" in variable name "static/uploads"`
3. **POSTGRES_PASSWORD 未设置警告**

---

## ✅ 解决方案

### 问题 1: Docker 权限问题

**错误信息:**
```
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```

**解决方法:**

```bash
# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新加载组权限（或重新登录）
newgrp docker

# 验证权限
docker ps
```

**如果仍然不行，使用 sudo:**

```bash
# 所有 docker 命令前加 sudo
sudo docker compose -f docker-compose.production.yml build frontend
sudo docker compose -f docker-compose.production.yml up -d
```

---

### 问题 2: .env.production 语法错误

**错误信息:**
```
failed to read /opt/redpacket/.env.production: line 64: unexpected character "/" in variable name "static/uploads"
```

**原因:** `.env.production` 文件第 64 行可能有注释或路径格式错误。

**解决方法:**

```bash
cd /opt/redpacket

# 检查第 64 行附近的内容
sed -n '60,70p' .env.production

# 如果看到类似这样的行（错误）:
# static/uploads=/path/to/uploads  # 这是错误的

# 应该改为（正确）:
# STATIC_UPLOADS_DIR=/path/to/uploads  # 环境变量名不能包含斜杠

# 或者直接删除/注释掉有问题的行
nano .env.production
```

**常见错误格式:**
```bash
# ❌ 错误：变量名包含斜杠
static/uploads=/opt/redpacket/static/uploads

# ✅ 正确：使用下划线
STATIC_UPLOADS_DIR=/opt/redpacket/static/uploads

# ✅ 或者使用注释
# static/uploads directory: /opt/redpacket/static/uploads
```

---

### 问题 3: POSTGRES_PASSWORD 未设置

**警告信息:**
```
WARN [0000] The "POSTGRES_PASSWORD" variable is not set. Defaulting to a blank string.
```

**解决方法:**

确保 `.env.production` 文件中包含：

```bash
POSTGRES_PASSWORD=您的强密码
```

**检查配置:**

```bash
cd /opt/redpacket

# 检查 POSTGRES_PASSWORD 是否设置
grep POSTGRES_PASSWORD .env.production

# 如果没有，添加它
echo "POSTGRES_PASSWORD=YourStrongPassword123!" >> .env.production
```

---

## 🚀 完整修复步骤

在服务器上执行：

```bash
cd /opt/redpacket

# 1. 修复 Docker 权限
sudo usermod -aG docker $USER
newgrp docker

# 2. 检查并修复 .env.production 语法错误
nano .env.production
# 找到第 64 行附近，检查是否有包含斜杠的变量名
# 如果有，删除或注释掉，或改为正确的格式

# 3. 确保 POSTGRES_PASSWORD 已设置
grep -q "POSTGRES_PASSWORD=" .env.production || echo "POSTGRES_PASSWORD=YourStrongPassword123!" >> .env.production

# 4. 验证 .env.production 语法
docker compose -f docker-compose.production.yml config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ .env.production 语法正确"
else
    echo "❌ .env.production 仍有语法错误，请检查"
fi

# 5. 重新构建和启动
sudo docker compose -f docker-compose.production.yml build frontend
sudo docker compose -f docker-compose.production.yml up -d
```

---

## 🔍 检查 .env.production 文件

**查看文件内容:**

```bash
cd /opt/redpacket

# 查看整个文件
cat .env.production

# 查看第 60-70 行（错误行附近）
sed -n '60,70p' .env.production

# 检查所有包含斜杠的行（可能是问题）
grep -n "/" .env.production | grep -v "^#" | grep -v "://"
```

**常见问题行:**

```bash
# ❌ 这些格式是错误的：
static/uploads=/path
files/export=/path
logs/app.log=/path

# ✅ 应该改为：
STATIC_UPLOADS_DIR=/path
FILES_EXPORT_DIR=/path
LOGS_APP_FILE=/path

# 或者直接注释掉：
# static/uploads directory: /path
```

---

## 📝 快速修复命令

**一键修复（在服务器上执行）:**

```bash
cd /opt/redpacket

# 修复 Docker 权限
sudo usermod -aG docker $USER
newgrp docker

# 修复 .env.production（删除包含斜杠的变量名行）
sed -i '/^[^#]*\/.*=/d' .env.production

# 确保 POSTGRES_PASSWORD 存在
grep -q "^POSTGRES_PASSWORD=" .env.production || sed -i 's/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=YourStrongPassword123!/' .env.production || echo "POSTGRES_PASSWORD=YourStrongPassword123!" >> .env.production

# 验证并重新构建
sudo docker compose -f docker-compose.production.yml config
sudo docker compose -f docker-compose.production.yml build frontend
sudo docker compose -f docker-compose.production.yml up -d
```

---

*最后更新: 2025-01-XX*

