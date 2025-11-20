# 🧪 测试指南

> **更新时间**: 2025-11-18  
> **状态**: ✅ 测试基础设施已完善

---

## 📚 测试文件结构

```
tests/
├── conftest.py                    # 统一的测试 fixtures
├── test_*.py                      # 测试文件
└── README_TESTING.md              # 本文档
```

---

## 🔧 使用测试 Fixtures

### 基础 Fixtures

#### 1. 数据库 Fixtures

```python
def test_example(db_session):
    """使用数据库会话"""
    # db_session 是自动提供的 SQLAlchemy Session
    user = User(tg_id=12345, username="test")
    db_session.add(user)
    db_session.commit()
```

#### 2. FastAPI 客户端 Fixtures

```python
def test_api_endpoint(client):
    """使用测试客户端"""
    response = client.get("/admin/api/v1/stats")
    assert response.status_code == 200
```

#### 3. 认证 Fixtures

```python
def test_authenticated_endpoint(authenticated_client):
    """使用已认证的客户端"""
    response = authenticated_client.get("/admin/api/v1/stats")
    assert response.status_code == 200
```

#### 4. 完整设置 Fixtures

```python
def test_with_db_and_auth(client_with_db):
    """使用带数据库和认证的客户端"""
    response = client_with_db.get("/admin/api/v1/group-list")
    assert response.status_code == 200
```

### 测试数据 Fixtures

#### 1. 示例用户

```python
def test_with_user(sample_user):
    """使用示例用户"""
    assert sample_user.tg_id == 10001
    assert sample_user.username == "test_user"
```

#### 2. 示例群组

```python
def test_with_group(sample_group):
    """使用示例群组"""
    assert sample_group.name == "Test Group"
    assert sample_group.status == PublicGroupStatus.ACTIVE
```

#### 3. 示例红包

```python
def test_with_envelope(sample_envelope):
    """使用示例红包"""
    assert sample_envelope.amount == 100.0
    assert sample_envelope.count == 5
```

---

## 🛠️ 工具函数

### 创建测试数据

```python
from tests.conftest import create_test_user, create_test_group, create_test_envelope

def test_custom_data(db_session):
    """创建自定义测试数据"""
    # 创建用户
    user = create_test_user(db_session, tg_id=50001, username="custom_user")
    
    # 创建群组
    group, risk = create_test_group(
        db_session,
        creator_tg_id=50001,
        name="Custom Group",
        invite_link="https://t.me/+custom",
    )
    
    # 创建红包
    envelope = create_test_envelope(
        db_session,
        tg_id=60001,
        amount=200.0,
        count=10,
    )
```

---

## 📝 编写测试的最佳实践

### 1. 使用 Fixtures

✅ **推荐**:
```python
def test_example(db_session, authenticated_client):
    """使用 fixtures"""
    response = authenticated_client.get("/admin/api/v1/stats")
    assert response.status_code == 200
```

❌ **不推荐**:
```python
def test_example():
    """手动设置"""
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    init_db()
    # ... 大量设置代码
```

### 2. 测试隔离

每个测试应该：
- ✅ 使用独立的数据库（通过 `tmp_path` fixture）
- ✅ 不依赖其他测试的状态
- ✅ 清理测试数据（自动处理）

### 3. 测试命名

✅ **推荐**:
```python
def test_get_stats_trends_with_valid_days():
    """测试统计趋势 API - 有效天数参数"""
    pass

def test_get_stats_trends_with_invalid_days():
    """测试统计趋势 API - 无效天数参数"""
    pass
```

### 4. 测试文档

每个测试函数应该有清晰的 docstring：

```python
def test_example():
    """
    测试示例
    
    验证：
    - 功能正常
    - 错误处理
    - 边界条件
    """
    pass
```

---

## 🚀 运行测试

### 运行所有测试

```bash
pytest tests/
```

### 运行特定测试文件

```bash
pytest tests/test_stats_api_enhanced.py
```

### 运行特定测试函数

```bash
pytest tests/test_stats_api_enhanced.py::test_get_stats_trends_with_data
```

### 运行并生成覆盖率报告

```bash
pytest tests/ --cov=web_admin --cov=services --cov-report=html
```

### 运行并显示详细输出

```bash
pytest tests/ -v
```

---

## 📊 覆盖率目标

### 当前覆盖率
- **总体**: 21%
- **目标**: 30%+

### 模块覆盖率目标
- `web_admin/controllers/*`: 50%+
- `services/*`: 40%+
- `models/*`: 30%+

---

## 🔍 调试测试

### 查看测试输出

```bash
pytest tests/ -v -s
```

### 在失败时进入调试器

```bash
pytest tests/ --pdb
```

### 只运行失败的测试

```bash
pytest tests/ --lf
```

---

## 📚 相关文档

- `conftest.py` - 测试 fixtures 定义
- `pytest.ini` - Pytest 配置
- `测试覆盖率提升最终报告.md` - 覆盖率报告

---

*测试基础设施已完善，可以更高效地编写和维护测试！*

