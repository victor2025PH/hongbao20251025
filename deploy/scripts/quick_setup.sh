#!/bin/bash
# 快速配置脚本（简化版，不依赖新文件）
# 使用方法: sudo bash deploy/scripts/quick_setup.sh

set -e

PROJECT_DIR="/opt/redpacket"

echo "🚀 快速配置 systemd 服务和 cron 任务..."
echo ""

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ] && [ "$(id -u)" -ne 0 ]; then
    echo "⚠️  部分操作需要 root 权限，将使用 sudo"
    USE_SUDO="sudo"
else
    USE_SUDO=""
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p "${PROJECT_DIR}/logs"
mkdir -p "${PROJECT_DIR}/backups"
mkdir -p "${PROJECT_DIR}/metrics"
chmod 755 "${PROJECT_DIR}/logs" "${PROJECT_DIR}/backups" "${PROJECT_DIR}/metrics"
echo "✅ 目录创建完成"
echo ""

# 设置脚本权限（如果存在）
echo "🔐 设置脚本权限..."
if [ -d "${PROJECT_DIR}/scripts" ]; then
    chmod +x "${PROJECT_DIR}/scripts/cron_"*.sh 2>/dev/null || true
    chmod +x "${PROJECT_DIR}/scripts/check_"*.sh 2>/dev/null || true
    chmod +x "${PROJECT_DIR}/scripts/monitor_"*.sh 2>/dev/null || true
    echo "✅ 脚本权限已设置"
else
    echo "⚠️  scripts 目录不存在"
fi
echo ""

# 创建 systemd 服务文件（如果不存在）
echo "⚙️  配置 systemd 服务..."
SYSTEMD_FILE="/etc/systemd/system/redpacket.service"

if [ ! -f "${SYSTEMD_FILE}" ]; then
    echo "   创建 systemd 服务文件..."
    ${USE_SUDO} tee "${SYSTEMD_FILE}" > /dev/null << 'EOF'
[Unit]
Description=Red Packet System (Docker Compose)
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/redpacket
ExecStart=/usr/bin/docker-compose -f /opt/redpacket/docker-compose.production.yml up -d
ExecStop=/usr/bin/docker-compose -f /opt/redpacket/docker-compose.production.yml down
ExecReload=/usr/bin/docker-compose -f /opt/redpacket/docker-compose.production.yml restart
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
    echo "   ✅ 服务文件已创建"
else
    echo "   ✅ 服务文件已存在"
fi

# 启用并启动服务
echo "   重新加载 systemd..."
${USE_SUDO} systemctl daemon-reload
echo "   启用服务（开机自启）..."
${USE_SUDO} systemctl enable redpacket.service
echo "   启动服务..."
${USE_SUDO} systemctl start redpacket.service || {
    echo "   ⚠️  服务启动失败，请检查配置"
    echo "   查看日志: sudo journalctl -u redpacket.service -n 50"
}
echo "   检查服务状态..."
${USE_SUDO} systemctl status redpacket.service --no-pager -l || true
echo "✅ systemd 服务配置完成"
echo ""

# 配置 Cron 任务
echo "⏰ 配置 Cron 任务..."
CRON_TEMP_FILE="/tmp/redpacket_cron_$$"
cat > "${CRON_TEMP_FILE}" << 'EOF'
# Red Packet System - Cron 任务
0 2 * * * /opt/redpacket/scripts/cron_backup_db.sh >> /opt/redpacket/logs/cron_backup.log 2>&1
*/5 * * * * /opt/redpacket/scripts/cron_healthcheck.sh >> /opt/redpacket/logs/healthcheck.log 2>&1
*/2 * * * * /opt/redpacket/scripts/monitor_service.sh >> /opt/redpacket/logs/monitor.log 2>&1
*/5 * * * * /opt/redpacket/scripts/check_db_connection.sh >> /opt/redpacket/logs/db_check.log 2>&1
0 * * * * /opt/redpacket/scripts/check_disk_space.sh >> /opt/redpacket/logs/disk_check.log 2>&1
*/30 * * * * /opt/redpacket/scripts/check_memory.sh >> /opt/redpacket/logs/memory_check.log 2>&1
0 3 * * 0 /opt/redpacket/scripts/cron_cleanup_logs.sh >> /opt/redpacket/logs/cleanup.log 2>&1
0 * * * * /opt/redpacket/scripts/cron_collect_metrics.sh >> /opt/redpacket/logs/metrics.log 2>&1
EOF

# 检查是否已存在 Red Packet 的 cron 任务
if crontab -l 2>/dev/null | grep -q "Red Packet System"; then
    echo "   ⚠️  检测到已存在的 Red Packet Cron 任务"
    echo "   是否要替换？(y/n，默认: n)"
    read -r -t 10 -p "   请输入: " REPLACE_CRON || REPLACE_CRON="n"
    
    if [ "${REPLACE_CRON}" = "y" ] || [ "${REPLACE_CRON}" = "Y" ]; then
        crontab -l 2>/dev/null | grep -v "Red Packet System" | grep -v "/opt/redpacket/scripts/" | crontab - || true
        (crontab -l 2>/dev/null; cat "${CRON_TEMP_FILE}") | crontab -
        echo "   ✅ Cron 任务已替换"
    else
        echo "   ⚠️  跳过添加，保留现有配置"
    fi
else
    echo "   添加 Cron 任务..."
    (crontab -l 2>/dev/null; cat "${CRON_TEMP_FILE}") | crontab -
    echo "   ✅ Cron 任务已添加"
fi

rm -f "${CRON_TEMP_FILE}"
echo "✅ Cron 任务配置完成"
echo ""

# 验证配置
echo "🔍 验证配置..."
if ${USE_SUDO} systemctl is-active --quiet redpacket.service 2>/dev/null; then
    echo "   ✅ systemd 服务运行中"
else
    echo "   ⚠️  systemd 服务未运行"
fi

if crontab -l 2>/dev/null | grep -q "Red Packet System"; then
    echo "   ✅ Cron 任务已配置"
else
    echo "   ⚠️  Cron 任务未配置"
fi

echo ""
echo "=========================================="
echo "🎉 配置完成！"
echo "=========================================="
echo ""
echo "📋 后续操作:"
echo ""
echo "1. 检查服务状态:"
echo "   sudo systemctl status redpacket.service"
echo ""
echo "2. 查看服务日志:"
echo "   sudo journalctl -u redpacket.service -f"
echo ""
echo "3. 查看 Cron 任务:"
echo "   crontab -l"
echo ""
echo "4. 测试健康检查:"
echo "   curl http://localhost:8000/healthz"
echo ""

