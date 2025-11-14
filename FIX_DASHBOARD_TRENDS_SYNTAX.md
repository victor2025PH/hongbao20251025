# 修复 DashboardTrends 语法错误

> **错误**: `Expected '{', got 'interface'`  
> **位置**: `frontend-next/src/lib/api.ts:19:8`

---

## 🔍 问题原因

`interface extends Array<{...}> {}` 语法在 TypeScript 中不正确。应该使用 `type` 来定义数组类型。

**错误的语法**:
```typescript
export interface DashboardTrends extends Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}> {}
```

---

## ✅ 解决方案

### **正确的语法**

使用 `type` 而不是 `interface`：

```typescript
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>
```

---

## 🔧 在服务器上修复

### **步骤 1: 修复 `frontend-next/src/lib/api.ts`**

```bash
cd /opt/redpacket/frontend-next
nano src/lib/api.ts
```

找到第 19 行，修改为：

**修改前**:
```typescript
export interface DashboardTrends extends Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}> {}
```

**修改后**:
```typescript
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>
```

保存文件（Ctrl+O, Enter, Ctrl+X）

---

### **步骤 2: 验证修复**

```bash
# 检查语法
grep -A 5 "DashboardTrends" src/lib/api.ts

# 应该看到: export type DashboardTrends = Array<{
```

---

### **步骤 3: 重新构建**

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

## 🚀 快速修复命令

在服务器上执行：

```bash
cd /opt/redpacket/frontend-next && \
sed -i 's/export interface DashboardTrends extends Array</export type DashboardTrends = Array</' src/lib/api.ts && \
sed -i 's/}> {}$/}>/' src/lib/api.ts && \
cd /opt/redpacket && \
docker compose -f docker-compose.production.yml build frontend && \
docker compose -f docker-compose.production.yml up -d && \
echo "✅ 修复完成！"
```

---

## 📝 完整的正确类型定义

**`frontend-next/src/lib/api.ts`** (第 19-24 行):
```typescript
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>
```

**`frontend-next/src/mock/dashboard.ts`** (第 16-21 行):
```typescript
  trends: Array<{
    date: string
    users: number
    envelopes: number
    amount: number
  }>
```

---

## 🔍 验证

修复后验证：

```bash
cd /opt/redpacket/frontend-next

# 检查类型定义
grep -A 5 "DashboardTrends" src/lib/api.ts

# 应该看到: export type DashboardTrends = Array<{
# 不应该看到: export interface DashboardTrends extends Array
```

---

*最后更新: 2025-01-XX*

