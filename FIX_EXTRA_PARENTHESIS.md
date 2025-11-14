# 修复多余的右括号错误

> **错误**: `Expected '{', got 'interface'`  
> **位置**: `frontend-next/src/lib/api.ts:26:8`  
> **可能原因**: 第 28 行 `trends?: DashboardTrends)` 有多余的右括号

---

## 🔍 问题诊断

从错误信息看，第 28 行显示 `trends?: DashboardTrends)` 有一个多余的右括号 `)`，这会导致语法错误。

**错误的代码**:
```typescript
trends?: DashboardTrends)  // ❌ 多余的 )
```

**正确的代码**:
```typescript
trends?: DashboardTrends   // ✅ 没有 )
```

---

## ✅ 解决方案

### **步骤 1: 检查文件内容**

```bash
cd /opt/redpacket/frontend-next

# 查看第 26-30 行
sed -n '26,30p' src/lib/api.ts
```

如果看到 `trends?: DashboardTrends)`，说明有多余的右括号。

---

### **步骤 2: 修复**

#### 方法 A: 手动修复（推荐）

```bash
nano src/lib/api.ts
```

找到第 28 行，确保是：

```typescript
  trends?: DashboardTrends
```

**注意**: 后面不能有 `)`

保存文件（Ctrl+O, Enter, Ctrl+X）

#### 方法 B: 使用命令修复

```bash
# 移除多余的右括号
sed -i 's/trends?: DashboardTrends)/trends?: DashboardTrends/' src/lib/api.ts

# 验证修复
sed -n '26,30p' src/lib/api.ts
```

---

### **步骤 3: 验证修复**

```bash
# 检查修复后的内容
sed -n '26,30p' src/lib/api.ts

# 应该看到:
# export interface DashboardData {
#   stats: DashboardStats
#   trends?: DashboardTrends
#   recent_tasks?: {
```

---

### **步骤 4: 重新构建**

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

## 🔧 完整修复命令

```bash
cd /opt/redpacket/frontend-next && \
sed -i 's/trends?: DashboardTrends)/trends?: DashboardTrends/' src/lib/api.ts && \
sed -i 's/[[:cntrl:]]//g' src/lib/api.ts && \
sed -i 's/\r$//' src/lib/api.ts && \
sed -n '26,30p' src/lib/api.ts && \
cd /opt/redpacket && \
docker compose -f docker-compose.production.yml build frontend && \
docker compose -f docker-compose.production.yml up -d && \
echo "✅ 修复完成！"
```

---

## 📝 正确的完整定义（第 19-38 行）

确保文件内容是：

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
- 第 24 行: `}>`
- 第 25 行: 空行
- 第 26 行: `export interface DashboardData {`
- 第 28 行: `trends?: DashboardTrends`（**没有右括号**）

---

*最后更新: 2025-01-XX*

