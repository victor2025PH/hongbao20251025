# .env.production 配置指南

> 详细说明如何配置生产环境变量文件

---

## 🔑 必填配置项（必须修改）

### 1. 核心配置

```bash
# Telegram Bot Token（从 @BotFather 获取）
BOT_TOKEN=你的Telegram_Bot_Token

# 管理员 Telegram ID（您的用户ID，多个用逗号分隔）
ADMIN_IDS=123456789,987654321

# 超级管理员（可选，用于特殊权限）
SUPER_ADMINS=123456789
```

**如何获取：**
- Bot Token: 在 Telegram 中搜索 `@BotFather`，发送 `/newbot` 创建机器人，获取 Token
- Admin IDs: 在 Telegram 中搜索 `@userinfobot`，发送任意消息获取您的 ID

---

### 2. 数据库配置

```bash
# 数据库用户
POSTGRES_USER=redpacket

# 数据库密码（必须修改！至少16位，包含大小写字母、数字、特殊字符）
POSTGRES_PASSWORD=YourStrongPassword123!

# 数据库名称
POSTGRES_DB=redpacket

# 数据库连接 URL（会自动使用上面的配置）
DATABASE_URL=postgresql+psycopg2://redpacket:YourStrongPassword123!@db:5432/redpacket
```

**生成强密码的方法：**
```bash
# 在服务器上运行
openssl rand -base64 24
```

---

### 3. 安全配置（必须修改！）

```bash
# MiniApp JWT 密钥（至少32位随机字符串）
MINIAPP_JWT_SECRET=生成的64位十六进制字符串

# Admin Session 密钥（至少32位随机字符串）
ADMIN_SESSION_SECRET=生成的64位十六进制字符串
```

**生成随机密钥：**
```bash
# 在服务器上运行（生成64位十六进制字符串）
openssl rand -hex 32

# 运行两次，分别用于 MINIAPP_JWT_SECRET 和 ADMIN_SESSION_SECRET
```

**示例输出：**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

---

## 💰 支付配置（如果使用充值功能）

### NowPayments 配置

```bash
# NowPayments API 基础 URL
NOWPAYMENTS_BASE_URL=https://api.nowpayments.io/v1

# NowPayments API 密钥（从 NowPayments 后台获取）
NOWPAYMENTS_API_KEY=你的NowPayments_API密钥

# NowPayments IPN 密钥（从 NowPayments 后台获取）
NOWPAYMENTS_IPN_SECRET=你的NowPayments_IPN密钥

# IPN 回调 URL（您的域名 + /admin/ipn）
NOWPAYMENTS_IPN_URL=https://yourdomain.com/admin/ipn
```

**如何获取：**
1. 注册 NowPayments 账号：https://nowpayments.io
2. 在后台获取 API Key 和 IPN Secret
3. 配置 IPN URL 为：`https://您的域名/admin/ipn`

---

## 🤖 AI 配置（可选）

### 如果使用 OpenAI

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=你的OpenAI_API密钥
OPENAI_MODEL=gpt-4o-mini
```

### 如果使用 OpenRouter

```bash
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=你的OpenRouter_API密钥
OPENROUTER_MODEL=openai/gpt-4o-mini
```

**如何获取：**
- OpenAI: https://platform.openai.com/api-keys
- OpenRouter: https://openrouter.ai/keys

---

## 📱 MiniApp 配置

```bash
# MiniApp JWT 配置
MINIAPP_JWT_ISSUER=miniapp
MINIAPP_JWT_EXPIRE_SECONDS=7200

# Telegram Client ID（可选，用于 MiniApp 认证）
TELEGRAM_CLIENT_ID=你的Telegram客户端ID
```

---

## 🌍 其他配置（可选）

### 国际化

```bash
DEFAULT_LANG=zh          # 默认语言：中文
FALLBACK_LANG=en        # 备用语言：英文
TZ=Asia/Manila          # 时区
```

### 调试和功能开关

```bash
DEBUG=false             # 生产环境设为 false
ALLOW_RESET=false       # 是否允许重置功能
FLAG_ENABLE_PUBLIC_GROUPS=1  # 是否启用公开群组功能
```

### 充值配置

```bash
RECHARGE_PROVIDER=nowpayments
RECHARGE_EXPIRE_MINUTES=60
RECHARGE_COIN_USDT=USDTTRC20
RECHARGE_COIN_TON=TON
RECHARGE_ENABLE_TON=true
```

---

## 📝 配置步骤

### 在 nano 编辑器中：

1. **编辑必填项**：
   - 找到 `BOT_TOKEN=`，替换为您的 Bot Token
   - 找到 `ADMIN_IDS=`，替换为您的 Telegram ID
   - 找到 `POSTGRES_PASSWORD=`，替换为强密码
   - 找到 `MINIAPP_JWT_SECRET=`，替换为生成的密钥
   - 找到 `ADMIN_SESSION_SECRET=`，替换为生成的密钥

2. **保存文件**：
   - 按 `Ctrl + O`（Write Out）
   - 按 `Enter` 确认
   - 按 `Ctrl + X`（Exit）

3. **生成随机密钥**（在另一个终端）：
   ```bash
   # 打开新终端，SSH 连接到服务器
   openssl rand -hex 32  # 用于 MINIAPP_JWT_SECRET
   openssl rand -hex 32  # 用于 ADMIN_SESSION_SECRET
   ```
   然后复制生成的字符串到配置文件中。

---

## ✅ 配置检查清单

配置完成后，检查以下项：

- [ ] `BOT_TOKEN` 已填写
- [ ] `ADMIN_IDS` 已填写（您的 Telegram ID）
- [ ] `POSTGRES_PASSWORD` 已修改为强密码（至少16位）
- [ ] `MINIAPP_JWT_SECRET` 已生成并填写（64位十六进制）
- [ ] `ADMIN_SESSION_SECRET` 已生成并填写（64位十六进制）
- [ ] 如果使用支付功能，`NOWPAYMENTS_API_KEY` 和 `NOWPAYMENTS_IPN_SECRET` 已填写
- [ ] 如果使用 AI 功能，相应的 API Key 已填写

---

## 🚨 安全提示

1. **不要提交 `.env.production` 到 Git**
2. **使用强密码**（至少16位，包含大小写字母、数字、特殊字符）
3. **定期更换密钥**（特别是 JWT 和 Session 密钥）
4. **备份配置文件**（但不要放在公开位置）

---

## 💡 快速配置模板

最小化配置（仅必填项）：

```bash
# 核心配置
BOT_TOKEN=你的BotToken
ADMIN_IDS=你的TelegramID

# 数据库
POSTGRES_PASSWORD=强密码至少16位

# 安全密钥（运行 openssl rand -hex 32 生成）
MINIAPP_JWT_SECRET=生成的64位字符串
ADMIN_SESSION_SECRET=生成的64位字符串

# 其他保持默认即可
```

---

*最后更新: 2025-01-XX*

