# 快速部署指南

> 一步一步引导您完成服务器部署

---

## 🚀 开始部署

### 步骤 1: 服务器环境检查

**在服务器上执行:**

```bash
# 下载并运行环境检查脚本
cd /tmp
curl -O https://raw.githubusercontent.com/your-repo/deploy/scripts/deploy_step1_check.sh
chmod +x deploy_step1_check.sh
./deploy_step1_check.sh
```

**或者手动检查:**

```bash
# 检查操作系统
cat /etc/os-release

# 检查 Python（需要 3.11+）
python3 --version

# 检查 Node.js（需要 18+）
node --version

# 检查端口占用
netstat -tlnp | grep -E ':(8000|8080|3001)'
```

**将检查结果告诉我，我会继续下一步。**

---

### 步骤 2: 安装必要软件

如果环境检查发现问题，执行安装脚本：

```bash
chmod +x deploy/scripts/deploy_step2_install.sh
./deploy/scripts/deploy_step2_install.sh
```

---

### 步骤 3: 准备项目代码

```bash
chmod +x deploy/scripts/deploy_step3_setup.sh
./deploy/scripts/deploy_step3_setup.sh
```

**需要准备:**
- Git 仓库地址（如果从 Git 克隆）
- 或使用 scp/rsync 上传代码

---

### 步骤 4: 安装依赖

```bash
chmod +x deploy/scripts/deploy_step4_dependencies.sh
./deploy/scripts/deploy_step4_dependencies.sh
```

---

### 步骤 5: 构建前端

```bash
chmod +x deploy/scripts/deploy_step5_build.sh
./deploy/scripts/deploy_step5_build.sh
```

---

### 步骤 6: 配置 Nginx

```bash
chmod +x deploy/scripts/deploy_step6_nginx.sh
./deploy/scripts/deploy_step6_nginx.sh
```

**需要准备:**
- 域名（如果有）
- 邮箱地址（用于 SSL 证书）

---

### 步骤 7: 启动服务

```bash
chmod +x deploy/scripts/deploy_step7_start.sh
./deploy/scripts/deploy_step7_start.sh
```

**选择启动方式:**
- systemd（推荐生产环境）
- PM2（进程管理）
- Docker Compose（容器化）
- 直接运行（开发/测试）

---

### 步骤 8: 验证部署

```bash
chmod +x deploy/scripts/deploy_step8_verify.sh
./deploy/scripts/deploy_step8_verify.sh
```

---

## 📝 手动部署步骤（如果脚本不可用）

### 1. 上传代码到服务器

```bash
# 从本地使用 scp
scp -r /本地/项目/路径/* user@服务器IP:/opt/redpacket/

# 或使用 rsync
rsync -avz /本地/项目/路径/ user@服务器IP:/opt/redpacket/
```

### 2. 配置环境变量

```bash
cd /opt/redpacket
cp .env.production.example .env.production
nano .env.production  # 编辑并填入真实值
```

### 3. 安装依赖

```bash
# Python 依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 前端依赖
cd frontend-next
npm install
npm run build
cd ..
```

### 4. 初始化数据库

```bash
source venv/bin/activate
python3 -c "from models.db import init_db; init_db()"
```

### 5. 启动服务

```bash
# 后端服务
uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --workers 2 &

# MiniApp API
uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --workers 2 &

# 前端服务
cd frontend-next
npm start &
```

### 6. 配置 Nginx

```bash
sudo cp deploy/nginx/nginx.conf /etc/nginx/sites-available/redpacket
sudo sed -i 's/yourdomain.com/实际域名/g' /etc/nginx/sites-available/redpacket
sudo ln -s /etc/nginx/sites-available/redpacket /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. 申请 SSL 证书

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🔍 故障排查

### 服务无法启动

```bash
# 查看日志
tail -f logs/web_admin.log
tail -f logs/miniapp_api.log
tail -f logs/frontend.log

# 检查端口占用
netstat -tlnp | grep -E ':(8000|8080|3001)'

# 检查进程
ps aux | grep -E 'uvicorn|node'
```

### 数据库连接失败

```bash
# 检查环境变量
cat .env.production | grep DATABASE_URL

# 测试数据库连接
source venv/bin/activate
python3 -c "from models.db import engine; engine.connect(); print('OK')"
```

### Nginx 配置错误

```bash
# 测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 需要帮助？

如果遇到问题，请提供：
1. 错误日志
2. 环境信息（操作系统、Python/Node 版本）
3. 执行的命令和输出

---

*最后更新: 2025-01-XX*

