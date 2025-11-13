#!/bin/bash
# 部署步骤 1: 服务器环境检查脚本

echo "🔍 开始检查服务器环境..."
echo ""

# 检查操作系统
echo "📦 操作系统信息:"
if [ -f /etc/os-release ]; then
    cat /etc/os-release | grep -E "^NAME|^VERSION"
else
    echo "⚠️  无法检测操作系统版本"
fi
echo ""

# 检查 Python
echo "🐍 Python 版本:"
if command -v python3 &> /dev/null; then
    python3 --version
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        echo "✅ Python 版本符合要求 (3.11+)"
    else
        echo "❌ Python 版本过低，需要 3.11+"
    fi
else
    echo "❌ Python3 未安装"
fi
echo ""

# 检查 Node.js
echo "📦 Node.js 版本:"
if command -v node &> /dev/null; then
    node --version
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        echo "✅ Node.js 版本符合要求 (18+)"
    else
        echo "❌ Node.js 版本过低，需要 18+"
    fi
else
    echo "❌ Node.js 未安装"
fi
echo ""

# 检查 npm
echo "📦 npm 版本:"
if command -v npm &> /dev/null; then
    npm --version
else
    echo "❌ npm 未安装"
fi
echo ""

# 检查 Docker
echo "🐳 Docker 版本:"
if command -v docker &> /dev/null; then
    docker --version
    if command -v docker-compose &> /dev/null; then
        docker-compose --version
        echo "✅ Docker 和 Docker Compose 已安装"
    else
        echo "⚠️  Docker Compose 未安装"
    fi
else
    echo "⚠️  Docker 未安装（可选，如果使用 Docker 部署）"
fi
echo ""

# 检查端口占用
echo "🔌 端口占用检查:"
PORTS=(8000 8080 3001 5432 6379)
for PORT in "${PORTS[@]}"; do
    if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
        echo "⚠️  端口 $PORT 已被占用:"
        netstat -tlnp 2>/dev/null | grep ":$PORT "
    else
        echo "✅ 端口 $PORT 可用"
    fi
done
echo ""

# 检查磁盘空间
echo "💾 磁盘空间:"
df -h / | tail -1 | awk '{print "可用空间: " $4 " / 总空间: " $2}'
echo ""

# 检查内存
echo "🧠 内存信息:"
free -h | grep Mem | awk '{print "总内存: " $2 ", 已用: " $3 ", 可用: " $7}'
echo ""

echo "✅ 环境检查完成"
echo ""
echo "如果发现问题，请先解决后再继续部署。"

