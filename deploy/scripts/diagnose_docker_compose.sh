#!/bin/bash
# Docker Compose 启动失败诊断脚本
# 使用方法: bash deploy/scripts/diagnose_docker_compose.sh

set -e

PROJECT_DIR="/opt/redpacket"

echo "🔍 Docker Compose 启动失败诊断..."
echo "=========================================="
echo ""

# 1. 检查 Docker 服务状态
echo "1️⃣  检查 Docker 服务状态:"
if systemctl is-active --quiet docker 2>/dev/null; then
    echo "   ✅ Docker 服务运行中"
else
    echo "   ❌ Docker 服务未运行"
    echo "   启动 Docker: sudo systemctl start docker"
fi
echo ""

# 2. 检查 Docker Compose 版本
echo "2️⃣  检查 Docker Compose 版本:"
if docker compose version &> /dev/null; then
    docker compose version
    echo "   ✅ Docker Compose 可用"
else
    echo "   ❌ Docker Compose 不可用"
fi
echo ""

# 3. 检查配置文件
echo "3️⃣  检查配置文件:"
cd "${PROJECT_DIR}"
if docker compose -f docker-compose.production.yml config > /dev/null 2>&1; then
    echo "   ✅ 配置文件有效"
else
    echo "   ❌ 配置文件有错误，详细输出:"
    docker compose -f docker-compose.production.yml config
fi
echo ""

# 4. 检查环境变量文件
echo "4️⃣  检查环境变量文件:"
if [ -f ".env.production" ]; then
    echo "   ✅ .env.production 存在"
    echo "   关键变量检查:"
    if grep -q "DATABASE_URL" .env.production 2>/dev/null; then
        echo "      ✅ DATABASE_URL 已配置"
    else
        echo "      ⚠️  DATABASE_URL 未配置"
    fi
    if grep -q "POSTGRES_PASSWORD" .env.production 2>/dev/null; then
        echo "      ✅ POSTGRES_PASSWORD 已配置"
    else
        echo "      ⚠️  POSTGRES_PASSWORD 未配置"
    fi
else
    echo "   ❌ .env.production 不存在"
    echo "   请创建: cp .env.example .env.production && nano .env.production"
fi
echo ""

# 5. 检查端口占用
echo "5️⃣  检查端口占用:"
for port in 8000 3001 5432; do
    if ss -tulpn 2>/dev/null | grep -q ":${port} "; then
        echo "   ⚠️  端口 ${port} 被占用:"
        ss -tulpn 2>/dev/null | grep ":${port} " || true
    else
        echo "   ✅ 端口 ${port} 可用"
    fi
done
echo ""

# 6. 检查磁盘空间
echo "6️⃣  检查磁盘空间:"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "${DISK_USAGE}" -gt 90 ]; then
    echo "   ⚠️  磁盘使用率: ${DISK_USAGE}% (超过 90%)"
else
    echo "   ✅ 磁盘使用率: ${DISK_USAGE}%"
fi
df -h / | tail -1
echo ""

# 7. 检查 Docker 资源
echo "7️⃣  检查 Docker 资源:"
DOCKER_INFO=$(docker info 2>&1)
if echo "${DOCKER_INFO}" | grep -q "Server Version"; then
    echo "   ✅ Docker 正常运行"
    echo "   容器数量: $(docker ps -a | wc -l)"
    echo "   镜像数量: $(docker images | wc -l)"
else
    echo "   ❌ Docker 异常:"
    echo "${DOCKER_INFO}" | head -5
fi
echo ""

# 8. 尝试手动启动（查看详细错误）
echo "8️⃣  尝试手动启动（查看详细错误）:"
echo "   执行: docker compose -f docker-compose.production.yml up -d"
echo ""
docker compose -f docker-compose.production.yml up -d 2>&1 | tail -30 || {
    echo "   ❌ 启动失败，查看上面的错误信息"
}
echo ""

# 9. 查看容器状态
echo "9️⃣  查看容器状态:"
docker compose -f docker-compose.production.yml ps 2>/dev/null || echo "   无法查看容器状态"
echo ""

# 10. 查看服务日志
echo "🔟 查看 systemd 服务日志:"
if systemctl is-active --quiet redpacket.service 2>/dev/null || systemctl is-failed --quiet redpacket.service 2>/dev/null; then
    echo "   最近 20 行日志:"
    sudo journalctl -u redpacket.service -n 20 --no-pager || true
else
    echo "   服务未运行或不存在"
fi
echo ""

echo "=========================================="
echo "🎯 诊断完成！"
echo "=========================================="
echo ""
echo "📋 下一步操作:"
echo ""
echo "如果配置文件有错误，修复后重新启动:"
echo "  docker compose -f docker-compose.production.yml up -d"
echo ""
echo "如果环境变量缺失，创建 .env.production:"
echo "  cp .env.example .env.production"
echo "  nano .env.production"
echo ""
echo "查看详细错误日志:"
echo "  sudo journalctl -xeu redpacket.service -n 100"
echo "  docker compose -f docker-compose.production.yml logs"
echo ""

