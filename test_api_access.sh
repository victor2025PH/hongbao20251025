#!/bin/bash
# 测试 API 访问

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🧪 API 访问测试"
echo "===================================="
echo ""

# 在本地测试（Windows）
echo "从您的本地电脑测试 API 访问..."
echo ""

PUBLIC_IP="165.154.233.55"

echo "===================================="
echo "1️⃣ Web Admin API 测试"
echo "===================================="

echo "测试健康检查端点:"
echo "curl http://$PUBLIC_IP:8000/healthz"
echo ""

# 在 Windows PowerShell 中测试
if command -v curl >/dev/null 2>&1; then
    echo "使用 curl 测试:"
    curl -v --max-time 10 "http://$PUBLIC_IP:8000/healthz" 2>&1 | head -20
else
    echo "curl 不可用，使用 PowerShell 测试..."
    echo "请在 PowerShell 中执行："
    echo "Invoke-WebRequest -Uri 'http://$PUBLIC_IP:8000/healthz' -TimeoutSec 10"
fi
echo ""

echo "===================================="
echo "2️⃣ MiniApp API 测试"
echo "===================================="

echo "测试健康检查端点:"
echo "curl http://$PUBLIC_IP:8080/healthz"
echo ""

# 在 Windows PowerShell 中测试
if command -v curl >/dev/null 2>&1; then
    echo "使用 curl 测试:"
    curl -v --max-time 10 "http://$PUBLIC_IP:8080/healthz" 2>&1 | head -20
else
    echo "curl 不可用，使用 PowerShell 测试..."
    echo "请在 PowerShell 中执行："
    echo "Invoke-WebRequest -Uri 'http://$PUBLIC_IP:8080/healthz' -TimeoutSec 10"
fi
echo ""

echo "===================================="
echo "3️⃣ 服务器端验证"
echo "===================================="

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "检查服务状态："
docker compose -f docker-compose.production.yml ps web_admin miniapp_api | grep -E "web_admin|miniapp_api"
echo ""

echo "检查端口监听："
netstat -tlnp 2>/dev/null | grep -E ":8000|:8080" || ss -tlnp 2>/dev/null | grep -E ":8000|:8080"
echo ""

echo "测试本地访问："
echo "Web Admin API:"
curl -s http://127.0.0.1:8000/healthz | head -1
echo ""

echo "MiniApp API:"
curl -s http://127.0.0.1:8080/healthz | head -1
echo ""

echo "检查防火墙规则："
sudo ufw status | grep -E "8000|8080" || echo "ufw 未启用或无规则"
echo ""

REMOTE_SCRIPT

echo "===================================="
echo "4️⃣ 测试结果总结"
echo "===================================="

echo ""
echo "如果本地测试失败（连接超时），请："
echo "  1. 检查云服务商安全组规则是否已配置"
echo "  2. 等待 1-2 分钟让配置生效"
echo "  3. 检查您的网络连接"
echo "  4. 尝试使用浏览器访问测试"
echo ""

