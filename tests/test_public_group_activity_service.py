"""
测试 services/public_group_activity.py
公开群组活动服务层测试
"""
import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from models.public_group import PublicGroup, PublicGroupStatus, PublicGroupActivity
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


def test_get_active_campaign_summaries(db_session):
    """测试 get_active_campaign_summaries 函数"""
    from services.public_group_activity import get_active_campaign_summaries
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试获取活动摘要
    summaries = get_active_campaign_summaries(db_session)
    assert isinstance(summaries, list)


def test_summarize_activity_performance(db_session):
    """测试 summarize_activity_performance 函数"""
    from services.public_group_activity import summarize_activity_performance
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试汇总活动表现（不需要 group_id，只需要 session）
    result = summarize_activity_performance(db_session)
    assert isinstance(result, dict)


def test_summarize_conversions(db_session):
    """测试 summarize_conversions 函数"""
    from services.public_group_activity import summarize_conversions
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试汇总转化（需要 start_date 和 end_date）
    start_date = datetime.now(UTC) - timedelta(days=7)
    end_date = datetime.now(UTC)
    result = summarize_conversions(db_session, start_date=start_date, end_date=end_date)
    assert isinstance(result, list)


def test_summarize_conversion_overview(db_session):
    """测试 summarize_conversion_overview 函数"""
    from services.public_group_activity import summarize_conversion_overview
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试汇总转化概览（需要 start_date 和 end_date）
    start_date = datetime.now(UTC) - timedelta(days=7)
    end_date = datetime.now(UTC)
    result = summarize_conversion_overview(db_session, start_date=start_date, end_date=end_date)
    assert isinstance(result, dict)


def test_daily_conversion_trend(db_session):
    """测试 daily_conversion_trend 函数"""
    from services.public_group_activity import daily_conversion_trend
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试每日转化趋势（需要 start_date 和 end_date，不需要 days）
    start_date = datetime.now(UTC) - timedelta(days=7)
    end_date = datetime.now(UTC)
    result = daily_conversion_trend(db_session, start_date=start_date, end_date=end_date)
    assert isinstance(result, list)


def test_find_conversion_alerts(db_session):
    """测试 find_conversion_alerts 函数"""
    from services.public_group_activity import find_conversion_alerts
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试查找转化警报（需要 start_date 和 end_date）
    start_date = datetime.now(UTC) - timedelta(days=7)
    end_date = datetime.now(UTC)
    alerts = find_conversion_alerts(db_session, start_date=start_date, end_date=end_date)
    assert isinstance(alerts, list)


def test_list_activities(db_session):
    """测试 list_activities 函数"""
    from services.public_group_activity import list_activities
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试列出活动（只需要 session，不需要 group_id）
    activities = list_activities(db_session)
    assert isinstance(activities, list)


def test_create_activity(db_session):
    """测试 create_activity 函数"""
    from services.public_group_activity import create_activity
    
    # 创建测试群组
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    
    # 测试创建活动（需要 name 参数，不需要 group_id, title, description）
    activity = create_activity(
        db_session,
        name="Test Activity",
        description="Test Description",
    )
    assert activity is not None
    assert activity.name == "Test Activity"


def test_toggle_activity(db_session):
    """测试 toggle_activity 函数"""
    from services.public_group_activity import toggle_activity, create_activity
    
    # 创建测试群组和活动
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    activity = create_activity(
        db_session,
        name="Test Activity",
        description="Test Description",
    )
    
    # 测试切换活动状态（需要 activity_id 和 is_active）
    result = toggle_activity(db_session, activity_id=activity.id, is_active=False)
    assert result is not None


def test_bulk_update_activities(db_session):
    """测试 bulk_update_activities 函数"""
    from services.public_group_activity import bulk_update_activities, create_activity
    
    # 创建测试群组和活动
    group = create_test_group(db_session, creator_tg_id=10001, name="Test Group")
    activity = create_activity(
        db_session,
        name="Test Activity",
        description="Test Description",
    )
    
    # 测试批量更新活动（需要 action 参数）
    result = bulk_update_activities(
        db_session,
        activity_ids=[activity.id],
        action="update",
        updates={"name": "Updated Activity"},
    )
    assert result is not None
    assert isinstance(result, dict)
    assert "updated" in result
    assert "errors" in result

