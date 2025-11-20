# 部署方案状态与测试检查指南

> 当前进度、测试步骤和检查清单

---

## 📊 当前进度状态

### ✅ 已完成的工作

1. **文档创建** ✅
   - [x] 完整方案文档 (`docs/AUTO_DEPLOY_COMPLETE_GUIDE.md`)
   - [x] 快速开始指南 (`docs/AUTO_DEPLOY_QUICK_START.md`)
   - [x] 本文档（状态与测试指南）

2. **GitHub Actions 工作流** ✅
   - [x] `.github/workflows/deploy.yml` - 自动部署工作流

3. **部署脚本** ✅
   - [x] `deploy/scripts/auto_deploy_pipeline.sh` - 自动化部署
   - [x] `deploy/scripts/setup_auto_deploy.sh` - 环境设置
   - [x] `deploy/scripts/deploy_with_rollback.sh` - 带回滚部署
   - [x] `deploy/scripts/webhook_receiver.py` - Webhook 接收器
   - [x] `deploy/scripts/monitor_deployment.sh` - 监控脚本

4. **配置文件** ✅
   - [x] `Makefile` - 部署命令封装

---

## 🔍 当前阶段：配置与测试

### 步骤 1: 检查文件是否齐全

运行以下命令检查所有文件是否存在：

```bash
# 检查文档
ls -la docs/AUTO_DEPLOY*.md

# 检查 GitHub Actions
ls -la .github/workflows/deploy.yml

# 检查部署脚本
ls -la deploy/scripts/auto_deploy*.sh
ls -la deploy/scripts/setup_auto_deploy.sh
ls -la deploy/scripts/webhook_receiver.py
```

**预期输出**：所有文件都应存在

---

### 步骤 2: 验证脚本权限（在服务器上）

如果脚本需要执行权限，在服务器上运行：

```bash
chmod +x deploy/scripts/*.sh
chmod +x deploy/scripts/*.py
```

---

### 步骤 3: 选择并配置部署方案

根据你的需求选择一个方案：

#### 方案 A: GitHub Actions（推荐）

**配置检查清单**：

- [ ] SSH 密钥已生成
  ```bash
  # 检查密钥是否存在
  ls -la ~/.ssh/deploy_key
  ```
  
- [ ] 服务器 SSH 公钥已配置
  ```bash
  # 在服务器上检查
  cat ~/.ssh/authorized_keys | grep deploy
  ```
  
- [ ] GitHub Secrets 已配置
  - 进入仓库 → `Settings` → `Secrets and variables` → `Actions`
  - 检查以下 Secrets 是否存在：
    - [ ] `DEPLOY_HOST`
    - [ ] `DEPLOY_USER`
    - [ ] `DEPLOY_SSH_KEY`
    - [ ] `DEPLOY_PORT`（可选）
    - [ ] `DEPLOY_PATH`（可选）

**测试 SSH 连接**：

```bash
# 在本地测试
ssh -i ~/.ssh/deploy_key -p 22 ubuntu@你的服务器IP "echo 'SSH 连接成功'"
```

**测试 GitHub Actions**：

1. 提交并推送测试代码：
   ```bash
   git add .
   git commit -m "test: 测试自动部署"
   git push origin master
   ```

2. 检查 GitHub Actions：
   - 进入仓库 → `Actions` 标签
   - 查看 "自动部署到生产服务器" 工作流
   - 确认执行状态为绿色 ✅

---

#### 方案 B: 本地脚本部署

**配置检查清单**：

- [ ] 环境设置脚本已运行
  ```bash
  # 运行环境设置（首次使用）
  make setup
  # 或
  bash deploy/scripts/setup_auto_deploy.sh
  ```

- [ ] 配置文件已创建
  ```bash
  # 检查配置文件
  cat .env.deploy
  ```

**测试部署**：

```bash
# 方式 1: 使用 Makefile
make deploy

# 方式 2: 直接运行脚本
bash deploy/scripts/auto_deploy_pipeline.sh 服务器IP 用户名

# 方式 3: 快速部署（推荐）
make quick-deploy
```

---

#### 方案 C: Webhook 自动化

**配置检查清单**：

- [ ] Python 依赖已安装
  ```bash
  pip install flask requests
  ```

- [ ] Webhook 服务已启动
  ```bash
  # 直接运行
  python deploy/scripts/webhook_receiver.py
  
  # 或使用 systemd（推荐）
  sudo systemctl status webhook-receiver
  ```

- [ ] GitHub Webhook 已配置
  - 进入仓库 → `Settings` → `Webhooks` → `Add webhook`
  - 检查配置是否正确

**测试 Webhook**：

```bash
# 测试 Webhook 端点
curl http://服务器IP:8080/webhook/deploy

# 或查看日志
tail -f /opt/redpacket/logs/webhook.log
```

---

## 🧪 测试步骤

### 测试 1: SSH 连接测试

```bash
# 在本地执行
make test-ssh

# 或手动测试
ssh -i ~/.ssh/deploy_key -p 22 ubuntu@服务器IP "echo 'SSH 连接成功' && uname -a"
```

**预期结果**：
- ✅ SSH 连接成功
- ✅ 显示服务器系统信息

---

### 测试 2: 环境检查测试

```bash
# 在本地执行
make check-env
```

**预期结果**：
- ✅ Git 已安装
- ✅ SSH 已安装
- ⚠️ Docker 可选（本地不需要）

---

### 测试 3: 服务器状态检查

```bash
# 在服务器上执行
cd /opt/redpacket

# 检查 Docker
docker --version
docker compose version

# 检查 Git
git --version

# 检查项目目录
ls -la

# 检查环境变量文件
ls -la .env.production
```

**预期结果**：
- ✅ Docker 和 Docker Compose 已安装
- ✅ Git 已安装
- ✅ 项目目录存在
- ✅ `.env.production` 文件存在

---

### 测试 4: 部署流程测试

#### 方式 A: 使用 Makefile（推荐）

```bash
# 完整测试流程
make quick-deploy
```

这会自动执行：
1. 环境检查
2. SSH 连接测试
3. 部署执行

#### 方式 B: 手动测试

```bash
# 1. 检查环境
make check-env

# 2. 测试 SSH
make test-ssh

# 3. 执行部署
make deploy

# 4. 查看状态
make status

# 5. 查看日志
make logs
```

---

### 测试 5: 健康检查测试

在服务器上执行：

```bash
# 检查 Web Admin
curl http://127.0.0.1:8000/healthz

# 检查 MiniApp API
curl http://127.0.0.1:8080/healthz

# 检查 Frontend
curl http://127.0.0.1:3001

# 检查所有服务状态
docker compose -f docker-compose.production.yml ps
```

**预期结果**：
- ✅ 所有健康检查返回成功
- ✅ 所有服务状态为 `Up` 或 `healthy`

---

### 测试 6: GitHub Actions 工作流测试

1. **触发部署**：
   ```bash
   git add .
   git commit -m "test: 测试 GitHub Actions 自动部署"
   git push origin master
   ```

2. **查看执行状态**：
   - 进入 GitHub 仓库
   - 点击 `Actions` 标签
   - 查看 "自动部署到生产服务器" 工作流
   - 点击最新运行查看详细日志

3. **验证部署结果**：
   ```bash
   # 在服务器上检查
   make status
   # 或
   ssh -i ~/.ssh/deploy_key ubuntu@服务器IP \
     "cd /opt/redpacket && docker compose -f docker-compose.production.yml ps"
   ```

**预期结果**：
- ✅ GitHub Actions 执行成功（绿色 ✅）
- ✅ 服务器服务正常运行
- ✅ 健康检查通过

---

## ✅ 完整检查清单

### 配置阶段

- [ ] 已选择部署方案（GitHub Actions / 本地脚本 / Webhook）
- [ ] SSH 密钥已生成并配置
- [ ] 服务器 SSH 连接测试通过
- [ ] 环境设置脚本已运行（如果使用本地脚本）
- [ ] GitHub Secrets 已配置（如果使用 GitHub Actions）
- [ ] Webhook 已配置（如果使用 Webhook）

### 测试阶段

- [ ] SSH 连接测试通过
- [ ] 环境检查测试通过
- [ ] 服务器状态检查通过
- [ ] 部署流程测试通过
- [ ] 健康检查测试通过
- [ ] GitHub Actions 测试通过（如果使用）

### 验证阶段

- [ ] 服务状态正常
- [ ] 健康检查通过
- [ ] 日志无错误
- [ ] 功能测试通过

---

## 🔧 故障排除

### 问题 1: SSH 连接失败

**检查步骤**：
```bash
# 1. 检查密钥权限
ls -l ~/.ssh/deploy_key
# 应该是 600 权限

# 2. 测试连接（详细模式）
ssh -v -i ~/.ssh/deploy_key -p 22 ubuntu@服务器IP

# 3. 检查服务器 SSH 服务
ssh 服务器IP "sudo systemctl status sshd"
```

**解决方案**：
- 确保密钥权限正确：`chmod 600 ~/.ssh/deploy_key`
- 检查服务器防火墙是否开放 SSH 端口
- 验证公钥是否正确添加到服务器

---

### 问题 2: GitHub Actions 执行失败

**检查步骤**：
1. 查看 GitHub Actions 日志
2. 检查 Secrets 配置是否正确
3. 验证 SSH 连接是否正常

**常见原因**：
- Secrets 配置错误
- SSH 密钥格式不正确
- 服务器不可访问

---

### 问题 3: 部署后服务未启动

**检查步骤**：
```bash
# 1. 查看服务状态
docker compose -f docker-compose.production.yml ps

# 2. 查看日志
docker compose -f docker-compose.production.yml logs --tail 100

# 3. 检查环境变量
cat .env.production
```

**解决方案**：
- 检查 `.env.production` 配置是否正确
- 查看 Docker 日志排查错误
- 确保端口未被占用

---

## 📝 下一步操作

根据你的选择：

### 如果选择 GitHub Actions：

1. ✅ 配置 GitHub Secrets
2. ✅ 测试 SSH 连接
3. ✅ 推送代码测试自动部署
4. ✅ 查看 GitHub Actions 执行结果

### 如果选择本地脚本：

1. ✅ 运行 `make setup` 配置环境
2. ✅ 测试 `make deploy`
3. ✅ 验证部署结果

### 如果选择 Webhook：

1. ✅ 启动 Webhook 接收器
2. ✅ 配置 GitHub Webhook
3. ✅ 推送代码测试自动触发

---

## 🎯 快速测试命令

```bash
# 一键测试所有功能
make check-env && make test-ssh && make deploy && make status

# 或使用快速部署（包含所有测试）
make quick-deploy
```

---

## 📞 需要帮助？

- 查看完整文档：`docs/AUTO_DEPLOY_COMPLETE_GUIDE.md`
- 查看快速开始：`docs/AUTO_DEPLOY_QUICK_START.md`
- 检查日志文件：`/opt/redpacket/logs/deploy.log`

---

**最后更新**: 2025-01-15

