# 数据库同步问题修复总结

## ✅ 修复完成

### 问题根源

1. **数据库文件分离**：
   - `bot` 和 `web_admin` 容器各自使用独立的 SQLite 数据库文件
   - 虽然路径相同（`/app/data.sqlite`），但每个容器有自己的文件系统
   - 导致红包数据写入 `bot` 容器数据库，但 `web_admin` 读取不到

2. **环境变量覆盖**：
   - 系统环境变量 `DATABASE_URL` 设置为 PostgreSQL
   - Docker Compose 的环境变量优先级导致 `.env` 文件配置被覆盖

### 修复方案

#### 1. 添加共享数据卷

修改 `docker-compose.yml`，为所有服务添加共享数据卷：

```yaml
volumes:
  - ./data:/app/data  # 共享数据目录（包含 SQLite 数据库文件）
```

#### 2. 配置共享 SQLite 数据库

在 `docker-compose.yml` 中强制设置：

```yaml
environment:
  DATABASE_URL: sqlite:////app/data/data.sqlite  # 使用绝对路径（4个斜杠）
```

#### 3. 更新 .env 文件

```bash
DATABASE_URL=sqlite:////app/data/data.sqlite
```

### 验证结果

✅ **bot 和 web_admin 使用同一个数据库文件**：
- `bot DATABASE_URL: sqlite:////app/data/data.sqlite`
- `web_admin DATABASE_URL: sqlite:////app/data/data.sqlite`

✅ **数据库初始化成功**：
- `Database tables initialized successfully during startup`
- 所有表已创建

✅ **服务状态正常**：
- 所有容器运行正常（healthy）

### 修复后的行为

1. **数据同步**：
   - 所有服务（bot、web_admin、miniapp_api）使用同一个数据库文件
   - 红包数据写入后，Dashboard 立即能看到

2. **数据库位置**：
   - 数据库文件位于：`./data/data.sqlite`（宿主机）
   - 容器内路径：`/app/data/data.sqlite`
   - 支持数据持久化和备份

3. **启动行为**：
   - 首次启动时自动创建数据库和表结构
   - 后续启动自动初始化（幂等操作）

## 📝 后续测试

1. **测试红包发布**：
   - 在机器人中发布一个红包
   - 访问 `http://localhost:8000/admin/dashboard`
   - 检查 envelopes 数量是否增加

2. **测试前端刷新**：
   - 访问 `http://localhost:3001`
   - 检查统计数据是否正确显示
   - 等待 30 秒自动刷新，验证数据更新

3. **验证数据库同步**：
   ```bash
   # 检查两个容器是否看到相同的数据
   docker compose exec bot python -c "from models.db import get_session; from models.envelope import Envelope; from sqlalchemy import func; s = get_session().__enter__(); print('bot envelopes:', s.query(func.count(Envelope.id)).scalar()); s.__exit__(None, None, None)"
   docker compose exec web_admin python -c "from models.db import get_session; from models.envelope import Envelope; from sqlalchemy import func; s = get_session().__enter__(); print('web_admin envelopes:', s.query(func.count(Envelope.id)).scalar()); s.__exit__(None, None, None)"
   ```

## 🔧 其他修复

1. **Redis 端口冲突**：修改为 `127.0.0.1:6380:6379` 避免与宿主机冲突

2. **余额调整页面**：
   - 修复找不到用户时的错误提示
   - 修复表单字段水平对齐
   - 修复预览页面标题显示

3. **数据导出页面**：
   - 添加完整的异常处理和日志记录
   - 改进错误提示信息

## 📊 监控日志

已启动后台日志监控，使用以下命令查看：

```bash
# 查看所有服务日志
docker compose logs -f

# 只查看 bot 和 web_admin
docker compose logs -f bot web_admin

# 过滤错误日志
docker compose logs -f bot web_admin | Select-String -Pattern "ERROR|WARNING" -CaseSensitive:$false
```

## ✅ 修复完成

所有容器已重启，数据库配置已统一，现在可以测试红包发布和数据同步功能了。

