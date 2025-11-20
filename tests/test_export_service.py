"""
测试 services/export_service.py
导出服务层测试
"""
import pytest
from datetime import datetime, UTC
from decimal import Decimal
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

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
        user_tg_id=user_id,  # 使用 user_tg_id 而不是 user_id（user_id 是只读的 hybrid_property）
        amount=amount,
        type=ltype,
        token=token,
    )
    session.add(ledger)
    session.commit()
    session.refresh(ledger)
    return ledger


def test_ensure_export_dir():
    """测试 _ensure_export_dir 函数"""
    from services.export_service import _ensure_export_dir
    import os
    
    # 测试创建导出目录
    result = _ensure_export_dir()
    assert isinstance(result, str)
    assert os.path.isdir(result)


def test_dtfmt():
    """测试 _dtfmt 函数"""
    from services.export_service import _dtfmt
    
    # 测试有效日期
    dt = datetime(2025, 1, 1, 12, 30, 45)
    result = _dtfmt(dt)
    assert result == "2025-01-01 12:30:45"
    
    # 测试 None
    assert _dtfmt(None) == ""
    
    # 测试空值
    assert _dtfmt(None) == ""


def test_enum_to_str():
    """测试 _enum_to_str 函数"""
    from services.export_service import _enum_to_str
    from enum import Enum
    
    # 测试枚举
    class TestEnum(Enum):
        VALUE1 = "value1"
        VALUE2 = "value2"
    
    assert _enum_to_str(TestEnum.VALUE1) == "VALUE1"
    
    # 测试字符串
    assert _enum_to_str("test") == "test"
    
    # 测试整数
    assert _enum_to_str(123) == "123"
    
    # 测试 None
    assert _enum_to_str(None) == ""


def test_as_float():
    """测试 _as_float 函数"""
    from services.export_service import _as_float
    
    # 测试 Decimal
    assert _as_float(Decimal("100.50")) == 100.5
    
    # 测试浮点数
    assert _as_float(100.5) == 100.5
    
    # 测试整数
    assert _as_float(100) == 100.0
    
    # 测试字符串
    assert _as_float("100.5") == 100.5
    
    # 测试无效值
    assert _as_float("invalid") == 0.0


def test_normalize_username():
    """测试 _normalize_username 函数"""
    from services.export_service import _normalize_username
    
    # 测试带 @ 的用户名
    assert _normalize_username("@testuser") == "testuser"
    
    # 测试不带 @ 的用户名
    assert _normalize_username("testuser") == "testuser"
    
    # 测试 None
    assert _normalize_username(None) == ""
    
    # 测试空字符串
    assert _normalize_username("") == ""


def test_display_full_name():
    """测试 _display_full_name 函数"""
    from services.export_service import _display_full_name
    
    # 测试完整名称
    result = _display_full_name(
        username="testuser",
        full_name="Test User",
        first_name="Test",
        last_name="User",
    )
    assert isinstance(result, str)
    assert len(result) > 0
    
    # 测试只有用户名
    result = _display_full_name(username="testuser")
    assert result == "testuser"
    
    # 测试空值
    result = _display_full_name()
    assert result == ""


def test_as_int_list():
    """测试 _as_int_list 函数"""
    from services.export_service import _as_int_list
    
    # 测试列表
    assert _as_int_list([1, 2, 3]) == [1, 2, 3]
    
    # 测试字符串列表
    assert _as_int_list(["1", "2", "3"]) == [1, 2, 3]
    
    # 测试逗号分隔字符串
    assert _as_int_list("1,2,3") == [1, 2, 3]
    
    # 测试单个整数
    assert _as_int_list(123) == [123]
    
    # 测试空值
    assert _as_int_list(None) == []
    assert _as_int_list("") == []


def test_pick_user_by_query(db_session):
    """测试 _pick_user_by_query 函数"""
    from services.export_service import _pick_user_by_query
    from contextlib import contextmanager
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    db_session.commit()
    
    # Mock get_session 以使用测试数据库会话
    @contextmanager
    def mock_get_session():
        yield db_session
    
    with patch("services.export_service.get_session", side_effect=mock_get_session):
        # 测试通过 tg_id 查询
        result = _pick_user_by_query(10001)
        assert result is not None
        assert result.tg_id == 10001
        
        # 测试通过用户名查询
        result = _pick_user_by_query("testuser")
        assert result is not None
        assert result.username == "testuser"
        
        # 测试不存在的用户
        result = _pick_user_by_query(99999)
        assert result is None


def test_export_user_records(db_session):
    """测试 export_user_records 函数"""
    from services.export_service import export_user_records
    from contextlib import contextmanager
    
    # 创建测试用户和账本记录
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    ledger = create_test_ledger(db_session, user_id=10001, amount=100.0)
    db_session.commit()
    
    # Mock get_session 以使用测试数据库会话
    @contextmanager
    def mock_get_session():
        yield db_session
    
    # Mock pandas 和文件操作
    with patch("services.export_service.get_session", side_effect=mock_get_session), \
         patch("services.export_service._write_dataframe", return_value="/tmp/exports/test.xlsx"):
        result = export_user_records(10001, fmt="xlsx")
        # 应该返回文件路径或 None
        assert result is None or isinstance(result, str)


def test_export_all_records(db_session):
    """测试 export_all_records 函数"""
    from services.export_service import export_all_records
    from contextlib import contextmanager
    
    # 创建测试账本记录
    ledger = create_test_ledger(db_session, user_id=10001, amount=100.0)
    db_session.commit()
    
    # Mock get_session 以使用测试数据库会话
    @contextmanager
    def mock_get_session():
        yield db_session
    
    # Mock pandas 和文件操作
    with patch("services.export_service.get_session", side_effect=mock_get_session), \
         patch("services.export_service._write_dataframe", return_value="/tmp/exports/test.xlsx"):
        result = export_all_records(fmt="xlsx")
        # 应该返回文件路径或 None
        assert result is None or isinstance(result, str)


def test_export_all_users_detail(db_session):
    """测试 export_all_users_detail 函数"""
    from services.export_service import export_all_users_detail
    from contextlib import contextmanager
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    db_session.commit()
    
    # Mock get_session 以使用测试数据库会话
    @contextmanager
    def mock_get_session():
        yield db_session
    
    # Mock pandas 和文件操作
    with patch("services.export_service.get_session", side_effect=mock_get_session), \
         patch("services.export_service._write_dataframe", return_value="/tmp/exports/test.xlsx"):
        result = export_all_users_detail(fmt="xlsx")
        # 应该返回文件路径或 None
        assert result is None or isinstance(result, str)


def test_query_ledgers(db_session):
    """测试 _query_ledgers 函数"""
    from services.export_service import _query_ledgers
    from contextlib import contextmanager
    
    # 创建测试用户和账本记录
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    ledger = create_test_ledger(db_session, user_id=10001, amount=100.0)
    db_session.commit()
    
    # Mock get_session 以使用测试数据库会话
    @contextmanager
    def mock_get_session():
        yield db_session
    
    with patch("services.export_service.get_session", side_effect=mock_get_session):
        # 测试查询账本
        rows = _query_ledgers(user, start=None, end=None, tokens=None, types=None)
        assert isinstance(rows, list)
        assert len(rows) >= 1


def test_rows_to_records(db_session):
    """测试 _rows_to_records 函数"""
    from services.export_service import _rows_to_records
    
    # 创建测试账本记录
    ledger = create_test_ledger(db_session, user_id=10001, amount=100.0)
    db_session.commit()
    
    # 测试转换记录（不需要 mock get_session，因为 _rows_to_records 不直接使用数据库）
    records = _rows_to_records([ledger])
    assert isinstance(records, list)
    assert len(records) == 1
    assert isinstance(records[0], dict)


def test_attach_user_columns(db_session):
    """测试 _attach_user_columns 函数"""
    from services.export_service import _attach_user_columns
    from contextlib import contextmanager
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    db_session.commit()
    
    # 创建测试记录（使用 user_tg_id 而不是 user_id）
    records = [{"user_tg_id": 10001}]
    
    # Mock get_session 以使用测试数据库会话
    @contextmanager
    def mock_get_session():
        yield db_session
    
    with patch("services.export_service.get_session", side_effect=mock_get_session):
        # 测试附加用户列
        _attach_user_columns(records)
        assert len(records) == 1
        # 记录应该包含用户信息
        assert "user_tg_id" in records[0]
        assert "username" in records[0]


def test_get_user_field(db_session):
    """测试 _get_user_field 函数"""
    from services.export_service import _get_user_field
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    
    # 测试获取字段
    result = _get_user_field(user, "username", "name", default="")
    assert result == "testuser"
    
    # 测试不存在的字段
    result = _get_user_field(user, "nonexistent", default="default")
    assert result == "default"


def test_user_balances(db_session):
    """测试 _user_balances 函数"""
    from services.export_service import _user_balances
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    
    # 测试获取余额
    result = _user_balances(user)
    assert isinstance(result, tuple)
    assert len(result) == 4


def test_export_some_users_and_ledger(db_session):
    """测试 export_some_users_and_ledger 函数"""
    from services.export_service import export_some_users_and_ledger
    from contextlib import contextmanager
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    db_session.commit()
    
    # Mock get_session 以使用测试数据库会话
    @contextmanager
    def mock_get_session():
        yield db_session
    
    # Mock pandas 和文件操作
    with patch("services.export_service.get_session", side_effect=mock_get_session), \
         patch("services.export_service._write_dataframe", return_value="/tmp/exports/test.xlsx"):
        result = export_some_users_and_ledger(tg_ids=[10001], fmt="xlsx")
        # 应该返回文件路径或 None
        assert result is None or isinstance(result, str)

