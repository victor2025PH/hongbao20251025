# 修复 DashboardTrends 类型定义错误

> **错误**: `Property 'length' does not exist on type 'DashboardTrends'`  
> **位置**: `frontend-next/src/app/page.tsx:248:54`

---

## 🔍 问题原因

`DashboardTrends` 的类型定义不正确，导致无法使用 `.length` 属性。

**错误的定义**:
```typescript
export interface DashboardTrends {
  date: string
  users: number
  envelopes: number
  amount: number
}[]
```

这种写法在 TypeScript 中不正确，应该使用数组类型。

---

## ✅ 解决方案

### **方案 1: 更新代码（推荐）**

如果使用 Git，更新代码：

```bash
cd /opt/redpacket
git pull origin master
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

### **方案 2: 手动修复**

在服务器上修复两个文件：

#### 修复文件 1: `frontend-next/src/lib/api.ts`

```bash
cd /opt/redpacket/frontend-next
nano src/lib/api.ts
```

找到 `DashboardTrends` 接口定义（大约第 19-24 行），修改为：

**修改前**:
```typescript
export interface DashboardTrends {
  date: string
  users: number
  envelopes: number
  amount: number
}[]
```

**修改后**:
```typescript
export interface DashboardTrends extends Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}> {}
```

或者更简单的方式：
```typescript
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>
```

保存文件（Ctrl+O, Enter, Ctrl+X）

#### 修复文件 2: `frontend-next/src/mock/dashboard.ts`

```bash
nano src/mock/dashboard.ts
```

找到 `DashboardData` 接口中的 `trends` 定义（大约第 16-21 行），修改为：

**修改前**:
```typescript
  trends: {
    date: string
    users: number
    envelopes: number
    amount: number
  }[]
```

**修改后**:
```typescript
  trends: Array<{
    date: string
    users: number
    envelopes: number
    amount: number
  }>
```

保存文件

#### 重新构建

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

### **方案 3: 使用 sed 命令快速修复**

```bash
cd /opt/redpacket/frontend-next

# 修复 src/lib/api.ts
sed -i 's/export interface DashboardTrends {/export type DashboardTrends = Array</' src/lib/api.ts
sed -i '/^  date: string$/,/^  }\[\]$/ {
  s/^  }\[\]$/}>/
  s/^  date: string$/  {/
}' src/lib/api.ts

# 修复 src/mock/dashboard.ts
sed -i 's/  }\[\]$/  }>/' src/mock/dashboard.ts

# 验证修复
grep -A 5 "DashboardTrends\|trends:" src/lib/api.ts src/mock/dashboard.ts

# 重新构建
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

## 🔍 验证修复

修复后验证：

```bash
cd /opt/redpacket/frontend-next

# 检查类型定义
grep -A 3 "DashboardTrends" src/lib/api.ts
grep -A 3 "trends:" src/mock/dashboard.ts

# 应该看到 Array<{ 或 extends Array< 而不是 }[]
```

---

## 📝 完整修复流程

```bash
cd /opt/redpacket/frontend-next

# 1. 修复 src/lib/api.ts
cat > /tmp/fix_trends_api.txt << 'EOF'
export type DashboardTrends = Array<{
  date: string
  users: number
  envelopes: number
  amount: number
}>
EOF

# 手动编辑或使用 sed（根据实际情况调整）
# 这里提供手动编辑的指导

# 2. 修复 src/mock/dashboard.ts
# 同样需要手动编辑

# 3. 验证
grep "DashboardTrends\|trends:" src/lib/api.ts src/mock/dashboard.ts

# 4. 重新构建
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend --no-cache
docker compose -f docker-compose.production.yml up -d
```

---

## 🚀 推荐操作

**最简单的方法**：手动编辑两个文件，将 `}[]` 改为 `}>`，并在 `DashboardTrends` 接口定义中使用 `Array<{...}>` 或 `extends Array<{...}>`。

---

*最后更新: 2025-01-XX*

