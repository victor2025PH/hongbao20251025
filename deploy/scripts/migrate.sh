#!/bin/bash
# 数据库迁移脚本
# 使用方式: ./deploy/scripts/migrate.sh

set -e

echo "🔄 开始数据库迁移..."

# 检查环境变量
if [ -z "$DATABASE_URL" ]; then
    echo "❌ 错误: DATABASE_URL 环境变量未设置"
    exit 1
fi

# 激活虚拟环境（如果使用虚拟环境）
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 执行数据库初始化（使用现有的 init_db() 机制）
echo "📦 初始化数据库结构..."
python -c "
from models.db import init_db
try:
    init_db()
    print('✅ 数据库初始化成功')
except Exception as e:
    print(f'❌ 数据库初始化失败: {e}')
    exit(1)
"

# 检查是否有 Alembic（可选，如果项目使用 Alembic）
if [ -d "alembic" ] && command -v alembic &> /dev/null; then
    echo "📦 执行 Alembic 迁移..."
    alembic upgrade head
    echo "✅ Alembic 迁移完成"
else
    echo "ℹ️  未检测到 Alembic，跳过 Alembic 迁移"
fi

# 验证数据库连接
echo "🔍 验证数据库连接..."
python -c "
from models.db import engine
try:
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✅ 数据库连接正常')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
"

echo "✅ 数据库迁移完成"

