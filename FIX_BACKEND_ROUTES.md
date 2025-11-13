# 修复后端路由问题

## 🔍 发现的问题

1. **多个 uvicorn 进程同时运行** - 导致路由冲突
2. **/healthz 返回 404** - 虽然代码中已定义，但服务可能运行的是旧版本
3. **/admin/api/v1/dashboard/public 返回 404** - 路由可能未正确注册

## ✅ 已执行的修复

1. ✅ 停止了所有旧的 uvicorn 进程
2. ✅ 创建了启动脚本 `start_backend.bat`

## 🚀 手动启动步骤

### 方法 1: 使用启动脚本（推荐）

1. **打开新的 PowerShell 或 CMD 终端**
2. **运行启动脚本:**
   ```bash
   .\start_backend.bat
   ```
3. **等待服务启动完成**（看到 "Application startup complete"）
4. **测试端点:**
   - http://localhost:8000/healthz
   - http://localhost:8000/admin/api/v1/dashboard/public

### 方法 2: 手动启动

1. **打开新的终端窗口**
2. **进入项目目录:**
   ```bash
   cd "E:\002-工作文件\重要程序\红包系统机器人\037重新开发新功能"
   ```
3. **启动服务:**
   ```bash
   python -m uvicorn web_admin.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. **等待服务启动完成**

## 🔍 验证服务是否正常

启动后，在浏览器或另一个终端中测试：

```bash
# 测试健康检查
curl http://localhost:8000/healthz

# 测试 Dashboard API
curl http://localhost:8000/admin/api/v1/dashboard/public
```

**预期响应:**
- `/healthz`: `{"ok": true, "ts": "2025-01-XX..."}`
- `/admin/api/v1/dashboard/public`: `{"user_count": ..., "active_envelopes": ...}`

## ⚠️ 如果仍然返回 404

### 检查 1: 确认服务使用的是最新代码

1. **停止服务**（在运行服务的终端按 `Ctrl+C`）
2. **确认代码已保存**
3. **重新启动服务**

### 检查 2: 查看服务启动日志

启动服务时，应该看到类似输出：
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

如果有错误信息，请检查：
- 导入错误
- 语法错误
- 依赖缺失

### 检查 3: 确认路由注册顺序

路由应该在 `web_admin/main.py` 的 `create_app()` 函数中注册。

关键路由：
- `/healthz` - 定义在 `web_admin/main.py` 第 185 行
- `/admin/api/v1/dashboard` - 定义在 `web_admin/controllers/dashboard.py`，通过 `dashboard_router` 注册

## 📝 路由配置说明

### Dashboard 路由

- **路由前缀**: `/admin`（在 `web_admin/controllers/dashboard.py` 第 22 行定义）
- **完整路径**: `/admin/api/v1/dashboard` 和 `/admin/api/v1/dashboard/public`
- **注册位置**: `web_admin/main.py` 第 232 行

### 健康检查路由

- **路径**: `/healthz`
- **定义位置**: `web_admin/main.py` 第 185 行
- **响应**: `{"ok": true, "ts": "ISO时间戳"}`

## 💡 常见问题

### Q: 为什么有多个进程在运行？

**A:** 可能是之前启动的服务没有正确停止，或者有多个终端窗口同时运行了服务。

**解决方案:** 
1. 停止所有相关进程
2. 只在一个终端窗口启动服务

### Q: 服务启动后立即退出？

**A:** 可能是代码有错误或依赖缺失。

**解决方案:**
1. 查看错误信息
2. 检查 `requirements.txt` 中的依赖是否已安装
3. 运行 `pip install -r requirements.txt`

### Q: 端口 8000 被占用？

**A:** 其他程序可能正在使用端口 8000。

**解决方案:**
1. 查找占用端口的进程: `netstat -ano | findstr :8000`
2. 停止占用端口的进程
3. 或使用其他端口: `--port 8001`

---

*最后更新: 2025-01-XX*

