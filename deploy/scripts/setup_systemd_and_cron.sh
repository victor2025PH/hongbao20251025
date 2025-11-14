#!/bin/bash
# 一键配置 systemd 服务和 cron 任务脚本
# 使用方法: sudo bash deploy/scripts/setup_systemd_and_cron.sh

set -e

PROJECT_DIR="/opt/redpacket"
SCRIPT_DIR="${PROJECT_DIR}/scripts"
SYSTEMD_DIR="${PROJECT_DIR}/deploy/systemd"
LOG_DIR="${PROJECT_DIR}/logs"
BACKUP_DIR="${PROJECT_DIR}/backups"
METRICS_DIR="${PROJECT_DIR}/metrics"

echo "🚀 开始配置 systemd 服务和 cron 任务..."
echo ""

# 检查是否以 root 权限运行（部分操作需要 sudo）
if [ "$EUID" -ne 0 ] && [ "$(id -u)" -ne 0 ]; then
    echo "⚠️  部分操作需要 root 权限，将使用 sudo"
    USE_SUDO="sudo"
else
    USE_SUDO=""
fi

# 步骤 1: 更新代码（如果使用 Git）
echo "📥 步骤 1: 更新代码..."
cd "${PROJECT_DIR}"
if [ -d ".git" ]; then
    echo "   检测到 Git 仓库，尝试拉取最新代码..."
    git pull origin master || git pull origin main || echo "   ⚠️  Git pull 失败，继续执行..."
else
    echo "   ⚠️  未检测到 Git 仓库，跳过代码更新"
fi
echo "✅ 步骤 1 完成"
echo ""

# 步骤 2: 验证 TypeScript 修复（如果 frontend-next 存在）
echo "🔍 步骤 2: 验证前端构建..."
if [ -d "${PROJECT_DIR}/frontend-next" ]; then
    cd "${PROJECT_DIR}/frontend-next"
    if command -v npm &> /dev/null; then
        echo "   运行 npm run build..."
        npm run build || {
            echo "   ⚠️  前端构建失败，但继续执行其他步骤"
            echo "   请检查 TypeScript 错误并手动修复"
        }
    else
        echo "   ⚠️  npm 未安装，跳过前端构建验证"
        echo "   提示: 前端将在 Docker 构建时验证"
    fi
else
    echo "   ⚠️  frontend-next 目录不存在，跳过前端构建验证"
fi
echo "✅ 步骤 2 完成"
echo ""

# 步骤 3: 创建必要的目录
echo "📁 步骤 3: 创建必要的目录..."
mkdir -p "${LOG_DIR}"
mkdir -p "${BACKUP_DIR}"
mkdir -p "${METRICS_DIR}"
chmod 755 "${LOG_DIR}" "${BACKUP_DIR}" "${METRICS_DIR}"
echo "✅ 步骤 3 完成"
echo ""

# 步骤 4: 设置脚本执行权限
echo "🔐 步骤 4: 设置脚本执行权限..."
if [ -d "${SCRIPT_DIR}" ]; then
    chmod +x "${SCRIPT_DIR}/cron_"*.sh 2>/dev/null || true
    chmod +x "${SCRIPT_DIR}/check_"*.sh 2>/dev/null || true
    chmod +x "${SCRIPT_DIR}/monitor_"*.sh 2>/dev/null || true
    echo "   ✅ Cron 脚本权限已设置"
    echo "   ✅ 检查脚本权限已设置"
    echo "   ✅ 监控脚本权限已设置"
else
    echo "   ⚠️  scripts 目录不存在"
fi
echo "✅ 步骤 4 完成"
echo ""

# 步骤 5: 配置 systemd 服务
echo "⚙️  步骤 5: 配置 systemd 服务..."
if [ -f "${SYSTEMD_DIR}/redpacket.service" ]; then
    echo "   复制服务文件到 /etc/systemd/system/..."
    ${USE_SUDO} cp "${SYSTEMD_DIR}/redpacket.service" /etc/systemd/system/
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
    echo "   ✅ systemd 服务配置完成"
else
    echo "   ⚠️  服务文件不存在: ${SYSTEMD_DIR}/redpacket.service"
    echo "   请确保文件已创建"
fi
echo "✅ 步骤 5 完成"
echo ""

# 步骤 6: 配置 Cron 任务
echo "⏰ 步骤 6: 配置 Cron 任务..."
CRON_TEMP_FILE="/tmp/redpacket_cron_$$"
cat > "${CRON_TEMP_FILE}" << 'EOF'
# Red Packet System - 自动生成的 Cron 任务
# 生成时间: $(date)

# 数据库备份（每天凌晨 2 点）
0 2 * * * /opt/redpacket/scripts/cron_backup_db.sh >> /opt/redpacket/logs/cron_backup.log 2>&1

# 健康检查（每 5 分钟）
*/5 * * * * /opt/redpacket/scripts/cron_healthcheck.sh >> /opt/redpacket/logs/healthcheck.log 2>&1

# 服务监控（每 2 分钟）
*/2 * * * * /opt/redpacket/scripts/monitor_service.sh >> /opt/redpacket/logs/monitor.log 2>&1

# 数据库连接检查（每 5 分钟）
*/5 * * * * /opt/redpacket/scripts/check_db_connection.sh >> /opt/redpacket/logs/db_check.log 2>&1

# 磁盘空间检查（每小时）
0 * * * * /opt/redpacket/scripts/check_disk_space.sh >> /opt/redpacket/logs/disk_check.log 2>&1

# 内存检查（每 30 分钟）
*/30 * * * * /opt/redpacket/scripts/check_memory.sh >> /opt/redpacket/logs/memory_check.log 2>&1

# 日志清理（每周日凌晨 3 点）
0 3 * * 0 /opt/redpacket/scripts/cron_cleanup_logs.sh >> /opt/redpacket/logs/cleanup.log 2>&1

# 监控指标收集（每小时）
0 * * * * /opt/redpacket/scripts/cron_collect_metrics.sh >> /opt/redpacket/logs/metrics.log 2>&1
EOF

# 替换日期占位符
sed -i "s/\$(date)/$(date '+%Y-%m-%d %H:%M:%S')/" "${CRON_TEMP_FILE}"

echo "   当前用户的 crontab 内容:"
echo "   ========================="
if crontab -l 2>/dev/null; then
    echo ""
    echo "   是否要添加 Red Packet 系统的 Cron 任务？"
    echo "   (y/n，默认: y)"
    read -r -t 10 -p "   请输入: " ADD_CRON || ADD_CRON="y"
    
    if [ "${ADD_CRON}" = "y" ] || [ "${ADD_CRON}" = "Y" ] || [ -z "${ADD_CRON}" ]; then
        # 检查是否已存在 Red Packet 的 cron 任务
        if crontab -l 2>/dev/null | grep -q "Red Packet System"; then
            echo "   ⚠️  检测到已存在的 Red Packet Cron 任务"
            echo "   是否要替换？(y/n，默认: n)"
            read -r -t 10 -p "   请输入: " REPLACE_CRON || REPLACE_CRON="n"
            
            if [ "${REPLACE_CRON}" = "y" ] || [ "${REPLACE_CRON}" = "Y" ]; then
                # 删除旧的 Red Packet cron 任务
                crontab -l 2>/dev/null | grep -v "Red Packet System" | grep -v "/opt/redpacket/scripts/" | crontab - || true
                # 添加新的
                (crontab -l 2>/dev/null; cat "${CRON_TEMP_FILE}") | crontab -
                echo "   ✅ Cron 任务已替换"
            else
                echo "   ⚠️  跳过添加，保留现有配置"
            fi
        else
            # 直接添加
            (crontab -l 2>/dev/null; cat "${CRON_TEMP_FILE}") | crontab -
            echo "   ✅ Cron 任务已添加"
        fi
    else
        echo "   ⚠️  跳过添加 Cron 任务"
        echo "   您可以稍后手动运行: crontab -e"
        echo "   并添加以下内容:"
        echo ""
        cat "${CRON_TEMP_FILE}"
    fi
else
    echo "   (当前用户没有 crontab)"
    echo "   是否要创建新的 crontab 并添加 Red Packet 任务？(y/n，默认: y)"
    read -r -t 10 -p "   请输入: " CREATE_CRON || CREATE_CRON="y"
    
    if [ "${CREATE_CRON}" = "y" ] || [ "${CREATE_CRON}" = "Y" ] || [ -z "${CREATE_CRON}" ]; then
        cat "${CRON_TEMP_FILE}" | crontab -
        echo "   ✅ Cron 任务已创建"
    else
        echo "   ⚠️  跳过创建 Cron 任务"
    fi
fi

# 清理临时文件
rm -f "${CRON_TEMP_FILE}"

echo "✅ 步骤 6 完成"
echo ""

# 步骤 7: 验证配置
echo "🔍 步骤 7: 验证配置..."
echo "   检查 systemd 服务状态..."
if ${USE_SUDO} systemctl is-active --quiet redpacket.service 2>/dev/null; then
    echo "   ✅ systemd 服务运行中"
else
    echo "   ⚠️  systemd 服务未运行，请检查: sudo systemctl status redpacket.service"
fi

echo "   检查 Cron 任务..."
if crontab -l 2>/dev/null | grep -q "Red Packet System"; then
    echo "   ✅ Cron 任务已配置"
    echo "   查看 Cron 任务: crontab -l"
else
    echo "   ⚠️  Cron 任务未配置，请手动运行: crontab -e"
fi

echo "   检查脚本文件..."
MISSING_SCRIPTS=0
for script in cron_backup_db.sh cron_healthcheck.sh cron_cleanup_logs.sh cron_collect_metrics.sh check_db_connection.sh check_disk_space.sh check_memory.sh monitor_service.sh; do
    if [ ! -f "${SCRIPT_DIR}/${script}" ]; then
        echo "   ⚠️  缺失脚本: ${script}"
        MISSING_SCRIPTS=$((MISSING_SCRIPTS + 1))
    fi
done
if [ ${MISSING_SCRIPTS} -eq 0 ]; then
    echo "   ✅ 所有脚本文件存在"
else
    echo "   ⚠️  有 ${MISSING_SCRIPTS} 个脚本文件缺失"
fi

echo "✅ 步骤 7 完成"
echo ""

# 总结
echo "=========================================="
echo "🎉 配置完成！"
echo "=========================================="
echo ""
echo "📋 后续操作:"
echo ""
echo "1. 检查 systemd 服务:"
echo "   sudo systemctl status redpacket.service"
echo "   sudo journalctl -u redpacket.service -f"
echo ""
echo "2. 检查 Cron 任务:"
echo "   crontab -l"
echo ""
echo "3. 查看日志:"
echo "   tail -f ${LOG_DIR}/healthcheck.log"
echo "   tail -f ${LOG_DIR}/monitor.log"
echo ""
echo "4. 测试健康检查:"
echo "   curl http://localhost:8000/healthz"
echo ""
echo "5. 如果需要修改 Cron 任务:"
echo "   crontab -e"
echo ""
echo "6. 如果需要重启服务:"
echo "   sudo systemctl restart redpacket.service"
echo ""
echo "=========================================="

