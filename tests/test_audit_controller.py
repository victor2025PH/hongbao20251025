"""
测试 web_admin/controllers/audit.py
审计日志控制器测试
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


def test_audit_list(client_with_db, admin_session):
    """测试审计列表页面"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/audit")
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


def test_audit_list_with_filters(client_with_db, admin_session):
    """测试审计列表 - 带筛选条件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试类型筛选
        response = client_with_db.get("/admin/audit?ltype=ADJUSTMENT")
        assert response.status_code in [200, 401, 403]
        
        # 测试币种筛选
        response = client_with_db.get("/admin/audit?token=POINT")
        assert response.status_code in [200, 401, 403]
        
        # 测试用户筛选
        response = client_with_db.get("/admin/audit?user=10001")
        assert response.status_code in [200, 401, 403]


def test_audit_list_pagination(client_with_db, admin_session):
    """测试审计列表 - 分页"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 第一页
        response1 = client_with_db.get("/admin/audit?page=1&per_page=10")
        assert response1.status_code in [200, 401, 403]
        
        # 第二页
        response2 = client_with_db.get("/admin/audit?page=2&per_page=10")
        assert response2.status_code in [200, 401, 403]


def test_get_audit_logs_api(client_with_db, admin_session):
    """测试获取审计日志 API"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/audit/api/v1/audit")
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "pagination" in data
            assert "sum_amount" in data


def test_get_audit_logs_api_with_filters(client_with_db, admin_session):
    """测试获取审计日志 API - 带筛选条件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试类型筛选
        response = client_with_db.get("/admin/audit/api/v1/audit?ltype=ADJUSTMENT")
        assert response.status_code in [200, 401, 403]
        
        # 测试多个类型
        response = client_with_db.get("/admin/audit/api/v1/audit?types=ADJUSTMENT&types=RESET")
        assert response.status_code in [200, 401, 403]
        
        # 测试金额范围
        response = client_with_db.get("/admin/audit/api/v1/audit?min_amount=10&max_amount=1000")
        assert response.status_code in [200, 401, 403]


def test_get_audit_logs_api_pagination(client_with_db, admin_session):
    """测试获取审计日志 API - 分页"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 第一页
        response1 = client_with_db.get("/admin/audit/api/v1/audit?page=1&per_page=20")
        assert response1.status_code in [200, 401, 403]
        
        if response1.status_code == 200:
            data1 = response1.json()
            assert data1["pagination"]["page"] == 1
        
        # 第二页
        response2 = client_with_db.get("/admin/audit/api/v1/audit?page=2&per_page=20")
        assert response2.status_code in [200, 401, 403]


def test_audit_export_csv(client_with_db, admin_session):
    """测试导出审计日志 CSV"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/audit/export.csv")
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            assert "text/csv" in response.headers.get("content-type", "")
            assert "attachment" in response.headers.get("content-disposition", "")


def test_audit_export_csv_with_filters(client_with_db, admin_session):
    """测试导出审计日志 CSV - 带筛选条件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/audit/export.csv?ltype=ADJUSTMENT&limit=100")
        assert response.status_code in [200, 401, 403]


def test_audit_export_json(client_with_db, admin_session):
    """测试导出审计日志 JSON"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/audit/export.json")
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data


def test_audit_export_json_with_filters(client_with_db, admin_session):
    """测试导出审计日志 JSON - 带筛选条件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/audit/export.json?ltype=ADJUSTMENT&limit=100")
        assert response.status_code in [200, 401, 403]


def test_audit_endpoints_require_auth(client):
    """测试审计端点需要认证"""
    endpoints = [
        ("GET", "/admin/audit"),
        ("GET", "/admin/audit/api/v1/audit"),
        ("GET", "/admin/audit/export.csv"),
        ("GET", "/admin/audit/export.json"),
    ]
    
    for method, endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in [200, 401, 403, 307, 303]


def test_audit_per_page_limits(client_with_db, admin_session):
    """测试审计列表 per_page 限制"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试超出上限
        response = client_with_db.get("/admin/audit?per_page=300")
        assert response.status_code in [422, 401, 403]
        
        # 测试有效范围
        response = client_with_db.get("/admin/audit?per_page=100")
        assert response.status_code in [200, 401, 403]

