#!/bin/bash
# 尝试配置安全组（检查是否有 UCloud CLI）

server="ubuntu@165.154.233.55"
projectDir="/opt/redpacket"

echo ""
echo "===================================="
echo "🔧 配置安全组规则"
echo "===================================="
echo ""

ssh -o StrictHostKeyChecking=no "$server" << 'REMOTE_SCRIPT'
cd /opt/redpacket

echo "===================================="
echo "1️⃣ 检查是否有云服务商 CLI 工具"
echo "===================================="

# 检查 UCloud CLI
if command -v ucloud >/dev/null 2>&1; then
    echo "✅ 发现 UCloud CLI"
    ucloud version
    echo ""
    echo "尝试配置安全组规则..."
    # UCloud CLI 配置命令（需要认证）
    # ucloud firewall create-firewall --name redpacket-api --protocol tcp --port 8000,8080
else
    echo "ℹ️  未发现 UCloud CLI"
    echo "   需要使用控制台手动配置"
fi

# 检查阿里云 CLI
if command -v aliyun >/dev/null 2>&1; then
    echo "✅ 发现阿里云 CLI"
fi

# 检查腾讯云 CLI
if command -v tccli >/dev/null 2>&1; then
    echo "✅ 发现腾讯云 CLI"
fi

# 检查 AWS CLI
if command -v aws >/dev/null 2>&1; then
    echo "✅ 发现 AWS CLI"
fi

echo ""

echo "===================================="
echo "2️⃣ 验证服务器端配置"
echo "===================================="

echo "检查防火墙状态："
if command -v ufw >/dev/null 2>&1; then
    echo "ufw 防火墙状态："
    sudo ufw status | grep -E "8000|8080" || echo "  未找到规则"
fi

echo ""
echo "检查端口监听："
netstat -tlnp 2>/dev/null | grep -E ":8000|:8080" || ss -tlnp 2>/dev/null | grep -E ":8000|:8080"
echo ""

echo "===================================="
echo "3️⃣ 测试服务可用性"
echo "===================================="

echo "测试 Web Admin API (本地):"
if curl -s --max-time 5 http://127.0.0.1:8000/healthz > /dev/null 2>&1; then
    echo "✅ Web Admin API 本地访问正常"
    curl -s http://127.0.0.1:8000/healthz | head -1
else
    echo "❌ Web Admin API 本地访问失败"
fi
echo ""

echo "测试 MiniApp API (本地):"
if curl -s --max-time 5 http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
    echo "✅ MiniApp API 本地访问正常"
    curl -s http://127.0.0.1:8080/healthz | head -1
else
    echo "❌ MiniApp API 本地访问失败"
fi
echo ""

echo "===================================="
echo "4️⃣ 生成安全组配置说明"
echo "===================================="

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "165.154.233.55")

cat > /tmp/security_group_config.md << EOF
# 安全组配置说明

## UCloud 控制台配置步骤

### 1. 登录 UCloud 控制台
访问：https://console.ucloud.cn/

### 2. 找到云主机
- 进入"云主机 UHost"页面
- 找到云主机：**UHost-Sale**
- 资源ID：**uhost-lilim17se6os**

### 3. 配置安全组规则
点击云主机 → 详情 → 安全组 → 配置规则

### 4. 添加入站规则

**规则 1: Web Admin API**
- 方向：**入站**
- 协议：**TCP**
- 端口：**8000**
- 来源：**0.0.0.0/0**
- 动作：**允许**
- 优先级：**默认**
- 备注：Web Admin API

**规则 2: MiniApp API**
- 方向：**入站**
- 协议：**TCP**
- 端口：**8080**
- 来源：**0.0.0.0/0**
- 动作：**允许**
- 优先级：**默认**
- 备注：MiniApp API

### 5. 保存规则

### 6. 测试访问
- Web Admin API: http://$PUBLIC_IP:8000/healthz
- MiniApp API: http://$PUBLIC_IP:8080/healthz

EOF

echo "✅ 配置说明已生成：/tmp/security_group_config.md"
echo ""

REMOTE_SCRIPT

