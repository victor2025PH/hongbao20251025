#!/bin/bash
# 自动修复 systemd 服务配置脚本
# 使用方法: sudo bash deploy/scripts/fix_systemd_service.sh

set -e

PROJECT_DIR="/opt/redpacket"
SERVICE_FILE="/etc/systemd/system/redpacket.service"

echo "🔧 自动修复 systemd 服务配置..."
echo ""

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ] && [ "$(id -u)" -ne 0 ]; then
    echo "⚠️  需要 root 权限，使用 sudo"
    USE_SUDO="sudo"
else
    USE_SUDO=""
fi

# 步骤 1: 检测 docker-compose 路径
echo "🔍 步骤 1: 检测 docker-compose 路径..."
DOCKER_COMPOSE_CMD=""

# 尝试查找 docker-compose (旧版本)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD=$(which docker-compose)
    echo "   ✅ 找到 docker-compose: ${DOCKER_COMPOSE_CMD}"
elif [ -f "/usr/local/bin/docker-compose" ]; then
    DOCKER_COMPOSE_CMD="/usr/local/bin/docker-compose"
    echo "   ✅ 找到 docker-compose: ${DOCKER_COMPOSE_CMD}"
elif [ -f "/usr/bin/docker-compose" ]; then
    DOCKER_COMPOSE_CMD="/usr/bin/docker-compose"
    echo "   ✅ 找到 docker-compose: ${DOCKER_COMPOSE_CMD}"
# 尝试使用新版本的 docker compose
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="/usr/bin/docker compose"
    echo "   ✅ 使用 docker compose (新版本): ${DOCKER_COMPOSE_CMD}"
else
    echo "   ❌ 未找到 docker-compose 命令"
    echo "   请先安装 docker-compose 或确保 Docker 已正确安装"
    exit 1
fi

# 步骤 2: 检测 docker-compose 文件
echo ""
echo "🔍 步骤 2: 检测 docker-compose 文件..."
cd "${PROJECT_DIR}"

COMPOSE_FILE=""
if [ -f "docker-compose.production.yml" ]; then
    COMPOSE_FILE="docker-compose.production.yml"
    echo "   ✅ 找到: ${COMPOSE_FILE}"
elif [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
    echo "   ✅ 找到: ${COMPOSE_FILE}"
else
    echo "   ❌ 未找到 docker-compose 文件"
    echo "   请确保以下文件之一存在:"
    echo "   - docker-compose.production.yml"
    echo "   - docker-compose.yml"
    exit 1
fi

# 步骤 3: 测试 docker-compose 命令
echo ""
echo "🔍 步骤 3: 测试 docker-compose 命令..."
if [[ "${DOCKER_COMPOSE_CMD}" == *"docker compose"* ]]; then
    # 新版本: docker compose
    if ! docker compose -f "${PROJECT_DIR}/${COMPOSE_FILE}" config &> /dev/null; then
        echo "   ⚠️  docker compose 命令测试失败，但继续执行"
    else
        echo "   ✅ docker compose 命令可用"
    fi
else
    # 旧版本: docker-compose
    if ! "${DOCKER_COMPOSE_CMD}" -f "${PROJECT_DIR}/${COMPOSE_FILE}" config &> /dev/null; then
        echo "   ⚠️  docker-compose 命令测试失败，但继续执行"
    else
        echo "   ✅ docker-compose 命令可用"
    fi
fi

# 步骤 4: 更新 systemd 服务文件
echo ""
echo "⚙️  步骤 4: 更新 systemd 服务文件..."

${USE_SUDO} tee "${SERVICE_FILE}" > /dev/null << EOF
[Unit]
Description=Red Packet System (Docker Compose)
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${PROJECT_DIR}
ExecStart=${DOCKER_COMPOSE_CMD} -f ${PROJECT_DIR}/${COMPOSE_FILE} up -d
ExecStop=${DOCKER_COMPOSE_CMD} -f ${PROJECT_DIR}/${COMPOSE_FILE} down
ExecReload=${DOCKER_COMPOSE_CMD} -f ${PROJECT_DIR}/${COMPOSE_FILE} restart
TimeoutStartSec=0
Restart=on-failure
RestartSec=10

Environment="COMPOSE_PROJECT_NAME=redpacket"
Environment="TZ=Asia/Manila"

StandardOutput=journal
StandardError=journal
SyslogIdentifier=redpacket

[Install]
WantedBy=multi-user.target
EOF

echo "   ✅ 服务文件已更新"
echo "   使用的命令: ${DOCKER_COMPOSE_CMD}"
echo "   使用的文件: ${COMPOSE_FILE}"

# 步骤 5: 重新加载并启动服务
echo ""
echo "🚀 步骤 5: 重新加载并启动服务..."
${USE_SUDO} systemctl daemon-reload
echo "   ✅ systemd 配置已重新加载"

${USE_SUDO} systemctl enable redpacket.service
echo "   ✅ 服务已启用（开机自启）"

echo "   启动服务..."
if ${USE_SUDO} systemctl start redpacket.service; then
    echo "   ✅ 服务启动成功"
else
    echo "   ⚠️  服务启动失败，查看详细错误:"
    ${USE_SUDO} systemctl status redpacket.service --no-pager -l || true
    echo ""
    echo "   查看日志:"
    echo "   sudo journalctl -xeu redpacket.service -n 50"
    exit 1
fi

# 步骤 6: 验证服务状态
echo ""
echo "🔍 步骤 6: 验证服务状态..."
sleep 2
${USE_SUDO} systemctl status redpacket.service --no-pager -l || true

echo ""
echo "=========================================="
echo "🎉 修复完成！"
echo "=========================================="
echo ""
echo "📋 后续操作:"
echo ""
echo "1. 查看服务状态:"
echo "   sudo systemctl status redpacket.service"
echo ""
echo "2. 查看服务日志:"
echo "   sudo journalctl -u redpacket.service -f"
echo ""
echo "3. 检查 Docker 容器:"
echo "   docker ps"
echo ""
echo "4. 测试健康检查:"
echo "   curl http://localhost:8000/healthz"
echo ""

