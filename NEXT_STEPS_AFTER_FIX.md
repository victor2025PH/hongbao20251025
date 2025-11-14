# TypeScript 修复后的下一步操作

> **状态**: ✅ TypeScript 错误已修复（`isMock` 属性已添加）

---

## 🎯 当前状态

- ✅ `src/lib/api.ts` - 已包含 `isMock?: boolean`
- ✅ `src/mock/dashboard.ts` - 已包含 `isMock?: boolean`

---

## 🚀 下一步操作

### **步骤 1: 重新构建前端镜像**

```bash
cd /opt/redpacket
docker compose -f docker-compose.production.yml build frontend
```

**预期输出**: 构建成功，无 TypeScript 错误

---

### **步骤 2: 启动所有服务**

```bash
docker compose -f docker-compose.production.yml up -d
```

**预期输出**: 所有容器启动成功

---

### **步骤 3: 验证服务状态**

```bash
# 查看容器状态
docker compose -f docker-compose.production.yml ps

# 应该看到所有服务都是 "Up" 状态
```

---

### **步骤 4: 测试健康检查**

```bash
# 后端健康检查
curl http://localhost:8000/healthz

# 预期输出: {"ok": true, "ts": "..."}

# 前端访问（如果端口 3001 开放）
curl http://localhost:3001
```

---

### **步骤 5: 启动 systemd 服务（可选）**

如果之前配置了 systemd 服务，现在应该也能正常启动：

```bash
sudo systemctl restart redpacket.service
sudo systemctl status redpacket.service
```

---

## 🔍 如果构建仍然失败

### **检查构建日志**

```bash
# 查看详细的构建输出
docker compose -f docker-compose.production.yml build frontend --no-cache 2>&1 | tee build.log

# 查看错误信息
grep -i error build.log
```

### **常见问题**

1. **缓存问题**: 使用 `--no-cache` 重新构建
2. **依赖问题**: 检查 `package.json` 和 `package-lock.json`
3. **Node 版本**: 确保 Dockerfile 使用正确的 Node 版本

---

## 📋 完整命令序列

```bash
# 1. 进入项目目录
cd /opt/redpacket

# 2. 重新构建前端（清除缓存）
docker compose -f docker-compose.production.yml build frontend --no-cache

# 3. 启动所有服务
docker compose -f docker-compose.production.yml up -d

# 4. 查看服务状态
docker compose -f docker-compose.production.yml ps

# 5. 查看日志（如果有问题）
docker compose -f docker-compose.production.yml logs frontend

# 6. 测试健康检查
curl http://localhost:8000/healthz

# 7. 启动 systemd 服务（如果配置了）
sudo systemctl restart redpacket.service
sudo systemctl status redpacket.service
```

---

## ✅ 成功标志

- ✅ Docker 构建成功，无 TypeScript 错误
- ✅ 所有容器状态为 "Up"
- ✅ `/healthz` 返回 `{"ok": true}`
- ✅ systemd 服务状态为 "active (running)"

---

*最后更新: 2025-01-XX*

