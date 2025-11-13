#!/bin/bash
# 健康检查脚本
# 使用方式: ./deploy/scripts/healthcheck.sh

set -e

echo "🔍 开始健康检查..."

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_service() {
    local name=$1
    local url=$2
    
    echo -n "检查 $name... "
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 正常${NC}"
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        return 1
    fi
}

# 检查 Web Admin
check_service "Web Admin" "http://localhost:8000/healthz"

# 检查 MiniApp API
check_service "MiniApp API" "http://localhost:8080/healthz"

# 检查前端控制台
check_service "前端控制台" "http://localhost:3001"

# 检查数据库（如果使用 PostgreSQL）
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
    echo -n "检查 PostgreSQL... "
    if python -c "from models.db import engine; engine.connect(); print('OK')" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 正常${NC}"
    else
        echo -e "${RED}❌ 失败${NC}"
    fi
fi

# 检查 Prometheus（如果运行）
if curl -f -s "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
    echo -e "Prometheus: ${GREEN}✅ 正常${NC}"
else
    echo -e "Prometheus: ${YELLOW}⚠️  未运行（可选）${NC}"
fi

# 检查 Grafana（如果运行）
if curl -f -s "http://localhost:3000/api/health" > /dev/null 2>&1; then
    echo -e "Grafana: ${GREEN}✅ 正常${NC}"
else
    echo -e "Grafana: ${YELLOW}⚠️  未运行（可选）${NC}"
fi

echo ""
echo "✅ 健康检查完成"

