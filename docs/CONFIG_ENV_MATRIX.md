# 环境变量与端口配置矩阵

本文档汇总所有服务使用的环境变量和端口配置，包括 Web Admin、MiniApp API、前端控制台等。

> **注意**: 本文档基于 `config/settings.py`、`web_admin/main.py`、`miniapp/main.py`、`frontend-next/` 的实际代码生成。如有遗漏，请补充。

---

## 目录

- [端口配置](#端口配置)
- [后端环境变量](#后端环境变量)
- [前端环境变量](#前端环境变量)
- [敏感文件关联](#敏感文件关联)
- [配置验证](#配置验证)

---

## 端口配置

| 服务 | 端口 | 入口文件 | 说明 |
|------|------|----------|------|
| **Web Admin** | 8000 | `web_admin/main.py` | FastAPI Web 管理后台（HTML + REST API） |
| **MiniApp API** | 8080 | `miniapp/main.py` | FastAPI MiniApp 后端 API |
| **前端控制台** | 3001 | `frontend-next/` | Next.js 前端控制台 |
| **聊天 AI 前端** | 3000 | `saas-demo/` | Next.js 聊天 AI 控制台（独立项目） |

**启动命令**:
```bash
# Web Admin (8000)
uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --reload

# MiniApp API (8080)
uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --reload

# 前端控制台 (3001)
cd frontend-next && npm run dev
```

---

## 后端环境变量

### 核心配置（必填）

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `BOT_TOKEN` | web_admin, miniapp | ✅ | `123456:ABC-DEF...` | `生产Token` | Telegram Bot Token |
| `DATABASE_URL` | web_admin, miniapp | ✅ | `sqlite:///./data.sqlite` | `postgresql://user:pass@host:5432/db` | 数据库连接串 |
| `ADMIN_IDS` | web_admin, miniapp | ⚠️ | `123456,789012` | `管理员ID列表` | 管理员 Telegram ID（逗号分隔） |
| `SUPER_ADMINS` | web_admin, miniapp | ❌ | `999999` | `超管ID列表` | 超管白名单（逗号分隔） |

### 国际化配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `DEFAULT_LANG` | web_admin, miniapp | ❌ | `zh` | `zh` | 默认语言（默认: zh） |
| `FALLBACK_LANG` | web_admin, miniapp | ❌ | `en` | `en` | 回退语言（默认: en） |
| `TZ` | web_admin, miniapp | ❌ | `Asia/Manila` | `Asia/Manila` | 时区（默认: Asia/Manila） |

### 调试与功能开关

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `DEBUG` | web_admin, miniapp | ❌ | `true` | `false` | 调试模式（默认: true） |
| `ALLOW_RESET` | web_admin | ❌ | `false` | `false` | 是否允许"清零"操作（默认: false） |
| `FLAG_ENABLE_PUBLIC_GROUPS` | web_admin, miniapp | ❌ | `1` | `1` | 启用公开群组功能（1/true/yes/on） |

### 充值配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `RECHARGE_PROVIDER` | web_admin | ❌ | `mock` | `nowpayments` | 充值提供商（mock/nowpayments） |
| `RECHARGE_EXPIRE_MINUTES` | web_admin | ❌ | `60` | `60` | 充值订单过期时间（分钟） |
| `RECHARGE_COIN_USDT` | web_admin | ❌ | `USDTTRC20` | `USDTTRC20` | USDT 币种标识 |
| `RECHARGE_COIN_TON` | web_admin | ❌ | `TON` | `TON` | TON 币种标识 |
| `RECHARGE_ENABLE_TON` | web_admin | ❌ | `true` | `true` | 是否启用 TON 充值入口 |

### NowPayments 配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `NOWPAYMENTS_BASE_URL` | web_admin | ❌ | `https://api.nowpayments.io/v1` | `https://api.nowpayments.io/v1` | NowPayments API 基础地址 |
| `NOWPAYMENTS_API_KEY` | web_admin | ⚠️ | `空字符串` | `生产API密钥` | NowPayments API 密钥（生产必填） |
| `NOWPAYMENTS_IPN_SECRET` | web_admin | ⚠️ | `空字符串` | `生产IPN密钥` | NowPayments IPN 密钥（生产必填） |
| `NOWPAYMENTS_IPN_URL` | web_admin | ⚠️ | `空字符串` | `https://yourdomain.com/admin/ipn` | NowPayments IPN 回调地址（生产必填） |
| `NP_PAY_COIN_USDT` | web_admin | ❌ | `usdttrc20` | `usdttrc20` | NowPayments USDT 币种（小写） |
| `NP_PAY_COIN_TON` | web_admin | ❌ | `ton` | `ton` | NowPayments TON 币种（小写） |

### AI 配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `AI_PROVIDER` | web_admin | ❌ | `openai` | `openai` | AI 提供商（openai/openrouter） |
| `AI_TIMEOUT` | web_admin | ❌ | `20` | `20` | AI 请求超时（秒） |
| `AI_MAX_TOKENS` | web_admin | ❌ | `500` | `500` | AI 最大 Token 数 |
| `OPENAI_API_KEY` | web_admin | ⚠️ | `空字符串` | `sk-...` | OpenAI API 密钥（使用 OpenAI 时必填） |
| `OPENAI_MODEL` | web_admin | ❌ | `gpt-4o-mini` | `gpt-4o-mini` | OpenAI 模型名称 |
| `OPENROUTER_API_KEY` | web_admin | ⚠️ | `空字符串` | `sk-or-...` | OpenRouter API 密钥（使用 OpenRouter 时必填） |
| `OPENROUTER_MODEL` | web_admin | ❌ | `openai/gpt-4o-mini` | `openai/gpt-4o-mini` | OpenRouter 模型名称 |

### 封面配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `HB_COVER_CHANNEL_ID` | web_admin | ❌ | `空字符串` | `-1001234567890` | 红包封面频道 ID（整数） |

### MiniApp JWT 配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `MINIAPP_JWT_SECRET` | miniapp | ⚠️ | `change_me` | `强随机字符串` | JWT 签名密钥（生产必须修改） |
| `MINIAPP_JWT_ISSUER` | miniapp | ❌ | `miniapp` | `miniapp` | JWT 发行者（默认: miniapp） |
| `MINIAPP_JWT_EXPIRE_SECONDS` | miniapp | ❌ | `7200` | `7200` | JWT 过期时间（秒，默认: 7200） |
| `TELEGRAM_CLIENT_ID` | miniapp | ⚠️ | `空字符串` | `Telegram客户端ID` | Telegram 客户端 ID（用于验证 initData） |

### Web Admin 会话配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `ADMIN_SESSION_SECRET` | web_admin | ⚠️ | `dev_secret` | `强随机字符串` | 会话密钥（生产必须修改） |

### Web Admin 静态文件与模板配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `STATIC_DIR` | web_admin | ❌ | `static` | `static` | 静态文件目录（默认: static） |
| `TEMPLATE_DIR` | web_admin | ❌ | `templates` | `templates` | 模板目录（默认: templates） |
| `FILES_DIR` | web_admin | ❌ | `static/uploads` | `static/uploads` | 文件下载/导出目录 |

### Web Admin 安全响应头配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `ADMIN_CSP` | web_admin | ❌ | `默认CSP策略` | `自定义CSP` | Content-Security-Policy（默认较宽松） |
| `REFERRER_POLICY` | web_admin | ❌ | `no-referrer` | `no-referrer` | Referrer Policy |
| `X_FRAME_OPTIONS` | web_admin | ❌ | `DENY` | `DENY` | X-Frame-Options |
| `X_CONTENT_TYPE_OPTIONS` | web_admin | ❌ | `nosniff` | `nosniff` | X-Content-Type-Options |
| `PERMISSIONS_POLICY` | web_admin | ❌ | `geolocation=(), microphone=(), camera=()` | `同上` | Permissions Policy |
| `ENABLE_HSTS` | web_admin | ❌ | `0` | `1` | 是否启用 HSTS（HTTPS 环境设为 1） |

### Web Admin 压缩配置

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `GZIP_MIN_SIZE` | web_admin | ❌ | `1024` | `1024` | GZip 压缩最小文件大小（字节） |

---

## 前端环境变量

### Next.js 前端控制台（frontend-next）

| 变量名 | 作用范围 | 必填 | 本地示例值 | 生产示例值 | 说明 |
|--------|----------|------|------------|------------|------|
| `NEXT_PUBLIC_ADMIN_API_BASE_URL` | frontend-next | ❌ | `http://localhost:8000` | `https://api.yourdomain.com` | Web Admin API 基础地址 |
| `NEXT_PUBLIC_MINIAPP_API_BASE_URL` | frontend-next | ❌ | `http://localhost:8080` | `https://miniapp-api.yourdomain.com` | MiniApp API 基础地址 |
| `NEXT_PUBLIC_API_BASE_URL` | frontend-next | ❌ | `http://localhost:8000/api` | `https://api.yourdomain.com/api` | 通用 API 基础地址（向后兼容） |
| `NEXT_PUBLIC_DEV_USERNAME` | frontend-next | ❌ | `admin` | `不设置` | 开发环境用户名（仅开发用） |
| `NEXT_PUBLIC_DEV_PASSWORD` | frontend-next | ❌ | `admin123` | `不设置` | 开发环境密码（仅开发用） |
| `NEXT_PUBLIC_DEV_TG_ID` | frontend-next | ❌ | `123456` | `不设置` | 开发环境 Telegram ID（仅开发用） |
| `NEXT_PUBLIC_DEFAULT_LANG` | frontend-next | ❌ | `zh` | `zh` | 默认语言 |
| `NEXT_PUBLIC_ENABLE_DEVTOOLS` | frontend-next | ❌ | `false` | `false` | 是否启用 React Query Devtools（开发用） |

**配置方式**:
- 在 `frontend-next/.env.local` 或 `.env` 中设置
- 或在 `next.config.ts` 中通过 `env` 字段配置

---

## 敏感文件关联

### secrets/ 目录

| 文件 | 关联环境变量 | 说明 |
|------|-------------|------|
| `secrets/service_account.json` | 无（直接读取文件） | Google Service Account 密钥（用于 Google Sheet 同步） |

**注意**:
- `secrets/` 目录不应提交到 Git
- 生产环境需要手动部署此文件
- 文件权限应设置为 `600`（仅所有者可读）

### 其他敏感配置

| 配置项 | 存储位置 | 说明 |
|--------|----------|------|
| `BOT_TOKEN` | 环境变量 | Telegram Bot Token（不应硬编码） |
| `NOWPAYMENTS_API_KEY` | 环境变量 | NowPayments API 密钥（不应硬编码） |
| `NOWPAYMENTS_IPN_SECRET` | 环境变量 | NowPayments IPN 密钥（不应硬编码） |
| `OPENAI_API_KEY` | 环境变量 | OpenAI API 密钥（不应硬编码） |
| `OPENROUTER_API_KEY` | 环境变量 | OpenRouter API 密钥（不应硬编码） |
| `MINIAPP_JWT_SECRET` | 环境变量 | JWT 签名密钥（不应硬编码） |
| `ADMIN_SESSION_SECRET` | 环境变量 | Web Admin 会话密钥（不应硬编码） |

---

## 配置验证

### 使用 check_env.py 验证

```bash
# 检查 .env.example 是否包含所有必需的环境变量
python scripts/check_env.py
```

**退出码**:
- `0`: 所有必需键都存在
- `1`: 缺少必需键或检测到重复键
- `2`: 解析配置文件失败

### 使用 self_check.py 验证

```bash
# 运行完整自检（包括环境检查、健康检查、测试）
python scripts/self_check.py
```

**功能**:
- 检查环境变量
- 启动 Web Admin 服务并验证 `/healthz`
- 运行关键测试用例
- 运行活动报告脚本

### 手动验证步骤

1. **检查必需环境变量**:
   ```bash
   # 检查 BOT_TOKEN
   echo $BOT_TOKEN
   
   # 检查 DATABASE_URL
   echo $DATABASE_URL
   ```

2. **验证数据库连接**:
   ```bash
   python -c "from models.db import engine; engine.connect(); print('✅ DB OK')"
   ```

3. **验证服务健康**:
   ```bash
   # Web Admin
   curl http://localhost:8000/healthz
   
   # MiniApp API
   curl http://localhost:8080/healthz
   ```

---

## 生产环境部署建议

### 环境变量管理

1. **使用 `.env` 文件**（不提交到 Git）:
   ```bash
   # 生产环境
   cp .env.example .env.production
   # 编辑 .env.production，填入真实值
   ```

2. **使用环境变量注入**（Docker/K8s）:
   ```yaml
   # docker-compose.yml 示例
   environment:
     - BOT_TOKEN=${BOT_TOKEN}
     - DATABASE_URL=${DATABASE_URL}
     - ADMIN_IDS=${ADMIN_IDS}
   ```

3. **使用密钥管理服务**（AWS Secrets Manager、HashiCorp Vault 等）:
   - 生产环境建议使用专业的密钥管理服务
   - 避免在代码、日志、配置文件中暴露敏感信息

### 安全建议

1. **修改默认密钥**:
   - `MINIAPP_JWT_SECRET`: 必须修改为强随机字符串
   - `ADMIN_SESSION_SECRET`: 必须修改为强随机字符串

2. **启用 HTTPS**:
   - 设置 `ENABLE_HSTS=1`
   - 配置反向代理（Nginx/Caddy）处理 HTTPS

3. **限制管理员访问**:
   - 通过 `ADMIN_IDS` 和 `SUPER_ADMINS` 严格控制管理员列表
   - 定期审查管理员权限

4. **数据库安全**:
   - 使用强密码
   - 限制数据库访问 IP
   - 定期备份

---

## TODO

- [ ] 补充 `.env.example` 文件，包含所有环境变量的示例值
- [ ] 添加环境变量验证脚本，在启动时检查必需变量
- [ ] 添加环境变量文档生成脚本，自动从 `config/settings.py` 提取变量说明
- [ ] 补充 Docker Compose 配置示例
- [ ] 补充 Kubernetes ConfigMap/Secret 配置示例

---

*最后更新: 2025-01-XX*

