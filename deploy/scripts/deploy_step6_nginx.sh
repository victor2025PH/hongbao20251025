#!/bin/bash
# 部署步骤 6: 配置 Nginx

set -e

echo "🌐 开始配置 Nginx..."
echo ""

# 检查 Nginx 配置目录
if [ ! -f "deploy/nginx/nginx.conf" ]; then
    echo "❌ 错误: 未找到 deploy/nginx/nginx.conf"
    exit 1
fi

# 获取域名
read -p "请输入您的域名 (例如: yourdomain.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "⚠️  未输入域名，将使用 IP 地址配置"
    DOMAIN="localhost"
fi

# 复制并修改 Nginx 配置
echo "📝 生成 Nginx 配置..."
sudo cp deploy/nginx/nginx.conf /etc/nginx/sites-available/redpacket
sudo sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/redpacket
echo "✅ Nginx 配置已生成"
echo ""

# 启用配置
echo "🔗 启用 Nginx 配置..."
sudo ln -sf /etc/nginx/sites-available/redpacket /etc/nginx/sites-enabled/
echo "✅ 配置已启用"
echo ""

# 测试配置
echo "🧪 测试 Nginx 配置..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Nginx 配置测试通过"
else
    echo "❌ Nginx 配置测试失败，请检查配置"
    exit 1
fi
echo ""

# 重载 Nginx
echo "🔄 重载 Nginx..."
sudo systemctl reload nginx
echo "✅ Nginx 已重载"
echo ""

# 申请 SSL 证书（如果提供了域名）
if [ "$DOMAIN" != "localhost" ]; then
    read -p "是否申请 Let's Encrypt SSL 证书? (y/n): " apply_ssl
    if [ "$apply_ssl" = "y" ]; then
        read -p "请输入邮箱地址 (用于证书通知): " EMAIL
        echo "🔒 申请 SSL 证书..."
        sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive
        echo "✅ SSL 证书申请完成"
    else
        echo "⏭️  跳过 SSL 证书申请"
    fi
else
    echo "⏭️  使用 localhost，跳过 SSL 证书申请"
fi
echo ""

echo "✅ Nginx 配置完成"
echo ""
echo "下一步: 启动服务"

