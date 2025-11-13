#!/bin/bash
# 部署步骤 2: 安装必要软件

set -e

echo "📦 开始安装必要软件..."
echo ""

# 更新系统包
echo "🔄 更新系统包..."
sudo apt-get update -y
echo ""

# 安装基础工具
echo "🔧 安装基础工具..."
sudo apt-get install -y curl wget git build-essential
echo ""

# 安装 Python 3.11+（如果未安装或版本过低）
if ! command -v python3 &> /dev/null || [ "$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2 | awk '{if ($1 >= 3.11) print "ok"}')" != "ok" ]; then
    echo "🐍 安装 Python 3.11..."
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update -y
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
    echo "✅ Python 3.11 安装完成"
else
    echo "✅ Python 版本已符合要求"
fi
echo ""

# 安装 Node.js 18+（如果未安装或版本过低）
if ! command -v node &> /dev/null || [ "$(node --version | cut -d'v' -f2 | cut -d'.' -f1)" -lt 18 ]; then
    echo "📦 安装 Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo "✅ Node.js 安装完成"
else
    echo "✅ Node.js 版本已符合要求"
fi
echo ""

# 安装 Docker（可选，如果使用 Docker 部署）
read -p "是否安装 Docker? (y/n): " install_docker
if [ "$install_docker" = "y" ]; then
    echo "🐳 安装 Docker..."
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm get-docker.sh
        sudo usermod -aG docker $USER
        echo "✅ Docker 安装完成"
        echo "⚠️  请重新登录以使 Docker 组权限生效"
    else
        echo "✅ Docker 已安装"
    fi
    
    # 安装 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "🐳 安装 Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        echo "✅ Docker Compose 安装完成"
    else
        echo "✅ Docker Compose 已安装"
    fi
else
    echo "⏭️  跳过 Docker 安装"
fi
echo ""

# 安装 Nginx
echo "🌐 安装 Nginx..."
if ! command -v nginx &> /dev/null; then
    sudo apt-get install -y nginx
    sudo systemctl enable nginx
    echo "✅ Nginx 安装完成"
else
    echo "✅ Nginx 已安装"
fi
echo ""

# 安装 Certbot（用于 SSL 证书）
echo "🔒 安装 Certbot..."
if ! command -v certbot &> /dev/null; then
    sudo apt-get install -y certbot python3-certbot-nginx
    echo "✅ Certbot 安装完成"
else
    echo "✅ Certbot 已安装"
fi
echo ""

echo "✅ 软件安装完成"
echo ""
echo "下一步: 准备项目代码和配置环境变量"

