# 数据库迁移与初始化指南

本文档说明数据库结构来源、迁移/初始化脚本，以及首次部署和后续升级的步骤。

---

## 目录

- [数据库结构来源](#数据库结构来源)
- [初始化机制](#初始化机制)
- [首次部署步骤](#首次部署步骤)
- [后续升级步骤](#后续升级步骤)
- [数据种子脚本](#数据种子脚本)

---

## 数据库结构来源

### 模型定义位置

所有数据模型定义在 `models/` 目录下：

| 文件 | 说明 | 表名 |
|------|------|------|
| `models/user.py` | 用户模型 | `users` |
| `models/envelope.py` | 红包模型 | `envelopes` |
| `models/ledger.py` | 账本模型（流水记录） | `ledger` |
| `models/recharge.py` | 充值订单模型 | `recharge_orders` |
| `models/invite.py` | 邀请模型 | `invites` |
| `models/public_group.py` | 公开群组模型 | `public_groups`、`public_group_activities` 等 |
| `models/cover.py` | 封面模型 | `covers`（如果存在） |

### 数据库初始化

数据库初始化通过 `models/db.py` 中的 `init_db()` 函数完成：

```python
from models.db import init_db

# 初始化数据库（创建所有表）
init_db()
```

**功能**:
1. 导入所有模型（确保 `Base.metadata` 包含所有表定义）
2. 调用 `Base.metadata.create_all(bind=engine)` 创建所有表
3. 执行轻量迁移（为历史库补齐缺失列）
4. 创建强幂等表（`gsheet_membership_logged`）

---

## 初始化机制

### 自动表创建

`init_db()` 使用 SQLAlchemy 的 `create_all()` 方法，根据模型定义自动创建表结构。

**特点**:
- 幂等性：已存在的表不会重复创建
- 自动创建索引、外键约束
- 兼容 SQLite、PostgreSQL、MySQL

### 轻量迁移机制

`init_db()` 包含轻量迁移逻辑，用于为历史数据库自动补齐新增列：

**支持的迁移**:
1. **envelopes 表**:
   - `is_finished` (BOOLEAN)
   - `mvp_dm_sent` (BOOLEAN)
   - `cover_channel_id` (BIGINT)
   - `cover_message_id` (BIGINT)
   - `cover_file_id` (TEXT)
   - `cover_meta` (TEXT/JSON)

2. **users 表**:
   - `usdt_balance` (DECIMAL/NUMERIC)
   - `ton_balance` (DECIMAL/NUMERIC)
   - `point_balance` (INTEGER)
   - `energy_balance` (INTEGER)
   - `last_target_chat_id` (BIGINT)
   - `last_target_chat_title` (VARCHAR)
   - `language` (VARCHAR)
   - `role` (VARCHAR)

3. **recharge_orders 表**:
   - `finished_at` (TIMESTAMP)
   - `tx_hash` (VARCHAR)
   - `note` (VARCHAR)
   - `pay_address` (VARCHAR)
   - `pay_currency` (VARCHAR)
   - `pay_amount` (VARCHAR)
   - `network` (VARCHAR)
   - `invoice_id` (VARCHAR)
   - `payment_id` (VARCHAR)
   - `payment_url` (VARCHAR)
   - `purchase_id` (VARCHAR)
   - `qr_b64` (TEXT)

4. **public_group_activity_ai_history 表**（如果启用公开群组）:
   - `applied_activity_id` (INTEGER)
   - `applied_at` (TIMESTAMP)

**迁移机制**:
- 使用 `_ensure_column()` 函数检查列是否存在
- 如果不存在，执行 `ALTER TABLE ... ADD COLUMN ...`
- 兼容 SQLite、PostgreSQL、MySQL 的语法差异
- 并发安全：重复执行不会报错

### 强幂等表

`init_db()` 会自动创建 `gsheet_membership_logged` 表（如果不存在）：

**表结构**:
```sql
CREATE TABLE gsheet_membership_logged (
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    PRIMARY KEY (chat_id, user_id)
)
```

**用途**: 记录已写入 Google Sheet 的群成员关系，确保跨进程/重启也能保证"每群每人仅一条"的唯一性。

---

## 首次部署步骤

### 1. 准备环境变量

确保 `.env` 文件中包含数据库连接配置：

```bash
# SQLite（开发环境）
DATABASE_URL=sqlite:///./data.sqlite

# PostgreSQL（生产环境）
DATABASE_URL=postgresql://user:password@host:5432/dbname

# MySQL（生产环境）
DATABASE_URL=mysql://user:password@host:3306/dbname
```

### 2. 创建数据库（PostgreSQL/MySQL）

**PostgreSQL**:
```bash
# 创建数据库
createdb hongbao_db

# 或使用 psql
psql -U postgres
CREATE DATABASE hongbao_db;
```

**MySQL**:
```bash
mysql -u root -p
CREATE DATABASE hongbao_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**SQLite**: 无需手动创建，`init_db()` 会自动创建文件。

### 3. 运行数据库初始化

```bash
# 方式 1: 使用 Python 脚本
python -c "from models.db import init_db; init_db()"

# 方式 2: 在代码中调用（服务启动时自动执行）
# web_admin/main.py 和 miniapp/main.py 在启动时会调用 init_db()
```

**预期输出**:
- 无错误信息
- 数据库文件/表已创建

### 4. 验证数据库结构

**SQLite**:
```bash
sqlite3 data.sqlite ".tables"
sqlite3 data.sqlite ".schema users"
```

**PostgreSQL**:
```bash
psql -U user -d hongbao_db -c "\dt"
psql -U user -d hongbao_db -c "\d users"
```

**MySQL**:
```bash
mysql -u user -p hongbao_db -e "SHOW TABLES;"
mysql -u user -p hongbao_db -e "DESCRIBE users;"
```

### 5. 初始化测试数据（可选）

```bash
# 创建测试用的公开群组和活动
python scripts/seed_public_groups.py --groups 3 --activities 3 --creator 900001
```

**预期输出**:
```
[seed] group id=1 name='測試交友 20250101 #01' status=active risk=0 flags=[]
[seed] activity id=1 name='MiniApp 星星加碼 #01'
Seed completed.
Groups created: 1, 2, 3
Activities created: 1, 2, 3
```

---

## 后续升级步骤

### 1. 备份数据库

**SQLite**:
```bash
cp data.sqlite data.sqlite.backup-$(date +%Y%m%d-%H%M%S)
```

**PostgreSQL**:
```bash
pg_dump -U user hongbao_db > backup-$(date +%Y%m%d-%H%M%S).sql
```

**MySQL**:
```bash
mysqldump -u user -p hongbao_db > backup-$(date +%Y%m%d-%H%M%S).sql
```

### 2. 运行迁移

升级时，`init_db()` 会自动执行轻量迁移（补齐缺失列）：

```bash
# 方式 1: 直接调用
python -c "from models.db import init_db; init_db()"

# 方式 2: 重启服务（服务启动时会自动调用 init_db()）
# 无需额外操作
```

**注意**: `init_db()` 是幂等的，可以安全地重复执行。

### 3. 验证迁移成功

#### 检查新增列是否存在

**SQLite**:
```bash
sqlite3 data.sqlite "PRAGMA table_info(users);" | grep usdt_balance
```

**PostgreSQL**:
```bash
psql -U user -d hongbao_db -c "\d users" | grep usdt_balance
```

**MySQL**:
```bash
mysql -u user -p hongbao_db -e "DESCRIBE users;" | grep usdt_balance
```

#### 检查表结构完整性

**检查关键表是否存在**:
```bash
# SQLite
sqlite3 data.sqlite ".tables" | grep -E "(users|envelopes|ledger|recharge_orders|public_groups)"

# PostgreSQL
psql -U user -d hongbao_db -c "\dt" | grep -E "(users|envelopes|ledger|recharge_orders|public_groups)"

# MySQL
mysql -u user -p hongbao_db -e "SHOW TABLES;" | grep -E "(users|envelopes|ledger|recharge_orders|public_groups)"
```

#### 检查数据完整性

```bash
# 检查用户表是否有数据
python -c "from models.db import get_session; from models.user import User; 
with get_session() as s: print(f'Users: {s.query(User).count()}')"

# 检查红包表是否有数据
python -c "from models.db import get_session; from models.envelope import Envelope; 
with get_session() as s: print(f'Envelopes: {s.query(Envelope).count()}')"
```

### 4. 回滚（如果迁移失败）

如果迁移出现问题，可以回滚到备份：

**SQLite**:
```bash
cp data.sqlite.backup-YYYYMMDD-HHMMSS data.sqlite
```

**PostgreSQL**:
```bash
psql -U user -d hongbao_db < backup-YYYYMMDD-HHMMSS.sql
```

**MySQL**:
```bash
mysql -u user -p hongbao_db < backup-YYYYMMDD-HHMMSS.sql
```

---

## 数据种子脚本

### `scripts/seed_public_groups.py` - 公开群组种子数据

**用途**: 创建测试用的公开群组和活动数据

**执行方式**:
```bash
python scripts/seed_public_groups.py --groups 3 --activities 3 --creator 900001
```

**参数**:
- `--groups`: 创建的群组数量（默认: 3）
- `--activities`: 创建的活动数量（默认: 3）
- `--creator`: 创建者的 Telegram ID（默认: 900000）
- `--prefix`: 群组名称前缀（默认: "測試交友 "）

**功能**:
1. 生成测试群组定义（名称、邀请链接、描述、标签等）
2. 生成测试活动定义（名称、奖励点数、时间范围等）
3. 使用服务层创建群组和活动（保持与生产逻辑一致）
4. 输出创建的群组 ID 和活动 ID

**注意事项**:
- 使用服务层创建，确保验证逻辑与生产一致
- 如果群组已存在（`invite_link` 唯一约束），会抛出 `IntegrityError`
- 建议在测试环境或空数据库中运行

---

## 迁移策略说明

### 当前策略：轻量迁移

**优点**:
- 简单易用，无需额外工具
- 自动检测并补齐缺失列
- 兼容多种数据库（SQLite、PostgreSQL、MySQL）

**缺点**:
- 不支持删除列、重命名列、修改列类型
- 不支持复杂迁移（如数据转换）
- 不适合大型生产环境

### 未来建议：Alembic 迁移

对于大型生产环境，建议使用 Alembic 进行数据库迁移：

**优势**:
- 版本化迁移脚本
- 支持复杂迁移（数据转换、索引创建等）
- 支持回滚
- 团队协作友好

**迁移步骤**:
1. 安装 Alembic: `pip install alembic`
2. 初始化: `alembic init alembic`
3. 生成迁移: `alembic revision --autogenerate -m "add usdt_balance"`
4. 执行迁移: `alembic upgrade head`
5. 回滚: `alembic downgrade -1`

**TODO**: 考虑在后续版本中引入 Alembic 迁移。

---

## 常见问题

### Q: 如何检查数据库连接是否正常？

```bash
python -c "from models.db import engine; engine.connect(); print('✅ DB OK')"
```

### Q: 如何清空所有表数据（开发测试用）？

```bash
# ⚠️ 仅限开发测试使用
python scripts/cleanup_db.py
```

### Q: 迁移后某些列仍然缺失？

1. 检查 `init_db()` 是否正常执行（查看日志）
2. 检查数据库方言是否正确识别（SQLite/PostgreSQL/MySQL）
3. 手动执行 `ALTER TABLE` 语句（参考 `models/db.py` 中的 `_ensure_column` 逻辑）

### Q: 如何查看当前数据库版本/迁移状态？

当前没有版本表，可以通过检查关键列是否存在来判断：

```bash
# 检查 users 表是否有新列
python -c "from models.db import _column_exists; print(_column_exists('users', 'usdt_balance'))"
```

**TODO**: 添加数据库版本表，记录迁移历史。

---

## TODO

- [ ] 添加数据库版本表，记录迁移历史
- [ ] 添加迁移验证脚本，检查所有必需列是否存在
- [ ] 考虑引入 Alembic 迁移（大型生产环境）
- [ ] 添加数据库备份/恢复脚本
- [ ] 添加数据库性能优化建议（索引、查询优化等）

---

*最后更新: 2025-01-XX*

