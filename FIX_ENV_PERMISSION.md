# 修复 .env.production 文件权限问题

> 解决 "Permission denied" 错误

---

## 🔍 问题

保存 `.env.production` 文件时出现错误：
```
[ Error writing .env.production: Permission denied ]
```

**原因:** 文件可能是 root 用户创建的，当前用户没有写入权限。

---

## ✅ 解决方法

### 方法 1: 修改文件所有者（推荐）

在服务器上执行：

```bash
cd /opt/redpacket

# 将文件所有者改为当前用户
sudo chown $USER:$USER .env.production

# 验证权限
ls -la .env.production
```

然后重新编辑文件：
```bash
nano .env.production
```

现在应该可以正常保存了。

---

### 方法 2: 使用 sudo 编辑

如果方法 1 不行，使用 sudo 编辑：

```bash
cd /opt/redpacket

# 使用 sudo 编辑
sudo nano .env.production
```

**注意:** 使用 sudo 编辑后，记得修改文件所有者：
```bash
sudo chown $USER:$USER .env.production
```

---

### 方法 3: 复制并重新创建

```bash
cd /opt/redpacket

# 备份原文件
sudo cp .env.production .env.production.backup

# 复制到当前用户可写的位置
sudo cp .env.production /tmp/env.production.tmp

# 编辑临时文件
nano /tmp/env.production.tmp

# 保存后，使用 sudo 复制回来
sudo cp /tmp/env.production.tmp .env.production

# 修改所有者
sudo chown $USER:$USER .env.production

# 删除临时文件
rm /tmp/env.production.tmp
```

---

## 🚀 快速修复命令

**一键修复权限（在服务器上执行）:**

```bash
cd /opt/redpacket

# 修复所有配置文件的权限
sudo chown -R $USER:$USER .env.production
sudo chmod 644 .env.production

# 验证
ls -la .env.production
```

然后重新编辑：
```bash
nano .env.production
```

---

## 📝 保存文件

修复权限后，在 nano 编辑器中：

1. **保存文件**: 按 `Ctrl + O`（Write Out）
2. **确认文件名**: 按 `Enter`
3. **退出编辑器**: 按 `Ctrl + X`（Exit）

---

## ✅ 验证

保存后，验证文件：

```bash
# 检查文件权限
ls -la .env.production

# 应该显示类似：
# -rw-r--r-- 1 ubuntu ubuntu 1234 Nov 13 08:00 .env.production
# 所有者应该是您的用户名，不是 root
```

---

## 🔒 安全提示

`.env.production` 文件包含敏感信息，确保：

1. **文件权限**: `644`（所有者可读写，其他人只读）
2. **文件所有者**: 当前用户（不是 root）
3. **不要提交到 Git**: 确保 `.env.production` 在 `.gitignore` 中

---

*最后更新: 2025-01-XX*

