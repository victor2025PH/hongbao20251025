# 自动化部署快速开始指南

> 5 分钟快速配置自动化部署

---

## 🚀 三种部署方案快速对比

| 方案 | 配置时间 | 适用场景 | 推荐度 |
|------|----------|----------|--------|
| **GitHub Actions** | 5 分钟 | 开源/私有仓库，云端执行 | ⭐⭐⭐⭐⭐ |
| **本地脚本** | 2 分钟 | 本地控制，单次部署 | ⭐⭐⭐⭐ |
| **Webhook** | 10 分钟 | 需要本地服务器运行 | ⭐⭐⭐ |

---

## ⚡ 方案一：GitHub Actions（推荐 - 5分钟配置）

### 第 1 步：生成 SSH 密钥

```bash
# 在本地执行
ssh-keygen -t rsa -b 4096 -C "deploy@redpacket" -f ~/.ssh/deploy_key -N ""
```

### 第 2 步：配置服务器公钥

```bash
# 复制公钥内容
cat ~/.ssh/deploy_key.pub

# 在服务器上执行
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "粘贴你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 第 3 步：配置 GitHub Secrets

1. 进入仓库 → `Settings` → `Secrets and variables` → `Actions`
2. 添加以下 Secrets：

```
DEPLOY_HOST=165.154.233.55
DEPLOY_USER=ubuntu
DEPLOY_PORT=22
DEPLOY_PATH=/opt/redpacket
DEPLOY_SSH_KEY=<复制 ~/.ssh/deploy_key 的完整内容>
```

### 第 4 步：测试部署

```bash
# 推送代码到 master 分支
git add .
git commit -m "test: 测试自动部署"
git push origin master
```

✅ **完成！** 代码推送后会自动部署，可在 GitHub Actions 页面查看进度。

---

## 🔧 方案二：本地脚本部署（2分钟配置）

### 第 1 步：运行环境设置

```bash
# 在本地执行
make setup
# 或
bash deploy/scripts/setup_auto_deploy.sh
```

### 第 2 步：执行部署

```bash
# 方式 1: 使用 Makefile
make deploy

# 方式 2: 直接运行脚本
bash deploy/scripts/auto_deploy_pipeline.sh <服务器IP> <用户名>

# 方式 3: 快速部署（检查 + 测试 + 部署）
make quick-deploy
```

✅ **完成！** 部署会自动执行。

---

## 🔔 方案三：Webhook 自动化（10分钟配置）

### 第 1 步：安装依赖

```bash
pip install flask requests
```

### 第 2 步：在服务器上启动 Webhook 接收器

```bash
# 方式 1: 直接运行
python deploy/scripts/webhook_receiver.py

# 方式 2: 使用 systemd 服务（推荐）
sudo cp deploy/systemd/webhook-receiver.service /etc/systemd/system/
sudo systemctl enable webhook-receiver
sudo systemctl start webhook-receiver
```

### 第 3 步：配置 GitHub Webhook

1. 进入仓库 → `Settings` → `Webhooks` → `Add webhook`
2. 配置：
   - **Payload URL**: `http://your-server-ip:8080/webhook/deploy`
   - **Content type**: `application/json`
   - **Secret**: 生成随机密钥（见下方）
   - **Events**: 选择 `Just the push event`

### 第 4 步：设置 Webhook Secret

```bash
# 生成密钥
openssl rand -hex 32

# 在服务器上设置环境变量
export WEBHOOK_SECRET="生成的密钥"

# 或在 systemd 服务中配置
sudo nano /etc/systemd/system/webhook-receiver.service
# 添加: Environment="WEBHOOK_SECRET=你的密钥"
```

✅ **完成！** 推送代码到 master 分支会自动触发部署。

---

## 🎯 常用命令

### 使用 Makefile

```bash
make help          # 查看所有命令
make setup         # 设置环境
make deploy        # 部署到生产
make test-ssh      # 测试 SSH 连接
make status        # 查看服务状态
make logs          # 查看日志
make quick-deploy  # 快速部署
```

### 直接使用脚本

```bash
# 带自动回滚的部署
bash deploy/scripts/deploy_with_rollback.sh

# 监控部署
bash deploy/scripts/monitor_deployment.sh

# 手动触发部署
bash deploy/scripts/auto_deploy_pipeline.sh
```

---

## 📋 部署检查清单

### 首次部署前

- [ ] 服务器已安装 Docker 和 Docker Compose
- [ ] 服务器已安装 Git
- [ ] SSH 密钥已配置并测试
- [ ] `.env.production` 文件已配置
- [ ] GitHub Secrets 已配置（如果使用 GitHub Actions）

### 部署后验证

- [ ] 服务状态正常：`docker compose ps`
- [ ] 健康检查通过：`curl http://127.0.0.1:8000/healthz`
- [ ] 日志无错误：`docker compose logs --tail 100`
- [ ] 功能测试通过

---

## 🐛 常见问题

### 1. SSH 连接失败

```bash
# 测试连接
ssh -i ~/.ssh/deploy_key ubuntu@服务器IP

# 检查密钥权限
chmod 600 ~/.ssh/deploy_key
```

### 2. GitHub Actions 部署失败

- 检查 GitHub Secrets 是否配置正确
- 查看 Actions 日志排查问题
- 确认服务器 SSH 端口是否正确

### 3. Webhook 接收不到请求

```bash
# 检查 Webhook 服务状态
systemctl status webhook-receiver

# 查看日志
tail -f /opt/redpacket/logs/webhook.log

# 测试 Webhook
curl http://127.0.0.1:8080/webhook/deploy
```

---

## 📚 详细文档

- [完整方案文档](./AUTO_DEPLOY_COMPLETE_GUIDE.md) - 详细的配置说明和高级功能
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Compose 文档](https://docs.docker.com/compose/)

---

## 🎉 开始使用

推荐从 **GitHub Actions** 方案开始，这是最简单、最可靠的自动化部署方式。

```bash
# 1. 配置 SSH 密钥和 GitHub Secrets（见上方）
# 2. 推送代码
git push origin master
# 3. 完成！部署会自动执行
```

---

**有问题？** 查看 [完整方案文档](./AUTO_DEPLOY_COMPLETE_GUIDE.md) 或提交 Issue。

