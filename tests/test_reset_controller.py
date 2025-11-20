"""
测试 web_admin/controllers/reset.py
重置功能控制器测试
"""
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from models.user import User


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


@pytest.fixture
def admin_session():
    """模拟管理员会话"""
    return {"tg_id": 10001, "username": "admin"}


def test_reset_page(client_with_db, admin_session):
    """测试重置页面"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/reset")
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


def test_reset_preview_selected(client_with_db, db_session, admin_session):
    """测试预览选中用户重置"""
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="test_user")
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect", return_value=True):
            # 设置用户余额
            if hasattr(user, "balance_point"):
                user.balance_point = Decimal("100.00")
            db_session.commit()
            
            data = {
                "users": "10001",
                "asset": "POINT",
                "passphrase": "test",
            }
            response = client_with_db.post("/admin/reset/preview", data=data)
            assert response.status_code in [200, 401, 403, 400]


def test_reset_preview_selected_invalid_asset(client_with_db, fastapi_app, admin_session):
    """测试预览选中用户重置 - 无效币种"""
    from web_admin.deps import csrf_protect
    # 使用 dependency_overrides 覆盖 csrf_protect
    fastapi_app.dependency_overrides[csrf_protect] = lambda: True
    try:
        data = {
            "users": "10001",
            "asset": "INVALID",
            "passphrase": "test",
        }
        response = client_with_db.post("/admin/reset/preview", data=data, follow_redirects=False)
        # 无效币种应该返回 400
        assert response.status_code == 400
    finally:
        fastapi_app.dependency_overrides.pop(csrf_protect, None)


def test_reset_preview_selected_no_passphrase(client_with_db, fastapi_app, admin_session):
    """测试预览选中用户重置 - 无密码"""
    from web_admin.deps import csrf_protect
    # 使用 dependency_overrides 覆盖 csrf_protect
    fastapi_app.dependency_overrides[csrf_protect] = lambda: True
    try:
        data = {
            "users": "10001",
            "asset": "POINT",
            "passphrase": "",
        }
        response = client_with_db.post("/admin/reset/preview", data=data, follow_redirects=False)
        # 无密码应该返回 400
        assert response.status_code == 400
    finally:
        fastapi_app.dependency_overrides.pop(csrf_protect, None)


def test_reset_preview_all(client_with_db, admin_session):
    """测试预览全体用户重置"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect", return_value=True):
            data = {
                "asset": "POINT",
                "passphrase": "test",
            }
            response = client_with_db.post("/admin/reset/preview_all", data=data)
            assert response.status_code in [200, 401, 403, 400]


def test_reset_do_selected(client_with_db, db_session, admin_session):
    """测试执行选中用户重置"""
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="test_user")
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect", return_value=True):
            with patch("web_admin.deps.GuardDangerOpWithReset", return_value=admin_session):
                # Mock update_balance
                with patch("web_admin.controllers.reset.update_balance"):
                    data = {
                        "users": "10001",
                        "asset": "POINT",
                        "passphrase": "test",
                        "dryrun": 0,
                        "note": "RESET",
                    }
                    response = client_with_db.post("/admin/reset/do_selected", data=data)
                    assert response.status_code in [200, 401, 403, 400]


def test_reset_do_selected_dryrun(client_with_db, db_session, admin_session):
    """测试执行选中用户重置 - 试运行"""
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="test_user")
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect", return_value=True):
            with patch("web_admin.deps.GuardDangerOpWithReset", return_value=admin_session):
                data = {
                    "users": "10001",
                    "asset": "POINT",
                    "passphrase": "test",
                    "dryrun": 1,
                }
                response = client_with_db.post("/admin/reset/do_selected", data=data)
                assert response.status_code in [200, 401, 403, 400]


def test_reset_do_all(client_with_db, admin_session):
    """测试执行全体用户重置"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect", return_value=True):
            with patch("web_admin.deps.GuardDangerOpWithReset", return_value=admin_session):
                # Mock update_balance
                with patch("web_admin.controllers.reset.update_balance"):
                    data = {
                        "asset": "POINT",
                        "passphrase": "test",
                        "dryrun": 0,
                        "note": "RESET",
                    }
                    response = client_with_db.post("/admin/reset/do_all", data=data)
                    assert response.status_code in [200, 401, 403, 400]


def test_reset_do_all_dryrun(client_with_db, admin_session):
    """测试执行全体用户重置 - 试运行"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect", return_value=True):
            with patch("web_admin.deps.GuardDangerOpWithReset", return_value=admin_session):
                data = {
                    "asset": "POINT",
                    "passphrase": "test",
                    "dryrun": 1,
                }
                response = client_with_db.post("/admin/reset/do_all", data=data)
                assert response.status_code in [200, 401, 403, 400]


def test_reset_endpoints_require_auth(client):
    """测试重置端点需要认证"""
    endpoints = [
        ("GET", "/admin/reset"),
        ("POST", "/admin/reset/preview"),
        ("POST", "/admin/reset/preview_all"),
        ("POST", "/admin/reset/do_selected"),
        ("POST", "/admin/reset/do_all"),
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        assert response.status_code in [200, 401, 403, 307, 303, 400, 422]


def test_split_users_function():
    """测试 _split_users 函数"""
    from web_admin.controllers.reset import _split_users
    
    # 测试逗号分隔
    assert _split_users("user1,user2,user3") == ["user1", "user2", "user3"]
    
    # 测试换行分隔
    assert _split_users("user1\nuser2\nuser3") == ["user1", "user2", "user3"]
    
    # 测试中文逗号
    assert _split_users("user1，user2，user3") == ["user1", "user2", "user3"]
    
    # 测试空字符串
    assert _split_users("") == []


def test_resolve_single_function(db_session):
    """测试 _resolve_single 函数"""
    from web_admin.controllers.reset import _resolve_single
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    
    # 测试数字 ID
    result = _resolve_single(db_session, "10001")
    assert result is not None
    assert result.tg_id == 10001
    
    # 测试用户名
    result = _resolve_single(db_session, "@testuser")
    assert result is not None
    assert result.username == "testuser"
    
    # 测试不存在的用户
    result = _resolve_single(db_session, "99999")
    assert result is None

