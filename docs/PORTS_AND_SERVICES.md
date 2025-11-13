# 端口与服务说明

本文档说明项目中各个服务使用的端口及其职责。

## 端口分配

### 8000 - 统一 FastAPI 后端

**服务类型**: FastAPI Web 应用  
**服务名称**: Web Admin + API Server  
**启动命令**: 
```bash
uvicorn web_admin.main:app --host 0.0.0.0 --port 8000
```

**职责**:
- 提供 Web Admin 管理界面（HTML 页面）
- 提供 REST API 接口（JSON 响应）
- 同时服务聊天 AI 和红包系统

**主要路由**:
- `/admin/dashboard` - 管理后台仪表盘（HTML）
- `/admin/api/v1/dashboard/stats` - 仪表盘统计数据 API（需要认证）
- `/admin/api/v1/dashboard/stats/public` - 仪表盘统计数据 API（无需认证）
- `/admin/api/v1/audit` - 审计日志 API
- `/healthz` - 健康检查端点

**注意事项**:
- ⚠️ **只允许一个进程监听 8000 端口**
- 不要启动多个 Web Admin 进程，会导致端口冲突
- 如果需要单独的管理端，请使用其他端口（如 8001 或 8080）

---

### 8080 - Miniapp API 服务

**服务类型**: FastAPI API Server  
**服务名称**: Miniapp Backend  
**启动命令**: 
```bash
uvicorn miniapp.main:app --host 0.0.0.0 --port 8080
```

**职责**:
- 提供 Telegram MiniApp 相关 API
- 公开群组管理 API
- 用户认证和授权

**主要路由**:
- `/v1/groups/public` - 公开群组列表
- `/v1/groups/public/{id}` - 群组详情
- `/v1/groups/public/activities` - 群组活动列表
- `/api/auth/login` - 用户登录

---

### 3000 - 聊天 AI 前端（如适用）

**服务类型**: Next.js 前端应用  
**服务名称**: Chat AI Frontend  
**启动命令**: 
```bash
cd chat-ai-frontend
npm run dev
```

**职责**:
- 聊天 AI 用户界面
- 与 8000 端口后端通信

---

### 3001 - 红包系统前端

**服务类型**: Next.js 前端应用  
**服务名称**: Red Packet System Frontend  
**启动命令**: 
```bash
cd frontend-next
npm run dev
```

**职责**:
- 红包系统管理界面
- Dashboard 数据展示
- 群组管理界面
- 系统设置

**API 配置**:
- Web Admin API: `http://localhost:8000`（Dashboard、审计日志）
- Miniapp API: `http://localhost:8080`（群组相关）

---

## 服务启动顺序

1. **后端服务**（8000 和 8080）:
   ```bash
   # 启动 Web Admin（8000）
   uvicorn web_admin.main:app --host 0.0.0.0 --port 8000
   
   # 启动 Miniapp API（8080）
   uvicorn miniapp.main:app --host 0.0.0.0 --port 8080
   ```

2. **前端服务**（3001）:
   ```bash
   cd frontend-next
   npm run dev
   ```

---

## 常见问题

### Q: 为什么不能启动多个 8000 端口的服务？

A: 操作系统不允许同一个端口被多个进程监听。如果尝试启动第二个服务，会收到 "Address already in use" 错误。

### Q: 如何检查端口是否被占用？

**Windows**:
```powershell
netstat -ano | findstr :8000
```

**Linux/Mac**:
```bash
lsof -i :8000
```

### Q: 如果需要单独的管理端怎么办？

A: 可以：
1. 使用其他端口（如 8001）启动管理端
2. 修改前端配置指向新的端口
3. 在本文档中更新端口说明

### Q: Dashboard 显示 404 错误怎么办？

A: 检查以下几点：
1. 确认 8000 端口的后端服务正在运行
2. 访问 `http://localhost:8000/healthz` 确认服务健康
3. 检查前端调用的 API 路径是否正确（`/admin/api/v1/dashboard/stats` 或 `/admin/api/v1/dashboard/stats/public`）
4. 如果使用需要认证的接口，请先登录 `http://localhost:8000/admin/login`

---

## 更新日志

- 2024-XX-XX: 初始版本，明确端口分配和服务职责
- 2024-XX-XX: 添加无需认证的 Dashboard 统计接口

