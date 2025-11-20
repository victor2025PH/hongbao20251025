# 直接修复 src/lib/api.ts（无需脚本）

> **问题**: 文件格式看起来正确，但构建仍然失败

---

## 🔍 从检查结果看

从 `cat -A` 的输出看，文件格式是正确的：
- `trends?: DashboardTrends $` - `?:` 紧挨着 ✅
- `recent_tasks?: {$` - 格式正确 ✅
- `isMock?: boolean$` - 格式正确 ✅

但构建仍然失败，可能的问题：
1. **第 24-25 行之间有问题**：`}>` 和空行之间可能有隐藏字符
2. **第 25 行空行有问题**：空行可能有控制字符
3. **Turbopack 解析器问题**：可能需要完全重写相关部分

---

## ✅ 直接修复方案

### **方案 1: 在 nano 中完全重写（最可靠）**

```bash
cd /opt/redpacket/frontend-next
nano src/lib/api.ts
```

**步骤**:
1. 将光标移到第 19 行开头
2. 按 `Ctrl+K` 20 次（删除第 19-38 行）
3. **完全手动输入**以下内容（不要复制粘贴）：

```typescript
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>

export interface DashboardData {
  stats: DashboardStats
  trends?: DashboardTrends
  recent_tasks?: {
    id: string
    task: string
    status: 'success' | 'pending' | 'failed'
    group: string
    amount: string
    time: string
  }[]
  isMock?: boolean
}
```

4. 保存文件（Ctrl+O, Enter, Ctrl+X）

---

### **方案 2: 使用 sed 精确修复**

```bash
cd /opt/redpacket/frontend-next

# 备份
cp src/lib/api.ts src/lib/api.ts.bak

# 清理第 24-26 行之间的所有字符
sed -i '24s/.*/}>/' src/lib/api.ts
sed -i '25s/.*//' src/lib/api.ts  # 确保是空行
sed -i '26s/.*/export interface DashboardData {/' src/lib/api.ts

# 清理所有控制字符
sed -i 's/[[:cntrl:]]//g' src/lib/api.ts
sed -i 's/\r$//' src/lib/api.ts

# 验证
cat -A src/lib/api.ts | sed -n '24,30p'
```

---

### **方案 3: 使用 Python 直接修复**

```bash
cd /opt/redpacket/frontend-next

python3 << 'EOF'
# 读取文件
with open('src/lib/api.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复第 19-38 行
new_lines = lines[:18]  # 保留前 18 行

# 添加修复后的定义
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

# 添加剩余行
if len(lines) > 38:
    new_lines.extend(lines[38:])

# 写回文件
with open('src/lib/api.ts', 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(new_lines)

print("✅ 文件已修复")
EOF
```

---

### **方案 4: 检查并修复第 24-26 行**

```bash
cd /opt/redpacket/frontend-next

# 查看第 24-26 行的详细内容
cat -A src/lib/api.ts | sed -n '24,26p'

# 如果第 24 行不是 }>，修复它
sed -i '24s/.*/}>/' src/lib/api.ts

# 如果第 25 行不是空行，修复它
sed -i '25s/.*//' src/lib/api.ts

# 如果第 26 行有问题，修复它
sed -i '26s/.*/export interface DashboardData {/' src/lib/api.ts

# 清理控制字符
sed -i 's/[[:cntrl:]]//g' src/lib/api.ts
sed -i 's/\r$//' src/lib/api.ts

# 验证
cat -A src/lib/api.ts | sed -n '24,30p'
```

---

## 🚀 推荐操作流程

1. **先检查第 24-26 行**:
   ```bash
   cat -A src/lib/api.ts | sed -n '24,26p'
   ```

2. **如果看到异常字符，使用方案 2 或 3 修复**

3. **如果仍然失败，使用方案 1（手动重写）**

4. **重新构建**:
   ```bash
   cd /opt/redpacket
   docker compose -f docker-compose.production.yml build frontend
   ```

---

## 📝 正确的完整内容（第 19-38 行）

```typescript
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>

export interface DashboardData {
  stats: DashboardStats
  trends?: DashboardTrends
  recent_tasks?: {
    id: string
    task: string
    status: 'success' | 'pending' | 'failed'
    group: string
    amount: string
    time: string
  }[]
  isMock?: boolean
}
```

**关键点**:
- 第 19 行: `export type DashboardTrends = Array<{`
- 第 24 行: `}>`（没有其他字符）
- 第 25 行: 完全空行（没有任何字符，包括空格）
- 第 26 行: `export interface DashboardData {`（`{` 后面不能有其他字符）

---

*最后更新: 2025-01-XX*

