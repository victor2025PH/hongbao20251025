"""
测试 services/public_group_tracking.py
公开群组跟踪服务层测试
"""
import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import patch
from sqlalchemy.orm import Session

from models.public_group import PublicGroup, PublicGroupEvent, PublicGroupStatus


def create_test_group(
    session: Session,
    creator_tg_id: int = 10001,
    name: str = "Test Group",
    invite_link: str = "https://t.me/test",
) -> PublicGroup:
    """创建测试公开群组"""
    group = PublicGroup(
        creator_tg_id=creator_tg_id,
        name=name,
        invite_link=invite_link,
        status=PublicGroupStatus.ACTIVE,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def test_normalize_context():
    """测试 _normalize_context 函数"""
    from services.public_group_tracking import _normalize_context
    
    # 测试有效上下文
    context = {"key": "value", "number": 123}
    result = _normalize_context(context)
    assert isinstance(result, str)
    assert "key" in result
    
    # 测试 None
    assert _normalize_context(None) is None
    
    # 测试空字典
    assert _normalize_context({}) is None


def test_record_event(db_session):
    """测试 record_event 函数"""
    from services.public_group_tracking import record_event
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试记录事件
    event = record_event(
        db_session,
        group_id=group.id,
        event_type="view",
        user_tg_id=10001,
        context={"source": "test"},
    )
    assert event is not None
    assert event.group_id == group.id
    assert event.event_type == "view"
    
    db_session.commit()


def test_record_event_invalid_type(db_session):
    """测试 record_event - 无效事件类型"""
    from services.public_group_tracking import record_event
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试无效事件类型
    with pytest.raises(ValueError):
        record_event(
            db_session,
            group_id=group.id,
            event_type="invalid",
            user_tg_id=10001,
        )


def test_record_event_all_types(db_session):
    """测试 record_event - 所有允许的事件类型"""
    from services.public_group_tracking import record_event
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试所有允许的事件类型
    for event_type in ["view", "click", "join"]:
        event = record_event(
            db_session,
            group_id=group.id,
            event_type=event_type,
            user_tg_id=10001,
        )
        assert event is not None
        assert event.event_type == event_type
    
    db_session.commit()


def test_period_to_timedelta():
    """测试 _period_to_timedelta 函数"""
    from services.public_group_tracking import _period_to_timedelta
    
    # 测试标准周期
    assert _period_to_timedelta("1d") == timedelta(days=1)
    assert _period_to_timedelta("7d") == timedelta(days=7)
    assert _period_to_timedelta("30d") == timedelta(days=30)
    assert _period_to_timedelta("90d") == timedelta(days=90)
    
    # 测试别名
    assert _period_to_timedelta("24h") == timedelta(days=1)
    assert _period_to_timedelta("week") == timedelta(days=7)
    assert _period_to_timedelta("month") == timedelta(days=30)
    assert _period_to_timedelta("quarter") == timedelta(days=90)
    
    # 测试自定义天数
    assert _period_to_timedelta("5d") == timedelta(days=5)
    assert _period_to_timedelta("14d") == timedelta(days=14)
    
    # 测试无效周期
    with pytest.raises(ValueError):
        _period_to_timedelta("invalid")


def test_fetch_conversion_summary(db_session):
    """测试 fetch_conversion_summary 函数"""
    from services.public_group_tracking import fetch_conversion_summary
    
    # 创建测试群组和事件
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试获取转化摘要
    result = fetch_conversion_summary(db_session, period="7d", limit=10)
    assert isinstance(result, dict)
    assert "period" in result
    assert "totals" in result
    assert "conversion" in result
    assert "top_groups" in result


def test_fetch_conversion_summary_different_periods(db_session):
    """测试 fetch_conversion_summary - 不同周期"""
    from services.public_group_tracking import fetch_conversion_summary
    
    # 测试不同周期
    for period in ["1d", "7d", "30d", "90d"]:
        result = fetch_conversion_summary(db_session, period=period, limit=10)
        assert isinstance(result, dict)
        assert result["period"] == period


def test_fetch_dashboard_metrics(db_session):
    """测试 fetch_dashboard_metrics 函数"""
    from services.public_group_tracking import fetch_dashboard_metrics
    
    # 创建测试群组和事件
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试获取仪表板指标
    result = fetch_dashboard_metrics(db_session, days=14, top_n=5)
    assert isinstance(result, dict)
    assert "timeline" in result
    assert "top_groups" in result


def test_fetch_dashboard_metrics_invalid_days(db_session):
    """测试 fetch_dashboard_metrics - 无效天数"""
    from services.public_group_tracking import fetch_dashboard_metrics
    
    # 测试无效天数
    with pytest.raises(ValueError):
        fetch_dashboard_metrics(db_session, days=0)
    
    with pytest.raises(ValueError):
        fetch_dashboard_metrics(db_session, days=-1)


def test_fetch_user_history(db_session):
    """测试 fetch_user_history 函数"""
    from services.public_group_tracking import fetch_user_history
    
    # 创建测试群组和事件
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试获取用户历史
    result = fetch_user_history(db_session, user_tg_id=10001, limit=10)
    assert isinstance(result, list)

