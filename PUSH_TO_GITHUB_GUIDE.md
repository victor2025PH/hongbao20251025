# 推送代码到 GitHub 指南

> 将本地代码推送到 GitHub 仓库 `victor2025PH/hongbao20251025`

---

## 🚀 快速推送（已执行）

代码已准备好推送到 GitHub，如果推送失败，请按照以下步骤操作：

---

## 📋 推送步骤

### 方式一：使用 HTTPS + 个人访问令牌（推荐）

**1. 生成个人访问令牌（Personal Access Token）**

- 访问：https://github.com/settings/tokens
- 点击 "Generate new token" → "Generate new token (classic)"
- 设置名称：`redpacket-deploy`
- 选择权限：勾选 `repo`（完整仓库权限）
- 点击 "Generate token"
- **重要：复制生成的令牌（只显示一次）**

**2. 推送代码**

在项目目录执行：

```bash
# 如果还没有初始化 Git
git init
git remote add origin https://github.com/victor2025PH/hongbao20251025.git

# 添加文件
git add .

# 提交
git commit -m "Initial commit: 红包系统管理后台完整代码"

# 推送（使用令牌作为密码）
git push -u origin main
# 用户名: victor2025PH
# 密码: 粘贴您的个人访问令牌
```

---

### 方式二：使用 SSH（如果已配置 SSH 密钥）

```bash
# 更改远程仓库地址为 SSH
git remote set-url origin git@github.com:victor2025PH/hongbao20251025.git

# 推送
git push -u origin main
```

---

### 方式三：使用 GitHub CLI

```bash
# 安装 GitHub CLI（如果还没有）
# Windows: winget install GitHub.cli
# 或下载: https://cli.github.com/

# 登录
gh auth login

# 推送
git push -u origin main
```

---

## ✅ 验证推送成功

推送成功后，访问以下地址确认：

**仓库地址**: https://github.com/victor2025PH/hongbao20251025

您应该能看到：
- ✅ 所有项目文件
- ✅ README.md
- ✅ 所有源代码目录

---

## 🔍 如果推送失败

### 错误 1: "Authentication failed"

**解决方案：**
- 使用个人访问令牌代替密码
- 或配置 SSH 密钥

### 错误 2: "Repository not found"

**解决方案：**
- 确认仓库地址正确
- 确认您有推送权限
- 确认仓库是公开的或您有访问权限

### 错误 3: "Permission denied"

**解决方案：**
- 检查 GitHub 用户名和令牌是否正确
- 确认令牌有 `repo` 权限

---

## 📝 推送后的下一步

代码推送成功后，在服务器上执行：

```bash
# 1. 进入项目目录
cd /opt/redpacket

# 2. 克隆代码
git clone https://github.com/victor2025PH/hongbao20251025.git .

# 3. 开始部署
chmod +x deploy/scripts/deploy_docker_compose.sh
./deploy/scripts/deploy_docker_compose.sh
```

---

## 💡 提示

- **个人访问令牌**比密码更安全，推荐使用
- 令牌生成后请妥善保管，丢失需要重新生成
- 如果仓库是私有的，确保令牌有 `repo` 权限

---

*最后更新: 2025-01-XX*

