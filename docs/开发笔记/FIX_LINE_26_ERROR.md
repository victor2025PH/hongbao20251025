# 修复第 26 行语法错误

> **错误**: `Expected '{', got 'interface'`  
> **位置**: `frontend-next/src/lib/api.ts:26:8`  
> **问题**: `export interface DashboardData {` 后面有异常字符

---

## 🔍 问题诊断

从错误信息看，第 26 行的 `export interface DashboardData {` 后面可能有异常字符（如 `build`），导致语法错误。

---

## ✅ 解决方案

### **步骤 1: 检查文件内容**

```bash
cd /opt/redpacket/frontend-next

# 查看第 24-30 行的内容
sed -n '24,30p' src/lib/api.ts

# 应该看到:
# }>
# 
# export interface DashboardData {
#   stats: DashboardStats
#   trends?: DashboardTrends
#   recent_tasks?: {
```

如果看到 `export interface DashboardData {build` 或其他异常字符，说明文件损坏。

---

### **步骤 2: 手动修复**

```bash
nano src/lib/api.ts
```

找到第 26 行，确保内容是：

```typescript
export interface DashboardData {
```

**注意**:
- 第 26 行必须是：`export interface DashboardData {`
- `{` 后面不能有任何字符（除了换行）
- 确保第 25 行是空行

保存文件（Ctrl+O, Enter, Ctrl+X）

---

### **步骤 3: 验证修复**

```bash
# 检查第 24-30 行
sed -n '24,30p' src/lib/api.ts

# 应该看到:
# }>
# 
# export interface DashboardData {
#   stats: DashboardStats
#   trends?: DashboardTrends
```

---

### **步骤 4: 重新构建**

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

## 🔧 快速修复命令

如果文件确实损坏，可以使用以下命令修复：

```bash
cd /opt/redpacket/frontend-next

# 备份
cp src/lib/api.ts src/lib/api.ts.bak3

# 修复第 26 行（移除异常字符）
sed -i '26s/export interface DashboardData {.*/export interface DashboardData {/' src/lib/api.ts

# 或者使用更精确的方法
sed -i '26s/{build/{/' src/lib/api.ts
sed -i '26s/{.*{/{/' src/lib/api.ts

# 验证
sed -n '24,30p' src/lib/api.ts
```

---

## 📝 正确的文件内容（第 19-30 行）

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
```

**关键点**:
- 第 19 行: `export type DashboardTrends = Array<{`
- 第 24 行: `}>`
- 第 25 行: 空行
- 第 26 行: `export interface DashboardData {`（后面不能有其他字符）

---

## 🚀 完整修复流程

```bash
cd /opt/redpacket/frontend-next

# 1. 检查文件
sed -n '19,30p' src/lib/api.ts

# 2. 备份
cp src/lib/api.ts src/lib/api.ts.bak

# 3. 修复第 26 行
sed -i '26s/{.*{/{/' src/lib/api.ts

# 4. 验证
sed -n '24,30p' src/lib/api.ts

# 5. 重新构建
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
```

---

*最后更新: 2025-01-XX*

