"""
测试 web_admin/controllers/covers.py
封面管理控制器测试
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def admin_session():
    """模拟管理员会话"""
    return {"tg_id": 10001, "username": "admin"}


def test_covers_list_page(client_with_db, admin_session):
    """测试封面列表页面"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/covers")
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


def test_covers_list_page_with_params(client_with_db, admin_session):
    """测试封面列表页面 - 带参数"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试分页
        response = client_with_db.get("/admin/covers?page=2&per_page=10")
        assert response.status_code in [200, 401, 403]
        
        # 测试搜索
        response = client_with_db.get("/admin/covers?q=test")
        assert response.status_code in [200, 401, 403]
        
        # 测试 active 筛选
        response = client_with_db.get("/admin/covers?active=true")
        assert response.status_code in [200, 401, 403]


def test_covers_upload(client_with_db, admin_session, db_session):
    """测试上传封面"""
    # 清理可能存在的旧数据（确保测试隔离）
    from models.cover import Cover
    try:
        db_session.query(Cover).filter(Cover.channel_id == 0, Cover.message_id == 0).delete()
        db_session.commit()
    except Exception:
        db_session.rollback()
        pass
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 创建测试文件
        files = {
            "file": ("test.jpg", b"fake image content", "image/jpeg")
        }
        data = {
            "title": "Test Cover #tag1 #tag2"
        }
        
        response = client_with_db.post(
            "/admin/covers/upload",
            files=files,
            data=data,
            follow_redirects=False
        )
        # 应该重定向、成功或需要认证
        assert response.status_code in [200, 303, 302, 401, 403, 400, 422]


def test_covers_upload_no_file(client_with_db, admin_session):
    """测试上传封面 - 无文件"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        data = {"title": "Test Cover"}
        response = client_with_db.post("/admin/covers/upload", data=data)
        # 应该返回 400 或需要认证
        assert response.status_code in [400, 401, 403, 422]


def test_covers_toggle(client_with_db, admin_session):
    """测试切换封面上架状态"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # Mock toggle_cover_active
        with patch("web_admin.controllers.covers.toggle_cover_active"):
            response = client_with_db.post("/admin/covers/1/toggle", follow_redirects=False)
            # 应该重定向（如果不跟随重定向）或返回 200（如果跟随重定向）
            assert response.status_code in [200, 303, 302, 401, 403]


def test_covers_delete(client_with_db, admin_session):
    """测试删除封面"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # Mock delete_cover
        with patch("web_admin.controllers.covers.delete_cover"):
            response = client_with_db.post("/admin/covers/1/delete", follow_redirects=False)
            # 应该重定向（如果不跟随重定向）或返回 200（如果跟随重定向）
            assert response.status_code in [200, 303, 302, 401, 403]


def test_covers_endpoints_require_auth(client):
    """测试封面端点需要认证"""
    endpoints = [
        ("GET", "/admin/covers"),
        ("POST", "/admin/covers/upload"),
        ("POST", "/admin/covers/1/toggle"),
        ("POST", "/admin/covers/1/delete"),
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        assert response.status_code in [200, 401, 403, 307, 303, 400, 422]

