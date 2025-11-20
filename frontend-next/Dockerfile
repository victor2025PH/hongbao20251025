# 前端 Dockerfile（Next.js）
FROM node:20-alpine AS base

# 安装依赖阶段
FROM base AS deps
WORKDIR /app

# 复制 package 文件
COPY package.json package-lock.json* ./
RUN npm ci

# 构建阶段
FROM base AS builder
WORKDIR /app

# 复制依赖
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 设置环境变量（构建时）
# ⚠️ 重要：NEXT_PUBLIC_* 变量必须在构建时注入
ARG NEXT_PUBLIC_ADMIN_API_BASE_URL
ARG NEXT_PUBLIC_MINIAPP_API_BASE_URL
ARG NEXT_PUBLIC_API_BASE_URL
ARG NEXT_PUBLIC_DEFAULT_LANG
ARG NEXT_PUBLIC_ENABLE_DEVTOOLS
ARG NEXT_PUBLIC_ADMIN_WEB_USER
ARG NEXT_PUBLIC_ADMIN_WEB_PASSWORD
ARG NEXT_PUBLIC_ADMIN_TG_ID

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production \
    NEXT_PUBLIC_ADMIN_API_BASE_URL=${NEXT_PUBLIC_ADMIN_API_BASE_URL:-http://localhost:8001} \
    NEXT_PUBLIC_MINIAPP_API_BASE_URL=${NEXT_PUBLIC_MINIAPP_API_BASE_URL:-http://localhost:8080} \
    NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8001/api} \
    NEXT_PUBLIC_DEFAULT_LANG=${NEXT_PUBLIC_DEFAULT_LANG:-zh} \
    NEXT_PUBLIC_ENABLE_DEVTOOLS=${NEXT_PUBLIC_ENABLE_DEVTOOLS:-false} \
    NEXT_PUBLIC_ADMIN_WEB_USER=${NEXT_PUBLIC_ADMIN_WEB_USER:-} \
    NEXT_PUBLIC_ADMIN_WEB_PASSWORD=${NEXT_PUBLIC_ADMIN_WEB_PASSWORD:-} \
    NEXT_PUBLIC_ADMIN_TG_ID=${NEXT_PUBLIC_ADMIN_TG_ID:-}

# 构建 Next.js 应用
RUN npm run build

# 运行阶段
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# 创建非 root 用户
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 复制构建产物
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3001

ENV PORT=3001 \
    HOSTNAME="0.0.0.0"

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3001', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "server.js"]
