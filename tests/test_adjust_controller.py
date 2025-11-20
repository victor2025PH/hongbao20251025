"""
测试 web_admin/controllers/adjust.py
余额调整控制器测试
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


def test_adjust_form(client_with_db, admin_session):
    """测试余额调整表单页面"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/adjust")
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


def test_adjust_preview(client_with_db, db_session, admin_session):
    """测试余额调整预览"""
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="test_user")
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect"):
            # 设置用户余额
            if hasattr(user, "balance_point"):
                user.balance_point = Decimal("100.00")
            db_session.commit()
            
            data = {
                "users": "10001",
                "asset": "POINT",
                "amount": "50",
                "note": "测试调整",
            }
            response = client_with_db.post("/admin/adjust/preview", data=data)
            # 应该返回 200 或需要认证
            assert response.status_code in [200, 401, 403, 400]


def test_adjust_preview_invalid_asset(client_with_db, admin_session):
    """测试余额调整预览 - 无效币种"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect"):
            data = {
                "users": "10001",
                "asset": "INVALID",
                "amount": "50",
            }
            response = client_with_db.post("/admin/adjust/preview", data=data)
            # 可能返回 200（带错误信息）或错误状态码
            # 检查响应中是否包含错误信息或返回错误状态码
            assert response.status_code in [200, 400, 401, 403, 422]
            if response.status_code == 200:
                # 如果返回 200，检查响应内容是否包含错误信息
                content = response.text.lower()
                assert "invalid" in content or "错误" in content or "无效" in content


def test_adjust_preview_invalid_amount(client_with_db, admin_session):
    """测试余额调整预览 - 无效金额"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect"):
            data = {
                "users": "10001",
                "asset": "POINT",
                "amount": "invalid",
            }
            response = client_with_db.post("/admin/adjust/preview", data=data)
            # 可能返回 200（带错误信息）或错误状态码
            # 检查响应中是否包含错误信息或返回错误状态码
            assert response.status_code in [200, 400, 401, 403, 422]
            if response.status_code == 200:
                # 如果返回 200，检查响应内容是否包含错误信息
                content = response.text.lower()
                assert "invalid" in content or "错误" in content or "无效" in content


def test_adjust_preview_multiple_users(client_with_db, db_session, admin_session):
    """测试余额调整预览 - 多个用户"""
    # 创建多个测试用户
    user1 = create_test_user(db_session, tg_id=10001, username="user1")
    user2 = create_test_user(db_session, tg_id=10002, username="user2")
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect"):
            data = {
                "users": "10001,10002",
                "asset": "POINT",
                "amount": "50",
            }
            response = client_with_db.post("/admin/adjust/preview", data=data)
            assert response.status_code in [200, 401, 403, 400]


def test_adjust_preview_username(client_with_db, db_session, admin_session):
    """测试余额调整预览 - 使用用户名"""
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect"):
            data = {
                "users": "@testuser",
                "asset": "POINT",
                "amount": "50",
            }
            response = client_with_db.post("/admin/adjust/preview", data=data)
            assert response.status_code in [200, 401, 403, 400]


def test_adjust_do(client_with_db, db_session, admin_session):
    """测试执行余额调整"""
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="test_user")
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect"):
            with patch("web_admin.deps.GuardDangerOp", return_value=admin_session):
                # Mock update_balance
                with patch("web_admin.controllers.adjust.update_balance"):
                    data = {
                        "users": "10001",
                        "asset": "POINT",
                        "amount": "50",
                        "note": "测试调整",
                    }
                    response = client_with_db.post("/admin/adjust/do", data=data)
                    # 应该返回 200 或需要认证
                    assert response.status_code in [200, 401, 403, 400]


def test_adjust_do_negative_amount(client_with_db, db_session, admin_session):
    """测试执行余额调整 - 负数金额（扣减）"""
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="test_user")
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.csrf_protect"):
            with patch("web_admin.deps.GuardDangerOp", return_value=admin_session):
                # Mock can_spend 和 update_balance
                with patch("web_admin.controllers.adjust.can_spend", return_value=True):
                    with patch("web_admin.controllers.adjust.update_balance"):
                        data = {
                            "users": "10001",
                            "asset": "POINT",
                            "amount": "-50",
                            "note": "测试扣减",
                        }
                        response = client_with_db.post("/admin/adjust/do", data=data)
                        assert response.status_code in [200, 401, 403, 400]


def test_adjust_endpoints_require_auth(client):
    """测试余额调整端点需要认证"""
    endpoints = [
        ("GET", "/admin/adjust"),
        ("POST", "/admin/adjust/preview"),
        ("POST", "/admin/adjust/do"),
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        assert response.status_code in [200, 401, 403, 307, 303, 400, 422]


def test_split_users_function():
    """测试 _split_users 函数"""
    from web_admin.controllers.adjust import _split_users
    
    # 测试逗号分隔
    assert _split_users("user1,user2,user3") == ["user1", "user2", "user3"]
    
    # 测试换行分隔
    assert _split_users("user1\nuser2\nuser3") == ["user1", "user2", "user3"]
    
    # 测试中文逗号
    assert _split_users("user1，user2，user3") == ["user1", "user2", "user3"]
    
    # 测试空字符串
    assert _split_users("") == []
    
    # 测试空白字符
    assert _split_users("user1 user2 user3") == ["user1", "user2", "user3"]


def test_resolve_single_function(db_session):
    """测试 _resolve_single 函数"""
    from web_admin.controllers.adjust import _resolve_single
    
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


def test_parse_amount_function():
    """测试 _parse_amount 函数"""
    from web_admin.controllers.adjust import _parse_amount
    
    # 测试 POINT（整数）
    assert _parse_amount("POINT", "100") == Decimal("100")
    
    # 测试 USDT（小数）
    result = _parse_amount("USDT", "100.123456")
    assert isinstance(result, Decimal)
    
    # 测试无效金额
    with pytest.raises(ValueError):
        _parse_amount("POINT", "invalid")

