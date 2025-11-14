# 使用 Python 直接修复 src/lib/api.ts

> **无需脚本文件，直接在服务器上执行**

---

## 🚀 一键修复命令

在服务器上直接执行以下命令：

```bash
cd /opt/redpacket/frontend-next

python3 << 'PYTHON_EOF'
import re

file_path = 'src/lib/api.ts'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 备份
with open(file_path + '.bak', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# 构建新内容
new_lines = lines[:18]  # 保留前 18 行

# 添加修复后的定义（完全重写）
new_lines.extend([
    'export type DashboardTrends = Array<{\n',
    '  date: string\n',
    '  users: number\n',
    '  envelopes: number\n',
    '  amount: number\n',
    '}>\n',
    '\n',
    'export interface DashboardData {\n',
    '  stats: DashboardStats\n',
    '  trends?: DashboardTrends\n',
    '  recent_tasks?: {\n',
    '    id: string\n',
    '    task: string\n',
    '    status: \'success\' | \'pending\' | \'failed\'\n',
    '    group: string\n',
    '    amount: string\n',
    '    time: string\n',
    '  }[]\n',
    '  isMock?: boolean\n',
    '}\n',
])

# 添加剩余行（从第 39 行开始）
if len(lines) > 38:
    new_lines.extend(lines[38:])

# 写回文件（使用 LF 行尾符）
with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(new_lines)

print("✅ 文件已修复")
print(f"   备份文件: {file_path}.bak")
PYTHON_EOF
```

---

## 🔍 验证修复

```bash
# 检查修复后的内容
cat -A src/lib/api.ts | sed -n '19,38p'

# 应该看到:
# export type DashboardTrends = Array<{$
#   date: string$
#   users: number$
#   envelopes: number$
#   amount: number$
# }>$
# $
# export interface DashboardData {$
#   stats: DashboardStats$
#   trends?: DashboardTrends$
#   ...
```

---

## 🚀 重新构建

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

## 📝 如果 Python 不可用

使用 sed 方法：

```bash
cd /opt/redpacket/frontend-next

# 备份
cp src/lib/api.ts src/lib/api.ts.bak

# 精确修复第 19-38 行
sed -i '19,38d' src/lib/api.ts

# 在第 18 行后插入新内容
sed -i '18a\
export type DashboardTrends = Array<{\
  date: string\
  users: number\
  envelopes: number\
  amount: number\
}>\
\
export interface DashboardData {\
  stats: DashboardStats\
  trends?: DashboardTrends\
  recent_tasks?: {\
    id: string\
    task: string\
    status: '\''success'\'' | '\''pending'\'' | '\''failed'\''\
    group: string\
    amount: string\
    time: string\
  }[]\
  isMock?: boolean\
}' src/lib/api.ts

# 验证
sed -n '19,38p' src/lib/api.ts
```

---

*最后更新: 2025-01-XX*

