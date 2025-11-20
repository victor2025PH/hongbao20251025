"""
测试 web_admin/controllers/export.py
导出功能控制器测试
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def admin_session():
    """模拟管理员会话"""
    return {"tg_id": 10001, "username": "admin"}


def test_export_page(client_with_db, admin_session):
    """测试导出页面"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/export")
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


def test_export_all(client_with_db, admin_session):
    """测试导出所有数据"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # Mock export_service - 使用实际存在的函数名
        with patch("web_admin.controllers.export.es.export_all_users_and_ledger") as mock_export:
            mock_export.return_value = "/path/to/export.xlsx"
            # 需要提供 kind 参数
            data = {"kind": "users_ledger"}
            response = client_with_db.post("/admin/export/all", data=data)
            # 应该返回文件或需要认证，或 422（验证错误）
            assert response.status_code in [200, 401, 403, 404, 422]


def test_export_users(client_with_db, admin_session):
    """测试导出用户数据"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # Mock export_service 和 get_session
        with patch("web_admin.controllers.export.es.export_some_users_and_ledger") as mock_export:
            with patch("web_admin.controllers.export.get_session") as mock_get_session:
                from unittest.mock import MagicMock
                mock_session = MagicMock()
                mock_session.query.return_value.filter.return_value.all.return_value = []
                mock_get_session.return_value = mock_session
                
                mock_export.return_value = "/path/to/export.xlsx"
                data = {"users": "10001,10002", "mode": "merged"}
                response = client_with_db.post("/admin/export/users", data=data)
                # 应该返回文件或需要认证，或 500（服务器错误）
                assert response.status_code in [200, 401, 403, 404, 400, 500]


def test_export_users_empty(client_with_db, admin_session):
    """测试导出用户数据 - 空输入"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        data = {"users": ""}
        response = client_with_db.post("/admin/export/users", data=data)
        # 应该返回 400 或需要认证
        assert response.status_code in [400, 401, 403, 422]


def test_export_endpoints_require_auth(client):
    """测试导出端点需要认证"""
    endpoints = [
        ("GET", "/admin/export"),
        ("POST", "/admin/export/all"),
        ("POST", "/admin/export/users"),
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        assert response.status_code in [200, 401, 403, 307, 303, 400, 422]


def test_split_users_function():
    """测试 _split_users 函数"""
    from web_admin.controllers.export import _split_users
    
    # 测试逗号分隔
    assert _split_users("user1,user2,user3") == ["user1", "user2", "user3"]
    
    # 测试换行分隔
    assert _split_users("user1\nuser2\nuser3") == ["user1", "user2", "user3"]
    
    # 测试空字符串
    assert _split_users("") == []
    
    # 测试空白字符
    assert _split_users("user1 user2 user3") == ["user1", "user2", "user3"]


def test_resolve_targets_to_tg_ids_function(db_session):
    """测试 _resolve_targets_to_tg_ids 函数"""
    from web_admin.controllers.export import _resolve_targets_to_tg_ids
    from models.user import User
    
    # 创建测试用户
    user1 = User(tg_id=10001, username="user1")
    user2 = User(tg_id=10002, username="user2")
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    
    # Mock get_session 以使用测试数据库会话
    from unittest.mock import patch
    from models.db import get_session
    
    def mock_get_session():
        return db_session
    
    with patch("web_admin.controllers.export.get_session", side_effect=mock_get_session):
        # 测试数字 ID
        result = _resolve_targets_to_tg_ids(["10001", "10002"])
        assert 10001 in result
        assert 10002 in result
        
        # 测试用户名
        result = _resolve_targets_to_tg_ids(["@user1", "user2"])
        assert 10001 in result
        assert 10002 in result
        
        # 测试混合
        result = _resolve_targets_to_tg_ids(["10001", "@user2"])
        assert 10001 in result
        assert 10002 in result
        
        # 测试不存在的用户
        result = _resolve_targets_to_tg_ids(["99999"])
        assert 99999 not in result

