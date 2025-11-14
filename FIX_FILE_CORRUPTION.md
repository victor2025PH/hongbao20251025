# 修复文件损坏问题

> **错误**: `Expected '{', got 'DashboardTrends'`  
> **可能原因**: sed 命令执行时文件被截断或格式错误

---

## 🔍 问题诊断

从错误信息看，`Array<` 后面可能缺少 `{` 或者文件被截断。需要检查文件完整性。

---

## ✅ 解决方案

### **步骤 1: 检查文件内容**

```bash
cd /opt/redpacket/frontend-next

# 查看第 19 行附近的内容
sed -n '17,25p' src/lib/api.ts

# 或者查看完整的 DashboardTrends 定义
grep -A 10 "DashboardTrends" src/lib/api.ts
```

**应该看到**:
```typescript
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>
```

**如果看到**:
- `Array<d` - 文件被截断
- `Array<` 后面没有 `{` - 格式错误
- 其他异常字符 - 文件损坏

---

### **步骤 2: 恢复备份（如果有）**

```bash
# 检查是否有备份
ls -la src/lib/api.ts*

# 如果有备份，恢复
cp src/lib/api.ts.bak src/lib/api.ts
```

---

### **步骤 3: 手动修复（最可靠）**

```bash
cd /opt/redpacket/frontend-next
nano src/lib/api.ts
```

找到第 19 行，确保完整的内容是：

```typescript
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>
```

**关键点**:
- `export type`（不是 `export interface`）
- `Array<{`（`<` 后面必须是 `{`）
- 最后是 `}>`（不是 `}> {}`）

保存文件（Ctrl+O, Enter, Ctrl+X）

---

### **步骤 4: 验证修复**

```bash
# 检查语法
grep -A 6 "DashboardTrends" src/lib/api.ts

# 应该看到完整的定义
```

---

## 🔧 完整修复命令

如果文件确实损坏，可以使用以下命令完全重写该部分：

```bash
cd /opt/redpacket/frontend-next

# 备份
cp src/lib/api.ts src/lib/api.ts.bak2

# 使用 sed 精确替换（找到 DashboardTrends 定义并替换）
# 方法 1: 如果知道确切行号
sed -i '19s/.*/export type DashboardTrends = Array<{/' src/lib/api.ts
sed -i '20s/.*/  date: string/' src/lib/api.ts
sed -i '21s/.*/  users: number/' src/lib/api.ts
sed -i '22s/.*/  envelopes: number/' src/lib/api.ts
sed -i '23s/.*/  amount: number/' src/lib/api.ts
sed -i '24s/.*/}>/' src/lib/api.ts

# 方法 2: 使用 Python（如果可用）
python3 << 'EOF'
import re

with open('src/lib/api.ts', 'r') as f:
    content = f.read()

# 替换 DashboardTrends 定义
pattern = r'export\s+(?:type|interface)\s+DashboardTrends[^}]*\}'
replacement = '''export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('src/lib/api.ts', 'w') as f:
    f.write(content)
EOF

# 验证
grep -A 6 "DashboardTrends" src/lib/api.ts
```

---

## 🚀 推荐操作流程

1. **检查文件内容**:
   ```bash
   sed -n '17,25p' src/lib/api.ts
   ```

2. **如果文件损坏，手动修复**:
   ```bash
   nano src/lib/api.ts
   # 编辑第 19-24 行
   ```

3. **验证修复**:
   ```bash
   grep -A 6 "DashboardTrends" src/lib/api.ts
   ```

4. **重新构建**:
   ```bash
   cd /opt/redpacket
   docker compose -f docker-compose.production.yml build frontend
   ```

---

## 📝 正确的完整定义

确保 `src/lib/api.ts` 第 19-24 行是：

```typescript
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>
```

**注意**:
- 第 19 行: `export type DashboardTrends = Array<{`
- 第 20-23 行: 字段定义
- 第 24 行: `}>`

---

*最后更新: 2025-01-XX*

