# 修复服务器上的 TypeScript 错误

> **错误**: `Property 'isMock' does not exist on type 'DashboardData'`  
> **位置**: `frontend-next/src/app/page.tsx:216:27`

---

## 🔍 问题原因

服务器上的代码还没有更新，`DashboardData` 接口中缺少 `isMock` 属性。

---

## ✅ 解决方案

### **方案 1: 更新代码（推荐）**

如果使用 Git，更新代码：

```bash
cd /opt/redpacket
git pull origin master
# 或者
git pull origin main
```

然后重新构建：
```bash
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

### **方案 2: 手动修复（如果无法使用 Git）**

在服务器上手动修复类型定义：

#### 步骤 1: 修复 `frontend-next/src/lib/api.ts`

```bash
cd /opt/redpacket/frontend-next
nano src/lib/api.ts
```

找到 `DashboardData` 接口定义（大约第 26 行），修改为：

```typescript
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
  isMock?: boolean  // 标识是否使用 mock 数据
}
```

保存文件（Ctrl+O, Enter, Ctrl+X）

#### 步骤 2: 修复 `frontend-next/src/mock/dashboard.ts`

```bash
nano src/mock/dashboard.ts
```

找到 `DashboardData` 接口定义（大约第 5 行），修改为：

```typescript
export interface DashboardData {
  stats: {
    user_count: number
    active_envelopes: number
    last_7d_amount: string
    last_7d_orders: number
    pending_recharges: number
    success_recharges: number
    since: string
    until: string
  }
  trends: {
    date: string
    users: number
    envelopes: number
    amount: number
  }[]
  recent_tasks: {
    id: string
    task: string
    status: 'success' | 'pending' | 'failed'
    group: string
    amount: string
    time: string
  }[]
  isMock?: boolean  // 标识是否使用 mock 数据
}
```

保存文件

#### 步骤 3: 重新构建

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

### **方案 3: 一键修复脚本**

在服务器上执行以下命令，自动修复：

```bash
cd /opt/redpacket/frontend-next

# 修复 src/lib/api.ts
sed -i '/export interface DashboardData {/,/^}/ {
  /^}$/i\
  isMock?: boolean  // 标识是否使用 mock 数据
}' src/lib/api.ts

# 修复 src/mock/dashboard.ts
sed -i '/export interface DashboardData {/,/^}/ {
  /^}$/i\
  isMock?: boolean  // 标识是否使用 mock 数据
}' src/mock/dashboard.ts

# 验证修复
grep -A 2 "isMock" src/lib/api.ts
grep -A 2 "isMock" src/mock/dashboard.ts

# 重新构建
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d
```

---

### **方案 4: 使用 patch 文件**

如果方案 3 的 sed 命令不工作，可以使用 patch：

```bash
cd /opt/redpacket/frontend-next

# 创建修复补丁
cat > /tmp/fix_isMock.patch << 'EOF'
--- a/src/lib/api.ts
+++ b/src/lib/api.ts
@@ -29,6 +29,7 @@ export interface DashboardData {
     amount: string
     time: string
   }[]
+  isMock?: boolean  // 标识是否使用 mock 数据
 }
 
 export interface AuditLogItem {
--- a/src/mock/dashboard.ts
+++ b/src/mock/dashboard.ts
@@ -27,6 +27,7 @@ export interface DashboardData {
     time: string
   }[]
+  isMock?: boolean  // 标识是否使用 mock 数据
 }
 
 export const MOCK_DASHBOARD: DashboardData = {
EOF

# 应用补丁（需要先检查文件内容是否匹配）
# 如果 patch 命令不可用，使用方案 2 手动修复
```

---

## 🔍 验证修复

修复后，验证：

```bash
cd /opt/redpacket/frontend-next

# 检查类型定义
grep -A 5 "interface DashboardData" src/lib/api.ts | grep isMock
grep -A 5 "interface DashboardData" src/mock/dashboard.ts | grep isMock

# 如果看到 isMock，说明修复成功
```

然后重新构建：

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend --no-cache
docker compose -f docker-compose.production.yml up -d
```

---

## 📝 完整修复流程（推荐）

```bash
cd /opt/redpacket

# 1. 更新代码（如果使用 Git）
git pull origin master || echo "Git pull 失败，使用手动修复"

# 2. 如果 Git pull 失败，手动修复
cd frontend-next

# 修复 src/lib/api.ts
if ! grep -q "isMock" src/lib/api.ts; then
    echo "修复 src/lib/api.ts..."
    # 在 DashboardData 接口的最后一个 } 前添加 isMock 属性
    sed -i '/^  }\]$/a\  isMock?: boolean  // 标识是否使用 mock 数据' src/lib/api.ts
fi

# 修复 src/mock/dashboard.ts
if ! grep -q "isMock" src/mock/dashboard.ts; then
    echo "修复 src/mock/dashboard.ts..."
    sed -i '/^  }\]$/a\  isMock?: boolean  // 标识是否使用 mock 数据' src/mock/dashboard.ts
fi

# 3. 验证修复
echo "验证修复..."
grep "isMock" src/lib/api.ts && echo "✅ src/lib/api.ts 已修复" || echo "❌ src/lib/api.ts 修复失败"
grep "isMock" src/mock/dashboard.ts && echo "✅ src/mock/dashboard.ts 已修复" || echo "❌ src/mock/dashboard.ts 修复失败"

# 4. 重新构建
cd /opt/redpacket
echo "重新构建前端..."
docker compose -f docker-compose.production.yml build frontend
docker compose -f docker-compose.production.yml up -d

# 5. 检查服务状态
docker compose -f docker-compose.production.yml ps
```

---

## 🚀 快速修复命令（一键执行）

在服务器上执行：

```bash
cd /opt/redpacket/frontend-next && \
sed -i '/^  }\]$/a\  isMock?: boolean  // 标识是否使用 mock 数据' src/lib/api.ts && \
sed -i '/^  }\]$/a\  isMock?: boolean  // 标识是否使用 mock 数据' src/mock/dashboard.ts && \
cd /opt/redpacket && \
docker compose -f docker-compose.production.yml build frontend && \
docker compose -f docker-compose.production.yml up -d && \
echo "✅ 修复完成！"
```

---

*最后更新: 2025-01-XX*

