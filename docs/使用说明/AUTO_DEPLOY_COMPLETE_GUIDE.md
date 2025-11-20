# 自动化协同部署完整方案

> 实现本地服务器与远程服务器之间的全自动化协同部署，支持持续集成与发布（CI/CD）

---

## 📋 目录

1. [架构概览](#架构概览)
2. [前置准备](#前置准备)
3. [方案一：GitHub Actions + SSH 部署（推荐）](#方案一github-actions--ssh-部署推荐)
4. [方案二：Webhook + 本地触发](#方案二webhook--本地触发)
5. [方案三：完全自动化 Pipeline](#方案三完全自动化-pipeline)
6. [安全认证配置](#安全认证配置)
7. [错误处理与回滚](#错误处理与回滚)
8. [监控与通知](#监控与通知)
9. [故障排除](#故障排除)

---

## 🏗️ 架构概览

### 部署流程

```
本地开发 → Git Push → GitHub → 自动触发
                                ↓
                         GitHub Actions / Webhook
                                ↓
                         SSH 连接到服务器
                                ↓
                         Git Pull + 构建 + 部署
                                ↓
                         健康检查 + 通知
```

### 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **GitHub Actions** | 无需本地维护，云端执行 | 需要 GitHub 配置 | 开源/私有仓库 |
| **Webhook + 本地** | 灵活，可自定义 | 需要本地服务器运行 | 内网环境 |
| **Pipeline 脚本** | 简单直接 | 需要手动触发 | 小型项目 |

---

## 🔧 前置准备

### 1. 服务器环境要求

- **操作系统**: Ubuntu 20.04+ / Debian 11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.25+
- **SSH**: OpenSSH 7.6+

### 2. 网络要求

- 服务器可以访问 GitHub（如果使用 GitHub Actions）
- 本地可以 SSH 连接到服务器
- 服务器开放必要端口（SSH: 22, HTTP: 80/443, 应用端口: 8000/8080/3001）

### 3. 权限要求

- GitHub 仓库有推送权限
- 服务器有 sudo 权限（用于安装软件）
- 服务器有 Docker 操作权限

---

## 🚀 方案一：GitHub Actions + SSH 部署（推荐）

### 特点

- ✅ **完全自动化**：代码推送到 GitHub 后自动部署
- ✅ **无需本地维护**：部署在云端执行
- ✅ **安全性高**：使用 SSH 密钥认证
- ✅ **支持多环境**：可配置开发/测试/生产环境

### 配置步骤

#### 步骤 1: 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

1. 进入仓库 → `Settings` → `Secrets and variables` → `Actions`
2. 添加以下 Secrets：

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `DEPLOY_HOST` | 服务器 IP 地址 | `165.154.233.55` |
| `DEPLOY_USER` | SSH 用户名 | `ubuntu` |
| `DEPLOY_SSH_KEY` | SSH 私钥（完整内容） | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DEPLOY_PORT` | SSH 端口（可选） | `22` |
| `DEPLOY_PATH` | 项目部署路径 | `/opt/redpacket` |

#### 步骤 2: 创建 GitHub Actions 工作流

创建工作流文件：`.github/workflows/deploy.yml`

（文件内容见下文）

#### 步骤 3: 配置服务器 SSH 密钥

在服务器上配置免密登录：

```bash
# 在服务器上执行
mkdir -p ~/.ssh
chmod 700 ~/.ssh
# 将 GitHub Actions 使用的公钥添加到 authorized_keys
```

#### 步骤 4: 测试部署

```bash
# 在本地推送代码
git add .
git commit -m "test: 测试自动部署"
git push origin master
```

部署会自动触发，可在 GitHub Actions 页面查看执行日志。

---

## 🔄 方案二：Webhook + 本地触发

### 特点

- ✅ **灵活可控**：可在本地控制部署时机
- ✅ **支持多服务器**：可同时部署到多个服务器
- ✅ **自定义流程**：可完全自定义部署流程

### 配置步骤

#### 步骤 1: 配置 GitHub Webhook

1. 进入仓库 → `Settings` → `Webhooks` → `Add webhook`
2. 配置：
   - **Payload URL**: `http://your-local-server:8080/webhook/deploy`
   - **Content type**: `application/json`
   - **Secret**: 设置一个安全的密钥
   - **Events**: 选择 `Just the push event`

#### 步骤 2: 在服务器上安装 Webhook 接收器

（见下文脚本）

#### 步骤 3: 在本地运行 Webhook 服务器

```bash
# 安装依赖
pip install flask requests

# 运行 Webhook 服务器
python deploy/webhook_receiver.py
```

---

## 🔁 方案三：完全自动化 Pipeline

### 特点

- ✅ **一键部署**：单命令完成所有操作
- ✅ **本地可控**：完全在本地执行
- ✅ **支持回滚**：可快速回滚到上一版本

### 使用方法

```bash
# 本地执行部署
bash deploy/scripts/auto_deploy_pipeline.sh

# 或使用 Makefile
make deploy
```

---

## 🔐 安全认证配置

### 1. SSH 密钥认证

#### 生成 SSH 密钥对

```bash
# 在本地生成密钥对
ssh-keygen -t rsa -b 4096 -C "deploy@redpacket" -f ~/.ssh/deploy_key

# 查看公钥
cat ~/.ssh/deploy_key.pub

# 查看私钥（用于 GitHub Secrets）
cat ~/.ssh/deploy_key
```

#### 在服务器上配置公钥

```bash
# 在服务器上执行
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### 测试 SSH 连接

```bash
# 在本地测试
ssh -i ~/.ssh/deploy_key ubuntu@服务器IP "echo 'SSH 连接成功'"
```

### 2. Webhook Secret 认证

```bash
# 生成随机密钥
openssl rand -hex 32

# 在 Webhook 配置中使用此密钥
# 在接收脚本中验证签名
```

### 3. 环境变量保护

```bash
# 在服务器上创建环境变量文件
cat > /opt/redpacket/.env.production << 'EOF'
# 敏感信息不提交到 Git
DATABASE_URL=postgresql://...
REDIS_PASSWORD=...
SECRET_KEY=...
EOF

# 设置权限
chmod 600 /opt/redpacket/.env.production
```

---

## ⚠️ 错误处理与回滚

### 1. 部署前检查

- ✅ Git 仓库可访问
- ✅ 服务器 SSH 连接正常
- ✅ 服务器磁盘空间充足
- ✅ 必需端口未被占用

### 2. 部署中监控

- ✅ 代码拉取成功
- ✅ Docker 镜像构建成功
- ✅ 服务启动成功
- ✅ 健康检查通过

### 3. 自动回滚机制

如果部署失败，自动回滚到上一版本：

```bash
# 回滚脚本
git checkout HEAD~1
docker compose -f docker-compose.production.yml up -d
```

### 4. 错误通知

部署失败时自动发送通知：
- 邮件通知
- 企业微信/钉钉通知
- Slack 通知

---

## 📊 监控与通知

### 1. 部署状态监控

- 查看 GitHub Actions 执行日志
- 查看服务器部署日志：`/opt/redpacket/logs/deploy.log`
- 使用 Prometheus + Grafana 监控服务状态

### 2. 通知配置

#### 邮件通知

```bash
# 配置 SMTP 服务器
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-password
```

#### 企业微信通知

```bash
# 配置 Webhook URL
export WECHAT_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
```

---

## 🐛 故障排除

### 常见问题

#### 1. SSH 连接失败

```bash
# 检查 SSH 配置
ssh -v -i ~/.ssh/deploy_key ubuntu@服务器IP

# 检查服务器 SSH 服务
sudo systemctl status sshd
```

#### 2. Git Pull 失败

```bash
# 在服务器上手动拉取
cd /opt/redpacket
git stash
git pull origin master
```

#### 3. Docker 构建失败

```bash
# 查看构建日志
docker compose -f docker-compose.production.yml build --no-cache 2>&1 | tee build.log

# 清理缓存
docker system prune -a
```

#### 4. 服务启动失败

```bash
# 查看服务日志
docker compose -f docker-compose.production.yml logs --tail 100

# 检查端口占用
netstat -tlnp | grep -E ':(8000|8080|3001)'
```

---

## 📝 完整配置文件

所有配置文件见下文：

- [GitHub Actions 工作流](#github-actions-工作流文件)
- [Webhook 接收器](#webhook-接收器脚本)
- [自动化部署脚本](#自动化部署脚本)
- [本地触发脚本](#本地触发脚本)

---

## 🎯 最佳实践

1. **使用分支策略**
   - `master` → 生产环境
   - `develop` → 开发环境
   - `staging` → 测试环境

2. **版本标记**
   - 每次部署打标签：`git tag v1.0.0`
   - 使用语义化版本号

3. **数据库迁移**
   - 在部署前备份数据库
   - 使用迁移工具管理数据库变更

4. **零停机部署**
   - 使用蓝绿部署
   - 或使用滚动更新

5. **监控告警**
   - 设置服务健康检查
   - 配置异常告警

---

## 📚 参考资料

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [SSH 密钥配置指南](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

---

## ✅ 部署检查清单

- [ ] GitHub Secrets 已配置
- [ ] SSH 密钥已配置并测试
- [ ] 服务器环境已准备
- [ ] 工作流文件已创建
- [ ] 首次部署已测试
- [ ] 监控告警已配置
- [ ] 回滚方案已测试

---

**最后更新**: 2025-01-15
**维护者**: 开发团队

