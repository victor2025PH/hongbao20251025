# 部署指南（简短版）

本文档提供快速部署指南，帮助你在本地或生产环境快速启动 037 红包系统。

> **参考文档**: 详细配置请参考 `docs/CONFIG_ENV_MATRIX.md`、`docs/DB_MIGRATION_AND_SEEDING.md`、`docs/HEALTHCHECK_AND_SELFTEST.md`。

---

## 概览

本系统包含以下服务：

| 服务 | 端口 | 说明 |
|------|------|------|
| **Web Admin** | 8000 | FastAPI Web 管理后台（HTML + REST API） |
| **MiniApp API** | 8080 | FastAPI MiniApp 后端 API |
| **前端控制台** | 3001 | Next.js 前端控制台 |
| **数据库** | - | SQLite（开发）/ PostgreSQL（生产） |

---

## 环境准备

### Python 版本

- **要求**: Python 3.9+
- **推荐**: Python 3.11+

### Node.js 版本

- **要求**: Node.js 18+
- **推荐**: Node.js 20+

### 必需环境变量

创建 `.env` 文件（参考 `docs/CONFIG_ENV_MATRIX.md`），至少包含：

```bash
# 必填
BOT_TOKEN=你的Telegram_Bot_Token
DATABASE_URL=sqlite:///./data.sqlite  # 或 postgresql://user:pass@host:5432/dbname
ADMIN_IDS=123456,789012  # 管理员 Telegram ID（逗号分隔）

# 推荐（生产环境必填）
MINIAPP_JWT_SECRET=强随机字符串  # 必须修改
ADMIN_SESSION_SECRET=强随机字符串  # 必须修改
```

---

## 本地开发一键启动

### 1. 创建虚拟环境 & 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt
```

---

### 2. 初始化数据库

```bash
# 初始化数据库（创建所有表）
python -c "from models.db import init_db; init_db()"

# 可选：初始化测试数据
python scripts/seed_public_groups.py --groups 3 --activities 3
```

---

### 3. 启动 Web Admin（端口 8000）

```bash
uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --reload
```

**验证**:
```bash
curl http://localhost:8000/healthz
# 预期: {"ok": true, "ts": "..."}
```

---

### 4. 启动 MiniApp API（端口 8080，可选）

```bash
uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --reload
```

**验证**:
```bash
curl http://localhost:8080/healthz
# 预期: {"ok": true}
```

---

### 5. 启动前端控制台（端口 3001）

```bash
cd frontend-next
npm install
npm run dev
```

**验证**: 访问 `http://localhost:3001`，应看到 Dashboard 页面。

---

### 6. 快速检查清单

```bash
# 1. Web Admin 健康检查
curl http://localhost:8000/healthz

# 2. Web Admin 就绪检查
curl http://localhost:8000/readyz

# 3. MiniApp API 健康检查
curl http://localhost:8080/healthz

# 4. Dashboard API（公开接口）
curl http://localhost:8000/admin/api/v1/dashboard/public

# 5. 前端页面
# 浏览器访问: http://localhost:3001
```

---

## 生产环境部署建议

### 使用 systemd（推荐）

#### Web Admin 服务

创建 `/etc/systemd/system/hongbao-web-admin.service`:

```ini
[Unit]
Description=Hongbao Web Admin
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/037重新开发新功能
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn web_admin.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**启动服务**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hongbao-web-admin
sudo systemctl start hongbao-web-admin
```

#### MiniApp API 服务

创建 `/etc/systemd/system/hongbao-miniapp-api.service`:

```ini
[Unit]
Description=Hongbao MiniApp API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/037重新开发新功能
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn miniapp.main:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

**启动服务**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hongbao-miniapp-api
sudo systemctl start hongbao-miniapp-api
```

---

### 使用 Docker Compose（可选）

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web-admin:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/hongbao
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_IDS=${ADMIN_IDS}
    depends_on:
      - db

  miniapp-api:
    build: .
    command: uvicorn miniapp.main:app --host 0.0.0.0 --port 8080
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/hongbao
      - BOT_TOKEN=${BOT_TOKEN}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=hongbao
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**启动**:
```bash
docker-compose up -d
```

---

### 数据库建议

**生产环境推荐使用 PostgreSQL**:

1. **安装 PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # CentOS/RHEL
   sudo yum install postgresql-server postgresql-contrib
   ```

2. **创建数据库**:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE hongbao_db;
   CREATE USER hongbao_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE hongbao_db TO hongbao_user;
   ```

3. **更新 DATABASE_URL**:
   ```bash
   DATABASE_URL=postgresql://hongbao_user:your_password@localhost:5432/hongbao_db
   ```

4. **初始化数据库**:
   ```bash
   python -c "from models.db import init_db; init_db()"
   ```

5. **定期备份**:
   ```bash
   # 每日备份脚本（crontab）
   0 2 * * * pg_dump -U hongbao_user hongbao_db > /backup/hongbao_$(date +\%Y\%m\%d).sql
   ```

---

### 反向代理（Nginx）

创建 `/etc/nginx/sites-available/hongbao`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Web Admin
    location /admin {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # MiniApp API
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 前端控制台
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**启用配置**:
```bash
sudo ln -s /etc/nginx/sites-available/hongbao /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 发布与回滚

### 发布前检查

```bash
# 1. 运行测试
pytest tests/ -v

# 2. 运行自检脚本
python scripts/self_check.py

# 3. 检查环境变量
python scripts/check_env.py

# 4. 构建前端（如果修改了前端）
cd frontend-next
npm run build
```

---

### 发布步骤

1. **备份数据库**:
   ```bash
   # SQLite
   cp data.sqlite data.sqlite.backup-$(date +%Y%m%d-%H%M%S)
   
   # PostgreSQL
   pg_dump -U user hongbao_db > backup-$(date +%Y%m%d-%H%M%S).sql
   ```

2. **更新代码**:
   ```bash
   git pull origin main
   ```

3. **安装依赖**（如果有更新）:
   ```bash
   pip install -r requirements.txt
   cd frontend-next && npm install
   ```

4. **运行数据库迁移**（如果有）:
   ```bash
   python -c "from models.db import init_db; init_db()"
   ```

5. **重启服务**:
   ```bash
   # systemd
   sudo systemctl restart hongbao-web-admin
   sudo systemctl restart hongbao-miniapp-api
   
   # 或 docker-compose
   docker-compose restart
   ```

6. **验证服务**:
   ```bash
   curl http://localhost:8000/healthz
   curl http://localhost:8080/healthz
   ```

---

### 回滚步骤

如果新版本有问题，快速回滚：

1. **代码回滚**:
   ```bash
   git checkout <previous-commit-hash>
   ```

2. **数据库回滚**（如果新版本包含数据库变更）:
   ```bash
   # SQLite
   cp data.sqlite.backup-YYYYMMDD-HHMMSS data.sqlite
   
   # PostgreSQL
   psql -U user -d hongbao_db < backup-YYYYMMDD-HHMMSS.sql
   ```

3. **重启服务**:
   ```bash
   sudo systemctl restart hongbao-web-admin
   sudo systemctl restart hongbao-miniapp-api
   ```

4. **验证回滚**:
   ```bash
   curl http://localhost:8000/healthz
   # 检查关键功能是否正常
   ```

---

## 常见问题

### Q: 端口被占用怎么办？

```bash
# 检查端口占用
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# 杀死进程或修改端口
```

### Q: 数据库连接失败？

1. 检查 `DATABASE_URL` 是否正确
2. 检查数据库服务是否运行
3. 检查数据库用户权限

### Q: 前端无法访问后端 API？

1. 检查后端服务是否运行
2. 检查 `NEXT_PUBLIC_ADMIN_API_BASE_URL` 配置
3. 检查 CORS 设置（如果有）

### Q: 登录后无法访问管理页面？

1. 检查 `ADMIN_IDS` 是否包含你的 Telegram ID
2. 检查 Session Cookie 是否设置
3. 查看浏览器控制台错误信息

---

## 快速命令参考

```bash
# 启动所有服务（开发环境）
# 终端 1:
uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2:
uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --reload

# 终端 3:
cd frontend-next && npm run dev

# 健康检查
curl http://localhost:8000/healthz
curl http://localhost:8080/healthz

# 查看服务状态（systemd）
sudo systemctl status hongbao-web-admin
sudo systemctl status hongbao-miniapp-api

# 查看日志（systemd）
sudo journalctl -u hongbao-web-admin -f
sudo journalctl -u hongbao-miniapp-api -f
```

---

*最后更新: 2025-01-XX*

