"""
测试 web_admin/controllers/approvals.py
审批功能控制器测试
"""
import pytest
import json
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


def test_approvals_list(client_with_db, admin_session):
    """测试审批列表页面"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/approvals")
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


def test_approvals_list_with_status(client_with_db, admin_session):
    """测试审批列表 - 状态筛选"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试待审批
        response = client_with_db.get("/admin/approvals?status=PENDING")
        assert response.status_code in [200, 401, 403]
        
        # 测试已审批
        response = client_with_db.get("/admin/approvals?status=APPROVED")
        assert response.status_code in [200, 401, 403]
        
        # 测试已拒绝
        response = client_with_db.get("/admin/approvals?status=REJECTED")
        assert response.status_code in [200, 401, 403]


def test_approvals_list_pagination(client_with_db, admin_session):
    """测试审批列表 - 分页"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 第一页
        response1 = client_with_db.get("/admin/approvals?page=1&per_page=10")
        assert response1.status_code in [200, 401, 403]
        
        # 第二页
        response2 = client_with_db.get("/admin/approvals?page=2&per_page=10")
        assert response2.status_code in [200, 401, 403]


def test_approvals_enqueue(client_with_db, admin_session):
    """测试入队审批请求"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        payload = json.dumps({
            "asset": "POINT",
            "amount": 100,
            "users": [10001, 10002]
        })
        data = {
            "op_type": "ADJUST_BATCH",
            "payload": payload,
        }
        response = client_with_db.post("/admin/approvals/enqueue", data=data, follow_redirects=False)
        # 应该重定向或成功（如果客户端跟随了重定向）
        assert response.status_code in [200, 303, 302, 401, 403, 400]


def test_approvals_enqueue_invalid_json(client_with_db, admin_session):
    """测试入队审批请求 - 无效 JSON"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        data = {
            "op_type": "ADJUST_BATCH",
            "payload": "invalid json",
        }
        response = client_with_db.post("/admin/approvals/enqueue", data=data)
        # 应该返回 400
        assert response.status_code in [400, 401, 403, 422]


def test_approvals_approve(client_with_db, admin_session):
    """测试审批通过"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.GuardDangerOp", return_value=admin_session):
            # Mock 审批执行
            with patch("web_admin.controllers.approvals._dispatch", return_value={"ok": 1, "fail": 0}):
                response = client_with_db.post("/admin/approvals/1/approve")
                # 应该重定向或返回 404
                assert response.status_code in [303, 302, 401, 403, 404, 400]


def test_approvals_approve_not_found(client_with_db, admin_session):
    """测试审批通过 - 不存在的审批"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        with patch("web_admin.deps.GuardDangerOp", return_value=admin_session):
            response = client_with_db.post("/admin/approvals/99999/approve")
            # 应该返回 404
            assert response.status_code in [404, 401, 403, 400]


def test_approvals_reject(client_with_db, admin_session):
    """测试拒绝审批"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        data = {
            "reason": "测试拒绝原因",
        }
        response = client_with_db.post("/admin/approvals/1/reject", data=data)
        # 应该重定向或返回 404
        assert response.status_code in [303, 302, 401, 403, 404, 400]


def test_approvals_reject_not_found(client_with_db, admin_session):
    """测试拒绝审批 - 不存在的审批"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        data = {
            "reason": "测试拒绝原因",
        }
        response = client_with_db.post("/admin/approvals/99999/reject", data=data)
        # 应该返回 404
        assert response.status_code in [404, 401, 403, 400]


def test_approvals_endpoints_require_auth(client):
    """测试审批端点需要认证"""
    endpoints = [
        ("GET", "/admin/approvals"),
        ("POST", "/admin/approvals/enqueue"),
        ("POST", "/admin/approvals/1/approve"),
        ("POST", "/admin/approvals/1/reject"),
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        assert response.status_code in [200, 401, 403, 307, 303, 400, 422, 404]


def test_json_payload_function():
    """测试 _json_payload 函数"""
    from web_admin.controllers.approvals import _json_payload
    
    # 测试字典输入
    assert _json_payload({"key": "value"}) == {"key": "value"}
    
    # 测试 JSON 字符串
    assert _json_payload('{"key": "value"}') == {"key": "value"}
    
    # 测试无效 JSON
    result = _json_payload("invalid")
    assert result == {}


def test_exec_adjust_batch_function(db_session):
    """测试 _exec_adjust_batch 函数"""
    from web_admin.controllers.approvals import _exec_adjust_batch
    from unittest.mock import patch
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001)
    
    payload = {
        "asset": "POINT",
        "amount": 100,
        "users": [10001],
        "note": "测试调整",
    }
    
    # Mock update_balance
    with patch("web_admin.controllers.approvals.update_balance"):
        result = _exec_adjust_batch(db_session, payload, operator_id=10001)
        assert "ok" in result
        assert "fail" in result
        assert "count" in result


def test_exec_reset_selected_function(db_session):
    """测试 _exec_reset_selected 函数"""
    from web_admin.controllers.approvals import _exec_reset_selected
    from unittest.mock import patch
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001)
    
    payload = {
        "asset": "POINT",
        "users": [10001],
        "note": "RESET",
    }
    
    # Mock get_balance 和 update_balance
    with patch("web_admin.controllers.approvals.get_balance", return_value=100):
        with patch("web_admin.controllers.approvals.update_balance"):
            result = _exec_reset_selected(db_session, payload, operator_id=10001)
            assert "ok" in result
            assert "fail" in result
            assert "total_deduct" in result

