#!/bin/bash
# 新服务器完整部署脚本
# 适用于重新安装系统的服务器
# 在服务器上执行: bash deploy/scripts/new_server_setup.sh

set -e  # 遇到错误立即退出

echo "===================================="
echo "🚀 新服务器完整部署脚本"
echo "===================================="
echo ""
echo "此脚本将执行以下操作："
echo "  1. 检查系统环境"
echo "  2. 安装 Docker 和 Docker Compose"
echo "  3. 创建项目目录"
echo "  4. 克隆代码"
echo "  5. 配置环境变量（需要手动编辑）"
echo ""
echo "===================================="
echo ""
read -p "按 Enter 继续，或 Ctrl+C 取消..."

# 步骤 1: 检查系统环境
echo ""
echo "📋 步骤 1: 检查系统环境..."
echo ""

# 检查操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "✅ 操作系统: $PRETTY_NAME"
else
    echo "⚠️  警告: 无法检测操作系统版本"
fi

# 检查是否为 root 或有 sudo 权限
if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
    SUDO="sudo"
    echo "✅ 具有管理员权限"
else
    echo "❌ 错误: 需要 sudo 权限来安装软件"
    exit 1
fi

# 步骤 2: 更新系统并安装基础工具
echo ""
echo "📦 步骤 2: 更新系统并安装基础工具..."
echo ""
$SUDO apt-get update
$SUDO apt-get install -y curl wget git

# 步骤 3: 安装 Docker
echo ""
echo "🐳 步骤 3: 安装 Docker..."
echo ""

if command -v docker &> /dev/null; then
    echo "✅ Docker 已安装: $(docker --version)"
else
    echo "正在安装 Docker..."
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    $SUDO sh /tmp/get-docker.sh
    rm /tmp/get-docker.sh
    
    # 将当前用户添加到 docker 组
    $SUDO usermod -aG docker $USER
    echo "✅ Docker 安装完成"
fi

# 步骤 4: 安装 Docker Compose
echo ""
echo "🐙 步骤 4: 安装 Docker Compose..."
echo ""

if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose 已安装: $(docker-compose --version)"
else
    echo "正在安装 Docker Compose..."
    $SUDO curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    $SUDO chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 安装完成"
fi

# 启动 Docker 服务
echo ""
echo "🔄 启动 Docker 服务..."
$SUDO systemctl start docker
$SUDO systemctl enable docker

# 验证安装
echo ""
echo "🧪 验证 Docker 安装..."
docker --version
docker-compose --version

# 步骤 5: 创建项目目录
echo ""
echo "📂 步骤 5: 创建项目目录..."
echo ""

PROJECT_DIR="/opt/redpacket"
if [ ! -d "$PROJECT_DIR" ]; then
    $SUDO mkdir -p $PROJECT_DIR
    $SUDO chown $USER:$USER $PROJECT_DIR
    echo "✅ 项目目录已创建: $PROJECT_DIR"
else
    echo "⚠️  项目目录已存在: $PROJECT_DIR"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 步骤 6: 克隆代码
echo ""
echo "📥 步骤 6: 克隆代码..."
echo ""

cd $PROJECT_DIR

if [ -d ".git" ]; then
    echo "⚠️  代码目录已存在，尝试拉取最新代码..."
    git pull origin master || {
        echo "⚠️  Git 拉取失败，继续使用现有代码"
    }
else
    echo "正在克隆代码..."
    git clone https://github.com/victor2025PH/hongbao20251025.git .
    echo "✅ 代码克隆完成"
fi

# 步骤 7: 配置环境变量
echo ""
echo "⚙️  步骤 7: 配置环境变量..."
echo ""

if [ ! -f .env.production ]; then
    echo "创建 .env.production 文件..."
    cat > .env.production << 'ENVEOF'
# PostgreSQL 数据库配置（必需）
POSTGRES_USER=redpacket
POSTGRES_PASSWORD=CHANGE_ME_TO_STRONG_PASSWORD
POSTGRES_DB=redpacket

# Telegram Bot 配置（必需）
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_IDS=YOUR_TELEGRAM_USER_ID
SUPER_ADMINS=YOUR_TELEGRAM_USER_ID

# 其他配置
FLAG_ENABLE_PUBLIC_GROUPS=1
DEBUG=false
TZ=Asia/Manila

# Web Admin 配置
ADMIN_WEB_USER=admin
ADMIN_WEB_PASSWORD=CHANGE_ME_TO_ADMIN_PASSWORD
ADMIN_SESSION_SECRET=CHANGE_ME_TO_32_CHARS_RANDOM_STRING

# MiniApp 配置
MINIAPP_JWT_SECRET=CHANGE_ME_TO_SECURE_VALUE
MINIAPP_JWT_ISSUER=miniapp
MINIAPP_JWT_EXPIRE_SECONDS=7200

# NOWPayments 配置（如果使用）
# NOWPAYMENTS_API_KEY=YOUR_API_KEY
# NOWPAYMENTS_IPN_SECRET=YOUR_IPN_SECRET
# NOWPAYMENTS_IPN_URL=https://your-domain.com/api/v1/ipn/nowpayments
ENVEOF
    echo "✅ .env.production 文件已创建"
    echo ""
    echo "⚠️  重要: 请编辑 .env.production 文件并修改以下配置："
    echo "  - POSTGRES_PASSWORD (数据库密码)"
    echo "  - BOT_TOKEN (Telegram Bot Token)"
    echo "  - ADMIN_IDS (您的 Telegram 用户 ID)"
    echo "  - ADMIN_WEB_PASSWORD (Web 管理员密码)"
    echo "  - ADMIN_SESSION_SECRET (随机字符串，至少 32 个字符)"
    echo "  - MINIAPP_JWT_SECRET (随机字符串)"
    echo ""
    read -p "按 Enter 编辑配置文件，或 Ctrl+C 稍后手动编辑..."
    nano .env.production || vim .env.production || {
        echo "⚠️  编辑器不可用，请稍后手动编辑: $PROJECT_DIR/.env.production"
    }
else
    echo "✅ .env.production 文件已存在"
fi

# 步骤 8: 提示下一步操作
echo ""
echo "===================================="
echo "✅ 服务器环境准备完成！"
echo "===================================="
echo ""
echo "下一步操作："
echo ""
echo "1. 确认 .env.production 配置正确"
echo "2. 执行部署脚本:"
echo "   cd $PROJECT_DIR"
echo "   bash deploy/scripts/deploy_on_server.sh"
echo ""
echo "或者手动执行："
echo "   cd $PROJECT_DIR"
echo "   docker compose -f docker-compose.production.yml build"
echo "   docker compose -f docker-compose.production.yml up -d"
echo ""
echo "===================================="
echo ""

# 提示需要重新登录以应用 docker 组权限
if ! groups | grep -q docker; then
    echo "⚠️  注意: 已将用户添加到 docker 组，但需要重新登录 SSH 才能生效"
    echo "   或者执行: newgrp docker"
    echo ""
fi

echo "✅ 脚本执行完成！"
echo ""
