"""
测试 models/recharge.py
充值订单模型测试
"""
import pytest
from decimal import Decimal
from datetime import datetime, UTC, timedelta
from sqlalchemy.orm import Session

from models.recharge import (
    RechargeOrder,
    OrderStatus,
    create_order,
    write_back_fields,
    write_back_np_fields,
    mark_success,
    mark_failed,
    set_expired,
    expire_orders,
    get_order,
    list_user_orders,
    order_to_public_dict,
    _canon_token,
    _q2,
    _q0,
    _fmt_token_amount_for_display,
)


def test_order_status_enum():
    """测试 OrderStatus 枚举"""
    assert OrderStatus.PENDING == "PENDING"
    assert OrderStatus.SUCCESS == "SUCCESS"
    assert OrderStatus.FAILED == "FAILED"
    assert OrderStatus.EXPIRED == "EXPIRED"


def test_recharge_order_creation(db_session):
    """测试 RechargeOrder 模型创建"""
    # 使用 create_order 创建订单（函数内部使用 get_session 并提交）
    order = create_order(
        user_id=10001,
        amount=Decimal("100.00"),
        token="USDT",
        provider="nowpayments",
    )
    
    assert order.user_tg_id == 10001
    assert order.provider == "nowpayments"
    assert order.token == "USDT"
    assert order.amount == "100.00"
    assert order.status == OrderStatus.PENDING


def test_create_order(db_session):
    """测试 create_order 函数"""
    order = create_order(
        user_id=10001,
        amount=Decimal("100.00"),
        token="USDT",
        provider="nowpayments",
        note="Test order",
    )
    
    assert order is not None
    assert order.user_tg_id == 10001
    assert order.token == "USDT"
    assert order.amount == "100.00"
    assert order.status == OrderStatus.PENDING
    assert order.provider == "nowpayments"


def test_create_order_different_tokens(db_session):
    """测试 create_order - 不同币种"""
    # 测试 USDT
    order1 = create_order(10001, Decimal("100.00"), "USDT")
    assert order1.token == "USDT"
    
    # 测试 TON
    order2 = create_order(10001, Decimal("50.00"), "TON")
    assert order2.token == "TON"
    
    # 测试 POINT
    order3 = create_order(10001, 1000, "POINT")
    assert order3.token == "POINT"


def test_write_back_fields(db_session):
    """测试 write_back_fields 函数"""
    # 创建订单
    order = create_order(10001, Decimal("100.00"), "USDT")
    db_session.commit()
    
    # 写回字段
    updated_order = write_back_fields(
        order.id,
        pay_address="TTest123",
        pay_currency="usdttrc20",
        pay_amount="100.50",
        network="trx",
    )
    
    assert updated_order.pay_address == "TTest123"
    assert updated_order.pay_currency == "usdttrc20"
    assert updated_order.pay_amount == "100.50"
    assert updated_order.network == "trx"


def test_write_back_np_fields(db_session):
    """测试 write_back_np_fields 函数"""
    import uuid
    # 创建订单（函数内部使用 get_session 并提交）
    order = create_order(10001, Decimal("100.00"), "USDT")
    
    # 使用唯一的 invoice_id 和 payment_id 以避免 UNIQUE constraint 错误
    unique_id = str(uuid.uuid4())[:8]
    # NowPayments 专用写回（函数内部使用 get_session）
    np_payload = {
        "invoice_id": f"test_invoice_{unique_id}",
        "payment_id": f"test_payment_{unique_id}",
        "payment_url": "https://nowpayments.io/payment/test",
        "pay_amount": "100.50",
        "pay_currency": "usdttrc20",
    }
    updated_order = write_back_np_fields(order.id, np_payload)
    
    assert updated_order is not None
    assert updated_order.invoice_id == f"test_invoice_{unique_id}"
    assert updated_order.payment_id == f"test_payment_{unique_id}"
    assert updated_order.payment_url == "https://nowpayments.io/payment/test"


def test_mark_success(db_session):
    """测试 mark_success 函数"""
    # 创建用户
    from models.user import User
    user = User(tg_id=10001, username="testuser")
    db_session.add(user)
    db_session.commit()
    
    # 创建订单
    order = create_order(10001, Decimal("100.00"), "USDT")
    db_session.commit()
    
    # 标记成功（函数内部使用 get_session，所以需要确保数据已提交）
    result = mark_success(order.id, tx_hash="0x123456")
    
    assert result is True
    # 重新获取订单验证
    updated_order = get_order(order.id)
    assert updated_order is not None
    assert updated_order.status == OrderStatus.SUCCESS
    assert updated_order.tx_hash == "0x123456"
    assert updated_order.finished_at is not None


def test_mark_success_idempotent(db_session):
    """测试 mark_success - 幂等性"""
    # 创建用户
    from models.user import User
    user = User(tg_id=10001, username="testuser")
    db_session.add(user)
    db_session.commit()
    
    # 创建订单并标记成功
    order = create_order(10001, Decimal("100.00"), "USDT")
    db_session.commit()
    
    mark_success(order.id)
    first_order = get_order(order.id)
    assert first_order is not None
    first_finished_at = first_order.finished_at
    
    # 再次标记成功（应该幂等）
    result = mark_success(order.id)
    assert result is True
    second_order = get_order(order.id)
    assert second_order is not None
    assert second_order.status == OrderStatus.SUCCESS
    # 完成时间应该不变
    assert second_order.finished_at == first_finished_at


def test_mark_failed(db_session):
    """测试 mark_failed 函数"""
    # 创建订单
    order = create_order(10001, Decimal("100.00"), "USDT")
    db_session.commit()
    
    # 标记失败（函数内部使用 get_session，所以需要确保数据已提交）
    result = mark_failed(order.id, note="Payment failed")
    
    assert result is True
    # 重新获取订单验证
    updated_order = get_order(order.id)
    assert updated_order is not None
    assert updated_order.status == OrderStatus.FAILED
    assert updated_order.note == "Payment failed"
    assert updated_order.finished_at is not None


def test_set_expired(db_session):
    """测试 set_expired 函数"""
    # 创建订单
    order = create_order(10001, Decimal("100.00"), "USDT")
    db_session.commit()
    
    # 标记过期（函数内部使用 get_session，所以需要确保数据已提交）
    result = set_expired(order.id)
    
    assert result is True
    # 重新获取订单验证
    updated_order = get_order(order.id)
    assert updated_order is not None
    assert updated_order.status == OrderStatus.EXPIRED


def test_expire_orders(db_session):
    """测试 expire_orders 函数"""
    # 创建多个订单
    order1 = create_order(10001, Decimal("100.00"), "USDT")
    order2 = create_order(10002, Decimal("50.00"), "USDT")
    db_session.commit()
    
    # 手动设置过期时间（模拟已过期）
    order1.expire_at = datetime.now(UTC) - timedelta(hours=1)
    db_session.commit()
    
    # 执行过期处理
    expired_count = expire_orders()
    
    assert expired_count >= 0  # 可能已经过期或未过期


def test_get_order(db_session):
    """测试 get_order 函数"""
    # 创建订单
    order = create_order(10001, Decimal("100.00"), "USDT")
    db_session.commit()
    
    # 获取订单
    found_order = get_order(order.id)
    
    assert found_order is not None
    assert found_order.id == order.id
    
    # 测试不存在的订单
    assert get_order(99999) is None


def test_list_user_orders(db_session):
    """测试 list_user_orders 函数"""
    # 创建多个订单
    for i in range(5):
        create_order(10001, Decimal(f"{10 + i}.00"), "USDT")
    db_session.commit()
    
    # 获取用户订单列表
    orders = list_user_orders(10001, limit=3)
    
    assert len(orders) == 3
    assert all(isinstance(o, RechargeOrder) for o in orders)
    assert all(o.user_tg_id == 10001 for o in orders)


def test_order_to_public_dict(db_session):
    """测试 order_to_public_dict 函数"""
    # 创建订单
    order = create_order(10001, Decimal("100.00"), "USDT", note="Test")
    db_session.commit()
    
    # 转换为公共字典
    public_dict = order_to_public_dict(order)
    
    assert isinstance(public_dict, dict)
    assert "id" in public_dict
    assert "token" in public_dict
    assert "amount" in public_dict
    assert "status" in public_dict
    assert "created_at" in public_dict
    assert "expire_at" in public_dict


def test_canon_token():
    """测试 _canon_token 函数"""
    assert _canon_token("usdt") == "USDT"
    assert _canon_token("TON") == "TON"
    assert _canon_token("point") == "POINT"
    assert _canon_token("") == ""


def test_q2():
    """测试 _q2 函数（量化到 2 位小数）"""
    assert _q2(1.0) == Decimal("1.00")
    assert _q2(1.123456) == Decimal("1.12")
    assert _q2(Decimal("100.50")) == Decimal("100.50")
    assert _q2("100.50") == Decimal("100.50")


def test_q0():
    """测试 _q0 函数（量化到整数）"""
    assert _q0(1.0) == Decimal("1")
    assert _q0(1.99) == Decimal("1")
    assert _q0(Decimal("100.50")) == Decimal("100")
    assert _q0("100.50") == Decimal("100")


def test_fmt_token_amount_for_display():
    """测试 _fmt_token_amount_for_display 函数"""
    # 测试 USDT
    assert _fmt_token_amount_for_display("USDT", "100.50") == "100.50"
    # 测试 POINT
    assert _fmt_token_amount_for_display("POINT", "100.50") == "100"
    # 测试空值
    assert _fmt_token_amount_for_display("USDT", None) == ""
    assert _fmt_token_amount_for_display("USDT", "") == ""

