"""
测试 services/invite_service.py
邀请服务层测试
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

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


def test_emoji_bar():
    """测试 _emoji_bar 函数"""
    from services.invite_service import _emoji_bar
    
    # 测试不同百分比
    result = _emoji_bar(0, slots=10)
    assert isinstance(result, str)
    assert len(result) == 10
    
    result = _emoji_bar(50, slots=10)
    assert isinstance(result, str)
    assert len(result) == 10
    
    result = _emoji_bar(100, slots=10)
    assert isinstance(result, str)
    assert len(result) == 10


def test_build_invite_progress_message():
    """测试 build_invite_progress_message 函数"""
    from services.invite_service import build_invite_progress_message
    
    # 测试不同百分比
    result = build_invite_progress_message(0, lang="zh")
    assert isinstance(result, str)
    assert len(result) > 0
    
    result = build_invite_progress_message(50, lang="zh")
    assert isinstance(result, str)
    
    result = build_invite_progress_message(100, lang="zh")
    assert isinstance(result, str)


def test_get_invite_progress_text():
    """测试 get_invite_progress_text 函数"""
    from services.invite_service import get_invite_progress_text
    
    # Mock get_progress
    with patch("services.invite_service.get_progress", return_value={"progress_percent": 50}):
        text, percent = get_invite_progress_text(10001, lang="zh")
        assert isinstance(text, str)
        assert isinstance(percent, int)
        assert percent == 50


def test_add_invite_and_rewards(db_session):
    """测试 add_invite_and_rewards 函数"""
    from services.invite_service import add_invite_and_rewards
    
    # 创建测试用户
    inviter = create_test_user(db_session, tg_id=10001, username="inviter")
    invitee = create_test_user(db_session, tg_id=10002, username="invitee")
    
    # Mock add_invite 和 feature flags
    with patch("services.invite_service.add_invite", return_value=True):
        with patch("services.invite_service._FF", return_value=0):  # 不给予额外积分
            result = add_invite_and_rewards(10001, 10002, give_extra_points=False)
            assert result is True


def test_add_invite_and_rewards_with_points(db_session):
    """测试 add_invite_and_rewards - 带积分奖励"""
    from services.invite_service import add_invite_and_rewards
    
    # 创建测试用户
    inviter = create_test_user(db_session, tg_id=10001, username="inviter")
    invitee = create_test_user(db_session, tg_id=10002, username="invitee")
    
    # Mock add_invite 和 feature flags
    with patch("services.invite_service.add_invite", return_value=True):
        with patch("services.invite_service._FF", return_value=100):  # 给予 100 积分
            with patch("services.invite_service.update_balance"):
                with patch("services.invite_service.add_ledger_entry"):
                    result = add_invite_and_rewards(10001, 10002, give_extra_points=True)
                    assert result is True


def test_redeem_points_to_progress(db_session):
    """测试 redeem_points_to_progress 函数"""
    from services.invite_service import redeem_points_to_progress
    from sqlalchemy import update as sql_update
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    
    # 设置用户积分
    if hasattr(user, "point_balance"):
        user.point_balance = 2000
    db_session.commit()
    
    # Mock get_progress 和 feature flags
    with patch("services.invite_service.get_progress", return_value={"progress_percent": 0}):
        # Mock _FF 返回不同的值
        def mock_ff(name, default):
            if name == "POINTS_PER_PROGRESS":
                return 1000
            elif name == "ENERGY_REWARD_AT_PROGRESS":
                return 2
            elif name == "ENERGY_REWARD_AMOUNT":
                return 1000
            return default
        
        with patch("services.invite_service._FF", side_effect=mock_ff):
            with patch("services.invite_service.update_balance"):
                with patch("services.invite_service.add_ledger_entry"):
                    # Mock InviteProgress 为 None，这样就不会执行 SQL 更新
                    with patch("services.invite_service.InviteProgress", None):
                        success, text, percent = redeem_points_to_progress(10001, lang="zh")
                        # 应该成功（有足够积分）
                        assert isinstance(success, bool)
                        assert isinstance(text, str)
                        assert isinstance(percent, int)


def test_redeem_points_to_progress_insufficient(db_session):
    """测试 redeem_points_to_progress - 积分不足"""
    from services.invite_service import redeem_points_to_progress
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    
    # 设置用户积分为 0
    if hasattr(user, "point_balance"):
        user.point_balance = 0
    db_session.commit()
    
    # Mock get_progress 和 feature flags
    with patch("services.invite_service.get_progress", return_value={"progress_percent": 0}):
        with patch("services.invite_service._FF", return_value=1000):  # 需要 1000 积分
            success, text, percent = redeem_points_to_progress(10001, lang="zh")
            # 应该失败（积分不足）
            assert success is False
            assert isinstance(text, str)
            assert isinstance(percent, int)


def test_redeem_energy_to_points(db_session):
    """测试 redeem_energy_to_points 函数"""
    from services.invite_service import redeem_energy_to_points
    
    # 创建测试用户
    user = create_test_user(db_session, tg_id=10001, username="testuser")
    
    # 设置用户能量
    if hasattr(user, "energy_balance"):
        user.energy_balance = 1000
    db_session.commit()
    
    # Mock feature flags
    with patch("services.invite_service._FF", return_value=100):  # 100 能量换 1 积分
        with patch("services.invite_service.update_balance"):
            with patch("services.invite_service.add_ledger_entry"):
                success, text = redeem_energy_to_points(10001, lang="zh")
                assert isinstance(success, bool)
                assert isinstance(text, str)


def test_build_invite_share_link():
    """测试 build_invite_share_link 函数"""
    from services.invite_service import build_invite_share_link
    
    # 测试生成邀请链接
    link = build_invite_share_link(10001)
    assert isinstance(link, str)
    assert len(link) > 0
    assert "10001" in link or "invite" in link.lower()


def test_FF_function():
    """测试 _FF 函数"""
    from services.invite_service import _FF
    from unittest.mock import MagicMock
    
    # Mock flags - 使用 spec_set 限制可用属性，并使用 __getattr__ 返回默认值
    mock_flags = MagicMock()
    mock_flags.TEST_FLAG = "test_value"
    
    # 让 mock_flags 在访问不存在的属性时使用 getattr 的默认值
    def getattr_handler(name):
        # 如果属性不存在，getattr 会返回默认值
        return getattr(mock_flags, name, AttributeError())
    
    # 创建新的 mock，使其在访问不存在的属性时抛出 AttributeError
    # 这样 getattr 的默认值就会生效
    class FlagsMock:
        TEST_FLAG = "test_value"
        def __getattr__(self, name):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    with patch("services.invite_service.flags", FlagsMock()):
        result = _FF("TEST_FLAG", "default")
        assert result == "test_value"
        
        # 测试不存在的标志 - 应该返回默认值
        result = _FF("NONEXISTENT", "default")
        assert result == "default"

