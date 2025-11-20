# 数据库同步问题排查报告

## 📋 问题概述

发布红包操作后，访问 `http://localhost:8000/admin/dashboard` 和 `http://localhost:3001` 时，系统未显示任何数据变动。

## 🔍 排查结果

### 1. 数据库配置检查

#### 1.1 数据库数量和名称

**PostgreSQL 数据库（配置但未使用）**：
- 数据库名称：`redpacket`
- 容器：`redpacket_db`
- 连接信息：`postgresql+psycopg2://redpacket:redpacket@db:5432/redpacket`
- 端口映射：`127.0.0.1:15432:5432`

**实际使用的数据库（问题根源）**：
- **bot 服务**：SQLite (`sqlite:///./data.sqlite`)
  - 数据库文件路径：`/app/data.sqlite`
  - 表数量：21 张
  - **envelopes 表记录数：1** ✅

- **web_admin 服务**：SQLite (`sqlite:///./data.sqlite`)
  - 数据库文件路径：`/app/data.sqlite`
  - 表数量：24 张
  - **envelopes 表记录数：0** ❌

#### 1.2 关键发现

**🔴 根本原因：数据库文件分离**

1. `bot` 和 `web_admin` 容器都使用 SQLite 数据库
2. 它们都使用相对路径 `./data.sqlite`，在各自容器内指向 `/app/data.sqlite`
3. **容器之间没有共享数据库文件的卷挂载**
4. 结果是：
   - `bot` 容器有自己的独立数据库文件（容器内：`/app/data.sqlite`）
   - `web_admin` 容器有自己的独立数据库文件（容器内：`/app/data.sqlite`）
   - 这两个文件是**完全不同的文件**，数据互不同步

### 2. 数据写入检查

#### 2.1 红包创建流程

**代码位置**：`routers/envelope.py:1368-1398`

```python
with get_session() as s:
    env = create_envelope(...)
    add_ledger_entry(...)
    s.commit()  # ✅ 正确提交事务
```

**数据写入位置**：
- 红包数据写入 `bot` 容器的数据库 ✅
- 但是 `web_admin` 容器读取的是自己的数据库 ❌

#### 2.2 数据查询检查

**Dashboard 查询**：`web_admin/controllers/dashboard.py:42-183`
- 查询 `web_admin` 容器的数据库
- 因为数据库文件不同，查询结果为空

**实际数据对比**：
- `bot` 容器：1 条 envelope 记录（ID: 1, 创建时间: 2025-11-15 23:35:15）
- `web_admin` 容器：0 条 envelope 记录

### 3. 缓存机制检查

#### 3.1 后端缓存

**位置**：`web_admin/controllers/dashboard.py:29-31`

```python
_CACHE: Dict[str, Any] = {"ts": 0, "data": None}
_CACHE_TTL = 30  # 秒
```

- 缓存时长：30 秒
- 问题：即使清除缓存，查询的还是不同的数据库

#### 3.2 前端刷新机制

**位置**：`frontend-next/src/app/page.tsx:38-43`

```typescript
refetchInterval: 30000, // 每30秒自动刷新
```

- 刷新间隔：30 秒
- 问题：即使刷新，后端返回的还是空数据

### 4. 环境变量检查

**docker-compose.yml 配置**：
```yaml
environment:
  DATABASE_URL: ${DATABASE_URL:-postgresql+psycopg2://redpacket:redpacket@db:5432/redpacket}
```

**实际使用的值**：
- `bot` 容器：`sqlite:///./data.sqlite` ❌（未使用 PostgreSQL）
- `web_admin` 容器：`sqlite:///./data.sqlite` ❌（未使用 PostgreSQL）

**原因**：`.env` 文件或环境变量覆盖了 docker-compose.yml 的默认值

## 🔧 解决方案

### 方案 1：使用共享卷挂载 SQLite 数据库文件（快速修复）

修改 `docker-compose.yml`，为 `bot` 和 `web_admin` 添加共享数据库卷：

```yaml
services:
  bot:
    volumes:
      - ./static:/app/static
      - ./exports:/app/exports
      - ./secrets:/app/secrets:ro
      - ./data:/app/data  # ✅ 新增：共享数据目录

  web_admin:
    volumes:
      - ./static:/app/static
      - ./exports:/app/exports
      - ./templates:/app/templates:ro
      - ./secrets:/app/secrets:ro
      - ./data:/app/data  # ✅ 新增：共享数据目录
```

同时修改 `.env` 或环境变量：
```bash
DATABASE_URL=sqlite:////app/data/data.sqlite
```

### 方案 2：统一使用 PostgreSQL（推荐生产环境）

修改 `.env` 文件：
```bash
DATABASE_URL=postgresql+psycopg2://redpacket:redpacket@db:5432/redpacket
```

然后重启所有服务：
```bash
docker compose down
docker compose up -d --build
```

### 方案 3：迁移现有数据（如果方案 1 或 2）

如果 `bot` 容器中有重要数据，需要先导出：

```bash
# 从 bot 容器导出数据
docker compose exec bot python -c "
from models.db import get_session
from models.envelope import Envelope
import json
s = get_session().__enter__()
envelopes = s.query(Envelope).all()
data = [{'id': e.id, 'chat_id': e.chat_id, 'sender_tg_id': e.sender_tg_id, 'status': e.status, 'created_at': str(e.created_at)} for e in envelopes]
print(json.dumps(data, indent=2))
s.__exit__(None, None, None)
"
```

## 📝 修复步骤（推荐方案 1）

1. **停止所有容器**：
```bash
docker compose down
```

2. **创建数据目录**：
```bash
mkdir -p data
```

3. **修改 docker-compose.yml**（添加共享卷）

4. **修改环境变量**（使用绝对路径）

5. **启动服务**：
```bash
docker compose up -d
```

6. **验证数据库同步**：
```bash
# 检查 bot 和 web_admin 是否使用同一个数据库文件
docker compose exec bot python -c "from models.db import DATABASE_URL; print(DATABASE_URL)"
docker compose exec web_admin python -c "from models.db import DATABASE_URL; print(DATABASE_URL)"

# 检查 envelopes 表记录数是否一致
docker compose exec bot python -c "from models.db import get_session; from models.envelope import Envelope; from sqlalchemy import func; s = get_session().__enter__(); print('bot:', s.query(func.count(Envelope.id)).scalar()); s.__exit__(None, None, None)"
docker compose exec web_admin python -c "from models.db import get_session; from models.envelope import Envelope; from sqlalchemy import func; s = get_session().__enter__(); print('web_admin:', s.query(func.count(Envelope.id)).scalar()); s.__exit__(None, None, None)"
```

## ✅ 验证检查清单

- [ ] 数据库文件路径一致
- [ ] bot 和 web_admin 使用同一个数据库文件
- [ ] envelopes 表记录数一致
- [ ] 发布红包后，dashboard 能立即看到数据
- [ ] 前端页面（localhost:3001）能正确显示数据
- [ ] 清除缓存后数据仍然正确

## 🎯 预期结果

修复后：
1. 所有服务使用同一个数据库文件
2. 发布红包后，数据立即写入共享数据库
3. Dashboard 能立即查询到最新数据
4. 前端页面每 30 秒刷新后能显示最新数据
5. 不再出现数据不一致问题

