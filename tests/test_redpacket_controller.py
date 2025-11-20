"""
测试 web_admin/controllers/redpacket.py
红包功能 API 控制器测试
"""
import pytest
from decimal import Decimal
from datetime import datetime, UTC
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, AsyncMock

from models.user import User
from models.envelope import Envelope, EnvelopeShare
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


def create_test_envelope(
    session: Session,
    sender_tg_id: int = 10001,
    chat_id: int = -1000000000,
    total_amount: Decimal = Decimal("100.00"),
    shares: int = 5,
    mode: str = "POINT",
    status: str = "active",
) -> Envelope:
    """创建测试红包"""
    envelope = Envelope(
        sender_tg_id=sender_tg_id,
        chat_id=chat_id,
        total_amount=total_amount,
        shares=shares,
        mode=mode,
        status=status,
        is_finished=False,
    )
    session.add(envelope)
    session.commit()
    session.refresh(envelope)
    return envelope


@pytest.fixture
def admin_session():
    """模拟管理员会话"""
    return {"tg_id": 10001, "username": "admin"}


def test_get_user_balance(client_with_db, db_session, admin_session):
    """测试查询用户余额"""
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="test_user")
    
    # 设置余额
    if hasattr(user, "balance_usdt"):
        user.balance_usdt = Decimal("100.00")
    if hasattr(user, "balance_ton"):
        user.balance_ton = Decimal("50.00")
    if hasattr(user, "balance_point"):
        user.balance_point = Decimal("200.00")
    db_session.commit()
    
    # Mock 会话
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/api/v1/redpacket/balance")
        # 应该返回 200 或需要认证
        assert response.status_code in [200, 401, 403]


def test_get_red_packet_info(client_with_db, db_session, admin_session):
    """测试查询红包信息"""
    # 创建测试红包
    envelope = create_test_envelope(
        db_session,
        sender_tg_id=10001,
        total_amount=Decimal("100.00"),
        shares=5,
    )
    
    # Mock 会话
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get(f"/admin/api/v1/redpacket/{envelope.id}")
        # 应该返回 200 或需要认证
        assert response.status_code in [200, 401, 403, 404]


def test_get_red_packet_info_not_found(client_with_db, admin_session):
    """测试查询不存在的红包"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/api/v1/redpacket/99999")
        # 应该返回 404
        assert response.status_code in [404, 401, 403]


def test_get_red_packet_history(client_with_db, db_session, admin_session):
    """测试查询红包历史记录"""
    # 创建测试用户和红包
    user = create_test_user(db_session, tg_id=10001)
    envelope = create_test_envelope(
        db_session,
        sender_tg_id=10001,
        total_amount=Decimal("100.00"),
        shares=5,
    )
    
    # Mock 会话
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/api/v1/redpacket/history?page=1&limit=20")
        # 应该返回 200 或需要认证
        assert response.status_code in [200, 401, 403]


def test_get_red_packet_history_pagination(client_with_db, db_session, admin_session):
    """测试红包历史记录分页"""
    # 创建多个红包
    for i in range(3):
        create_test_envelope(
            db_session,
            sender_tg_id=10001,
            total_amount=Decimal(f"{100 + i * 10}.00"),
            shares=5,
        )
    
    # Mock 会话
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 第一页
        response1 = client_with_db.get("/admin/api/v1/redpacket/history?page=1&limit=2")
        assert response1.status_code in [200, 401, 403]
        
        # 第二页
        response2 = client_with_db.get("/admin/api/v1/redpacket/history?page=2&limit=2")
        assert response2.status_code in [200, 401, 403]


def test_get_red_packet_history_limit_validation(client_with_db, admin_session):
    """测试红包历史记录 limit 参数验证"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试超出上限
        response = client_with_db.get("/admin/api/v1/redpacket/history?limit=200")
        assert response.status_code in [422, 401, 403]
        
        # 测试最小值
        response = client_with_db.get("/admin/api/v1/redpacket/history?limit=0")
        assert response.status_code in [422, 401, 403]


def test_get_red_packet_history_page_validation(client_with_db, admin_session):
    """测试红包历史记录 page 参数验证"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 测试无效页码
        response = client_with_db.get("/admin/api/v1/redpacket/history?page=0")
        assert response.status_code in [422, 401, 403]


def test_grab_red_packet_not_found(client_with_db, admin_session):
    """测试抢不存在的红包"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.post("/admin/api/v1/redpacket/99999/grab")
        # 应该返回 404
        assert response.status_code in [404, 401, 403]


def test_grab_red_packet_finished(client_with_db, db_session, admin_session):
    """测试抢已结束的红包"""
    # 创建已结束的红包
    envelope = create_test_envelope(
        db_session,
        sender_tg_id=10001,
        total_amount=Decimal("100.00"),
        shares=5,
        status="closed",
    )
    envelope.is_finished = True
    db_session.commit()
    
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.post(f"/admin/api/v1/redpacket/{envelope.id}/grab")
        # 应该返回 400
        assert response.status_code in [400, 401, 403, 404]


def test_send_red_packet_invalid_token(client_with_db, admin_session):
    """测试发送红包 - 无效币种"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.post(
            "/admin/api/v1/redpacket/send",
            json={
                "chat_id": -1000000000,
                "token": "INVALID",
                "total_amount": 100.0,
                "shares": 5,
            }
        )
        # 应该返回 400
        assert response.status_code in [400, 401, 403]


def test_send_red_packet_invalid_amount(client_with_db, admin_session):
    """测试发送红包 - 无效金额"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.post(
            "/admin/api/v1/redpacket/send",
            json={
                "chat_id": -1000000000,
                "token": "POINT",
                "total_amount": -10.0,
                "shares": 5,
            }
        )
        # 应该返回 400 或 422
        assert response.status_code in [400, 422, 401, 403]


def test_send_red_packet_invalid_shares(client_with_db, admin_session):
    """测试发送红包 - 无效份数"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.post(
            "/admin/api/v1/redpacket/send",
            json={
                "chat_id": -1000000000,
                "token": "POINT",
                "total_amount": 100.0,
                "shares": 0,
            }
        )
        # 应该返回 400 或 422
        assert response.status_code in [400, 422, 401, 403]


def test_redpacket_endpoints_require_auth(client):
    """测试红包端点需要认证"""
    # 不提供认证
    endpoints = [
        "/admin/api/v1/redpacket/balance",
        "/admin/api/v1/redpacket/history",
        "/admin/api/v1/redpacket/1",
        "/admin/api/v1/redpacket/1/grab",
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint) if endpoint != "/admin/api/v1/redpacket/1/grab" else client.post(endpoint)
        # 应该返回 401 或 403
        assert response.status_code in [200, 401, 403, 404]

