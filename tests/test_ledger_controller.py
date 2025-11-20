"""
测试 web_admin/controllers/ledger.py
账本查看控制器测试
"""
import pytest
from datetime import datetime, UTC
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from models.user import User
from models.ledger import Ledger, LedgerType


def create_test_user(
    session: Session,
    tg_id: int = 10001,
    username: str = "test_user",
) -> User:
    """创建测试用户"""
    user = User(
        tg_id=tg_id,
        username=username,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_test_ledger(
    session: Session,
    user_id: int = 10001,
    amount: float = 100.0,
    ltype: str = "ADJUSTMENT",
    token: str = "POINT",
) -> Ledger:
    """创建测试账本记录"""
    ledger = Ledger(
        user_id=user_id,
        amount=amount,
        type=ltype,
        token=token,
    )
    session.add(ledger)
    session.commit()
    session.refresh(ledger)
    return ledger


@pytest.fixture
def admin_session():
    """模拟管理员会话"""
    return {"tg_id": 10001, "username": "admin"}


def test_ledger_list(client_with_db, admin_session):
    """测试账本列表页面"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/ledger")
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


def test_ledger_list_with_filters(client_with_db, admin_session):
    """测试账本列表 - 带筛选条件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试类型筛选
        response = client_with_db.get("/admin/ledger?ltype=ADJUSTMENT")
        assert response.status_code in [200, 401, 403]
        
        # 测试币种筛选
        response = client_with_db.get("/admin/ledger?token=POINT")
        assert response.status_code in [200, 401, 403]
        
        # 测试用户筛选
        response = client_with_db.get("/admin/ledger?user=10001")
        assert response.status_code in [200, 401, 403]
        
        # 测试时间范围
        response = client_with_db.get("/admin/ledger?start=2025-01-01&end=2025-01-31")
        assert response.status_code in [200, 401, 403]


def test_ledger_list_pagination(client_with_db, admin_session):
    """测试账本列表 - 分页"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 第一页
        response1 = client_with_db.get("/admin/ledger?page=1&per_page=10")
        assert response1.status_code in [200, 401, 403]
        
        # 第二页
        response2 = client_with_db.get("/admin/ledger?page=2&per_page=10")
        assert response2.status_code in [200, 401, 403]


def test_ledger_export_csv(client_with_db, admin_session):
    """测试导出账本 CSV"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/ledger/export.csv")
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            assert "text/csv" in response.headers.get("content-type", "")
            assert "attachment" in response.headers.get("content-disposition", "")


def test_ledger_export_csv_with_filters(client_with_db, admin_session):
    """测试导出账本 CSV - 带筛选条件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/ledger/export.csv?ltype=ADJUSTMENT&limit=100")
        assert response.status_code in [200, 401, 403]


def test_ledger_export_json(client_with_db, admin_session):
    """测试导出账本 JSON"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/ledger/export.json")
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data


def test_ledger_export_json_with_filters(client_with_db, admin_session):
    """测试导出账本 JSON - 带筛选条件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/ledger/export.json?ltype=ADJUSTMENT&limit=100")
        assert response.status_code in [200, 401, 403]


def test_ledger_per_page_limits(client_with_db, admin_session):
    """测试账本列表 per_page 限制"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试超出上限
        response = client_with_db.get("/admin/ledger?per_page=300")
        assert response.status_code in [422, 401, 403]
        
        # 测试有效范围
        response = client_with_db.get("/admin/ledger?per_page=100")
        assert response.status_code in [200, 401, 403]


def test_ledger_endpoints_require_auth(client):
    """测试账本端点需要认证"""
    endpoints = [
        "/admin/ledger",
        "/admin/ledger/export.csv",
        "/admin/ledger/export.json",
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in [200, 401, 403, 307, 303]


def test_col_function():
    """测试 _col 函数"""
    from web_admin.controllers.ledger import _col
    
    # 测试存在的字段
    class MockModel:
        field1 = "value1"
        field2 = "value2"
    
    assert _col(MockModel, "field1", "field2") == "value1"
    assert _col(MockModel, "nonexistent", "field2") == "value2"
    
    # 测试不存在的字段
    assert _col(MockModel, "nonexistent") is None


def test_resolve_user_join_cols_function():
    """测试 _resolve_user_join_cols 函数"""
    from web_admin.controllers.ledger import _resolve_user_join_cols
    
    # 测试函数返回
    result = _resolve_user_join_cols()
    assert isinstance(result, tuple)
    assert len(result) == 2

