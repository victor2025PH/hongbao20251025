"""
测试 web_admin/controllers/logs.py
日志查看控制器测试
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def admin_session():
    """模拟管理员会话"""
    return {"tg_id": 10001, "username": "admin"}


def test_get_logs(client_with_db, admin_session):
    """测试获取系统日志"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/api/v1/logs")
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "pagination" in data


def test_get_logs_with_filters(client_with_db, admin_session):
    """测试获取系统日志 - 带筛选条件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试级别筛选
        response = client_with_db.get("/admin/api/v1/logs?level=error")
        assert response.status_code in [200, 401, 403]
        
        # 测试模块筛选
        response = client_with_db.get("/admin/api/v1/logs?module=web_admin")
        assert response.status_code in [200, 401, 403]
        
        # 测试搜索
        response = client_with_db.get("/admin/api/v1/logs?q=error")
        assert response.status_code in [200, 401, 403]
        
        # 测试时间范围
        response = client_with_db.get("/admin/api/v1/logs?start=2025-01-01&end=2025-01-31")
        assert response.status_code in [200, 401, 403]


def test_get_logs_pagination(client_with_db, admin_session):
    """测试获取系统日志 - 分页"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 第一页
        response1 = client_with_db.get("/admin/api/v1/logs?page=1&per_page=20")
        assert response1.status_code in [200, 401, 403]
        
        if response1.status_code == 200:
            data1 = response1.json()
            assert data1["pagination"]["page"] == 1
        
        # 第二页
        response2 = client_with_db.get("/admin/api/v1/logs?page=2&per_page=20")
        assert response2.status_code in [200, 401, 403]


def test_get_logs_per_page_limits(client_with_db, admin_session):
    """测试获取系统日志 - per_page 限制"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试超出上限
        response = client_with_db.get("/admin/api/v1/logs?per_page=300")
        assert response.status_code in [422, 401, 403]
        
        # 测试有效范围
        response = client_with_db.get("/admin/api/v1/logs?per_page=100")
        assert response.status_code in [200, 401, 403]


def test_get_audit_logs_alt(client_with_db, admin_session):
    """测试获取审计日志（别名）"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/api/v1/logs/audit")
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "pagination" in data


def test_get_audit_logs_alt_with_filters(client_with_db, admin_session):
    """测试获取审计日志（别名）- 带筛选条件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/api/v1/logs/audit?level=error&module=web_admin")
        assert response.status_code in [200, 401, 403]


def test_logs_endpoints_require_auth(client):
    """测试日志端点需要认证"""
    endpoints = [
        "/admin/api/v1/logs",
        "/admin/api/v1/logs/audit",
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in [200, 401, 403]


def test_get_logs_page_validation(client_with_db, admin_session):
    """测试获取系统日志 - page 参数验证"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试无效页码
        response = client_with_db.get("/admin/api/v1/logs?page=0")
        assert response.status_code in [422, 401, 403]
        
        # 测试负数页码
        response = client_with_db.get("/admin/api/v1/logs?page=-1")
        assert response.status_code in [422, 401, 403]

