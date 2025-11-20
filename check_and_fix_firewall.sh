#!/bin/bash
# 检查并修复防火墙配置

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔧 检查并修复防火墙配置"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 检查防火墙状态"
echo "===================================="

# 检查 ufw 防火墙
if command -v ufw >/dev/null 2>&1; then
    echo "检查 ufw 防火墙状态："
    sudo ufw status
    echo ""
    
    echo "检查已开放的端口："
    sudo ufw status | grep -E "8000|8080" || echo "  8000 和 8080 端口未开放"
    echo ""
fi

# 检查 firewalld 防火墙
if command -v firewall-cmd >/dev/null 2>&1; then
    echo "检查 firewalld 防火墙状态："
    sudo firewall-cmd --state 2>/dev/null || echo "  firewalld 未运行"
    echo ""
    
    if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
        echo "检查已开放的端口："
        sudo firewall-cmd --list-ports 2>/dev/null || echo "  无法获取端口列表"
        echo ""
    fi
fi

# 检查 iptables
echo "检查 iptables 规则："
sudo iptables -L -n | grep -E "8000|8080" || echo "  未找到 8000 或 8080 的规则"
echo ""

echo "===================================="
echo "2️⃣ 开放防火墙端口"
echo "===================================="

# 尝试使用 ufw
if command -v ufw >/dev/null 2>&1; then
    echo "使用 ufw 开放端口..."
    
    # 检查端口是否已开放
    if ! sudo ufw status | grep -q "8000/tcp"; then
        echo "开放 8000 端口..."
        echo "y" | sudo ufw allow 8000/tcp 2>/dev/null || sudo ufw allow 8000/tcp
        echo "✅ 8000 端口已开放"
    else
        echo "✅ 8000 端口已开放"
    fi
    
    if ! sudo ufw status | grep -q "8080/tcp"; then
        echo "开放 8080 端口..."
        echo "y" | sudo ufw allow 8080/tcp 2>/dev/null || sudo ufw allow 8080/tcp
        echo "✅ 8080 端口已开放"
    else
        echo "✅ 8080 端口已开放"
    fi
    
    # 确保 ufw 已启用
    if sudo ufw status | grep -q "Status: inactive"; then
        echo "启用 ufw 防火墙..."
        echo "y" | sudo ufw enable 2>/dev/null || sudo ufw enable
    fi
    
    echo ""
    echo "验证端口开放状态："
    sudo ufw status | grep -E "8000|8080"
    echo ""
fi

# 尝试使用 firewalld
if command -v firewall-cmd >/dev/null 2>&1 && sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
    echo "使用 firewalld 开放端口..."
    
    if ! sudo firewall-cmd --list-ports 2>/dev/null | grep -q "8000/tcp"; then
        echo "开放 8000 端口..."
        sudo firewall-cmd --permanent --add-port=8000/tcp 2>/dev/null
        sudo firewall-cmd --reload 2>/dev/null
        echo "✅ 8000 端口已开放"
    else
        echo "✅ 8000 端口已开放"
    fi
    
    if ! sudo firewall-cmd --list-ports 2>/dev/null | grep -q "8080/tcp"; then
        echo "开放 8080 端口..."
        sudo firewall-cmd --permanent --add-port=8080/tcp 2>/dev/null
        sudo firewall-cmd --reload 2>/dev/null
        echo "✅ 8080 端口已开放"
    else
        echo "✅ 8080 端口已开放"
    fi
    
    echo ""
    echo "验证端口开放状态："
    sudo firewall-cmd --list-ports 2>/dev/null
    echo ""
fi

echo "===================================="
echo "3️⃣ 检查服务监听状态"
echo "===================================="

echo "检查端口监听状态："
netstat -tlnp 2>/dev/null | grep -E ":8000|:8080" || ss -tlnp 2>/dev/null | grep -E ":8000|:8080"
echo ""

echo "===================================="
echo "4️⃣ 测试本地访问"
echo "===================================="

echo "测试 Web Admin API (本地):"
curl -s --max-time 5 http://127.0.0.1:8000/healthz 2>&1 | head -3 || echo "  本地访问失败"
echo ""

echo "测试 MiniApp API (本地):"
curl -s --max-time 5 http://127.0.0.1:8080/healthz 2>&1 | head -3 || echo "  本地访问失败"
echo ""

echo "===================================="
echo "5️⃣ 检查云服务商安全组"
echo "===================================="

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "165.154.233.55")
echo ""
echo "⚠️  重要提示："
echo "   服务器公网 IP: $PUBLIC_IP"
echo ""
echo "   如果仍然无法访问，请检查云服务商的安全组规则："
echo "   1. 登录云服务商控制台（如 UCloud）"
echo "   2. 找到云主机：UHost-Sale (uhost-lilim17se6os)"
echo "   3. 检查安全组规则，确保允许："
echo "      - 入站规则：TCP 8000 端口（来源：0.0.0.0/0）"
echo "      - 入站规则：TCP 8080 端口（来源：0.0.0.0/0）"
echo "   4. 如果没有开放，请添加规则并保存"
echo ""

echo "===================================="
echo "6️⃣ 验证外部访问测试"
echo "===================================="

echo "测试从服务器内部访问公网 IP:"
curl -s --max-time 5 http://$PUBLIC_IP:8000/healthz 2>&1 | head -3 || echo "  无法访问（可能需要安全组配置）"
echo ""

echo "===================================="
echo "✅ 检查完成"
echo "===================================="
echo ""

REMOTE_SCRIPT

