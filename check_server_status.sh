#!/bin/bash
# 检查服务器状态（通过其他方式验证）

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔍 检查服务器状态"
echo "===================================="
echo ""

# 尝试多种方式连接
echo "1️⃣ 检查 SSH 连接..."
timeout 5 ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$server" "echo 'SSH 连接成功'" 2>&1
SSH_RESULT=$?

if [ $SSH_RESULT -eq 0 ]; then
    echo "✅ SSH 连接正常"
    echo ""
    
    echo "2️⃣ 检查服务状态..."
    ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "检查 Docker 服务状态:"
docker compose -f docker-compose.production.yml ps web_admin miniapp_api 2>&1 | head -20
echo ""

echo "检查端口监听:"
netstat -tlnp 2>/dev/null | grep -E ":8000|:8080" || ss -tlnp 2>/dev/null | grep -E ":8000|:8080"
echo ""

echo "检查防火墙状态:"
sudo ufw status | head -10
echo ""

echo "测试本地访问:"
echo "Web Admin API:"
curl -s --max-time 5 http://127.0.0.1:8000/healthz || echo "本地访问失败"
echo ""
echo "MiniApp API:"
curl -s --max-time 5 http://127.0.0.1:8080/healthz || echo "本地访问失败"
echo ""

echo "检查 Docker 日志 (最近 10 行):"
docker compose -f docker-compose.production.yml logs --tail=10 web_admin 2>&1 | tail -10
echo ""

REMOTE_SCRIPT
    
elif [ $SSH_RESULT -eq 124 ] || [ $SSH_RESULT -eq 255 ]; then
    echo "❌ SSH 连接超时或失败"
    echo "   这可能是安全组未开放 22 端口导致的"
    echo ""
fi

echo ""
echo "===================================="
echo "📊 诊断结果"
echo "===================================="
echo ""

if [ $SSH_RESULT -ne 0 ]; then
    echo "⚠️  无法通过 SSH 连接服务器"
    echo ""
    echo "可能的原因:"
    echo "  1. UCloud 安全组未开放 22 端口（SSH）"
    echo "  2. UCloud 安全组未开放 8000 端口（Web Admin API）"
    echo "  3. UCloud 安全组未开放 8080 端口（MiniApp API）"
    echo "  4. 服务器网络问题"
    echo ""
    echo "🔧 解决方案:"
    echo "  1. 登录 UCloud 控制台: https://console.ucloud.cn/"
    echo "  2. 找到云主机: UHost-Sale (uhost-lilim17se6os)"
    echo "  3. 配置安全组，开放以下端口:"
    echo "     • TCP 22 (SSH)"
    echo "     • TCP 8000 (Web Admin API)"
    echo "     • TCP 8080 (MiniApp API)"
    echo "  4. 保存规则并等待 1-2 分钟生效"
fi

echo ""

