# 推送代码到 GitHub - 详细步骤

> 仓库地址: https://github.com/victor2025PH/hongbao20251025

---

## ✅ 已完成的操作

1. ✅ Git 仓库已初始化
2. ✅ 远程仓库已配置: `https://github.com/victor2025PH/hongbao20251025.git`
3. ✅ 所有文件已添加到 Git（231 个文件）
4. ✅ 代码已提交（提交信息: "Initial commit: 红包系统管理后台完整代码"）

---

## 🚀 现在需要推送代码

### 步骤 1: 生成个人访问令牌（Personal Access Token）

**这是必需的，因为 GitHub 不再支持密码认证！**

1. **访问 GitHub 令牌设置页面:**
   - 打开: https://github.com/settings/tokens
   - 或: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **生成新令牌:**
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 设置名称: `redpacket-deploy`
   - 设置过期时间: 根据需要选择（建议 90 天或 No expiration）
   - **选择权限**: 勾选 `repo`（完整仓库权限）
   - 点击 "Generate token"

3. **复制令牌:**
   - **重要**: 令牌只显示一次，请立即复制保存！
   - 格式类似: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

### 步骤 2: 推送代码

**在项目目录执行以下命令:**

```bash
# 推送代码（当前分支是 master）
git push -u origin master
```

**当提示输入时:**
- **Username**: `victor2025PH`
- **Password**: 粘贴您刚才复制的个人访问令牌（不是 GitHub 密码！）

---

### 步骤 3: 验证推送成功

推送成功后，访问以下地址确认：

**仓库地址**: https://github.com/victor2025PH/hongbao20251025

您应该能看到：
- ✅ 所有项目文件
- ✅ README.md
- ✅ 所有源代码目录（web_admin, frontend-next, models, services 等）

---

## 🔄 如果推送失败

### 错误 1: "Authentication failed"

**原因**: 使用了错误的密码或令牌

**解决方案**:
- 确认使用的是**个人访问令牌**，不是 GitHub 密码
- 确认令牌有 `repo` 权限
- 重新生成令牌并重试

### 错误 2: "Repository not found"

**原因**: 仓库不存在或没有权限

**解决方案**:
- 确认仓库地址正确: `https://github.com/victor2025PH/hongbao20251025.git`
- 确认您有推送权限
- 确认仓库是公开的或您有访问权限

### 错误 3: "Permission denied"

**原因**: 令牌权限不足

**解决方案**:
- 重新生成令牌，确保勾选了 `repo` 权限
- 确认令牌未过期

---

## 💡 替代方案

### 方案 A: 使用 GitHub CLI（如果已安装）

```bash
# 安装 GitHub CLI（如果还没有）
# Windows: winget install GitHub.cli

# 登录
gh auth login

# 推送
git push -u origin master
```

### 方案 B: 使用 SSH（如果已配置 SSH 密钥）

```bash
# 更改远程仓库地址为 SSH
git remote set-url origin git@github.com:victor2025PH/hongbao20251025.git

# 推送
git push -u origin master
```

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

## ✅ 快速命令清单

**在本地项目目录执行:**

```bash
# 1. 生成个人访问令牌（在浏览器中）
# 访问: https://github.com/settings/tokens
# 生成令牌并复制

# 2. 推送代码
git push -u origin master
# 用户名: victor2025PH
# 密码: 粘贴个人访问令牌

# 3. 验证
# 访问: https://github.com/victor2025PH/hongbao20251025
```

---

*最后更新: 2025-01-XX*

