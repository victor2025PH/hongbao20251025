# tests/test_services.py
# -*- coding: utf-8 -*-
"""
业务服务层测试：
- 邀请进度（拼多多模式）
- 充值服务（mock）
"""

from __future__ import annotations

import os
import sqlite3
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import text

# 强制使用 mock provider，避免网络请求
os.environ.setdefault("RECHARGE_PROVIDER", "mock")

# SQLite 默认不支持 Decimal 绑定，手动注册
sqlite3.register_adapter(Decimal, lambda d: str(d))

from models.db import engine, get_session, init_db  # noqa: E402
from models.invite import get_progress as model_get_progress  # noqa: E402
from models.user import User, update_balance  # noqa: E402
from services import invite_service, recharge_service  # noqa: E402


@pytest.fixture(autouse=True)
def _setup_database(tmp_path, request):
    """为每个测试使用独立的临时数据库"""
    # 保存原始数据库 URL
    original_db_url = os.environ.get("DATABASE_URL")
    
    # 使用测试函数名和唯一ID创建独立的数据库文件
    test_function_name = request.node.name if hasattr(request.node, 'name') else "test"
    import hashlib
    import time
    # 使用测试节点ID确保唯一性
    unique_id = hashlib.md5(f"test_services_{test_function_name}_{id(request.node)}_{time.time()}".encode()).hexdigest()[:16]
    test_db_path = tmp_path / f"test_services_{unique_id}.sqlite"
    # 确保数据库文件不存在
    if test_db_path.exists():
        try:
            test_db_path.unlink(missing_ok=True)
        except (FileNotFoundError, PermissionError):
            pass
    
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path.absolute()}"
    
    # 清理模块缓存，确保使用新的数据库 URL
    import sys
    modules_to_clear = (
        "models.db",
        "models.user",
        "models.invite",
        "models.ledger",
        "models.recharge",
        "services.invite_service",
        "services.recharge_service",
    )
    for mod in modules_to_clear:
        sys.modules.pop(mod, None)
    
    # 重新导入以使用新的数据库 URL
    from models.db import engine, get_session, init_db  # noqa: E402
    from models.invite import get_progress as model_get_progress  # noqa: E402
    from models.user import User, update_balance  # noqa: E402
    from services import invite_service, recharge_service  # noqa: E402
    
    # 初始化数据库
    try:
        init_db()
    except Exception:
        # 如果初始化失败（可能表已存在），忽略
        pass
    
    # 清理测试数据（确保每个测试从干净的状态开始）
    tables = (
        "invite_relations",
        "invite_progress",
        "ledger",
        "users",
        "recharge_orders",
    )
    with engine.begin() as conn:
        for table in tables:
            try:
                # 先检查表是否存在
                result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                if result.fetchone():
                    conn.execute(text(f"DELETE FROM {table}"))
            except Exception:
                pass
    
    yield
    
    # 清理
    try:
        # 关闭所有连接
        engine.dispose()
        # 删除数据库文件
        if test_db_path.exists():
            try:
                test_db_path.unlink(missing_ok=True)
            except (FileNotFoundError, PermissionError):
                pass
    except Exception:
        pass
    finally:
        # 恢复原始数据库 URL
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]


def test_invite_progress_flow():
    inviter_id = 40001
    invitee_ids = [40002, 40003, 40004, 40005]

    # 建立邀请人账户（先删除可能存在的用户和邀请关系）
    with get_session() as session:
        # 先删除可能存在的邀请关系
        from models.invite import InviteRelation, InviteProgress
        session.query(InviteRelation).filter(
            (InviteRelation.inviter_tg_id == inviter_id) |
            (InviteRelation.invitee_tg_id.in_(invitee_ids + [inviter_id]))
        ).delete(synchronize_session=False)
        session.query(InviteProgress).filter_by(inviter_tg_id=inviter_id).delete()
        # 先删除可能存在的用户
        session.query(User).filter_by(tg_id=inviter_id).delete()
        session.commit()
        # 创建新用户
        inviter = User(tg_id=inviter_id, point_balance=0)
        session.add(inviter)
        session.commit()

    # 初始进度应为 0%
    msg, percent = invite_service.get_invite_progress_text(inviter_id, lang="zh")
    assert isinstance(percent, int)
    assert 0 <= percent <= 100
    assert msg

    # 连续邀请 4 人
    for uid in invitee_ids:
        added = invite_service.add_invite_and_rewards(inviter_id, uid, give_extra_points=False)
        assert added is True

    progress = model_get_progress(inviter_id)
    assert progress["invited_count"] == len(invitee_ids)
    assert progress["progress_percent"] >= len(invitee_ids)

    # 补充足够积分后尝试兑换进度
    with get_session() as session:
        inviter = session.query(User).filter_by(tg_id=inviter_id).one()
        update_balance(session, inviter, "POINT", 6000)  # 默认 1000 分/进度，充足即可
        session.commit()

    ok, _, after = invite_service.redeem_points_to_progress(inviter_id, lang="zh")
    assert ok is True
    assert after > progress["progress_percent"]


def test_recharge_service_mock():
    user_id = 50001
    amount = Decimal("20.50")

    order = recharge_service.new_order(user_id=user_id, token="USDT", amount=amount, provider="mock")
    assert order.id > 0
    assert Decimal(str(order.amount)) == amount
    assert order.payment_url  # mock provider 会给出支付链接

    assert recharge_service.mark_order_success(order.id, tx_hash="0xmocktx") is True

    stored = recharge_service.get_order(order.id)
    assert stored is not None
    assert stored.status.name == "SUCCESS"
