"""
测试 routers/public_group.py
公开群组路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from aiogram.types import CallbackQuery, User as TgUser, Message, Chat
from aiogram.exceptions import TelegramBadRequest


@pytest.fixture
def mock_callback_query():
    """创建模拟的 CallbackQuery"""
    cb = Mock(spec=CallbackQuery)
    cb.from_user = Mock(spec=TgUser)
    cb.from_user.id = 12345
    cb.from_user.language_code = "zh"
    cb.data = "public_group:joined:1"
    cb.message = Mock(spec=Message)
    cb.message.chat = Mock(spec=Chat)
    cb.message.chat.id = 12345
    cb.message.message_id = 100
    cb.message.edit_text = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def mock_message():
    """创建模拟的 Message"""
    msg = Mock(spec=Message)
    msg.from_user = Mock(spec=TgUser)
    msg.from_user.id = 12345
    msg.from_user.username = "testuser"
    msg.from_user.language_code = "zh"
    msg.chat = Mock(spec=Chat)
    msg.chat.id = 12345
    msg.text = "/groups"
    msg.answer = AsyncMock()
    return msg


class TestCmdGroups:
    """测试 cmd_groups 处理函数"""
    
    async def test_cmd_groups_success(self, mock_message):
        """测试 /groups 命令成功"""
        mock_message.text = "/groups"
        
        mock_group = Mock()
        mock_group.id = 1
        mock_group.name = "Test Group"
        mock_group.invite_link = "https://t.me/test"
        mock_group.description = None
        mock_group.is_pinned = False
        mock_group.pinned_until = None
        mock_group.language = None
        mock_group.tags = []
        mock_group.members_count = None
        mock_group.entry_reward_enabled = False
        mock_group.entry_reward_points = None
        
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.public_group.get_session", return_value=mock_session):
            with patch("routers.public_group.list_groups", return_value=[mock_group]):
                with patch("routers.public_group.get_active_campaign_summaries", return_value=[]):
                    from routers.public_group import cmd_groups
                    await cmd_groups(mock_message)
                    
                    # 验证调用了 answer
                    assert mock_message.answer.called
    
    async def test_cmd_groups_empty(self, mock_message):
        """测试没有群组"""
        mock_message.text = "/groups"
        
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.public_group.get_session", return_value=mock_session):
            with patch("routers.public_group.list_groups", return_value=[]):
                with patch("routers.public_group.get_active_campaign_summaries", return_value=[]):
                    from routers.public_group import cmd_groups
                    await cmd_groups(mock_message)
                    
                    # 验证调用了 answer
                    assert mock_message.answer.called


class TestCmdGroupCreate:
    """测试 cmd_group_create 处理函数"""
    
    async def test_cmd_group_create_success(self, mock_message):
        """测试创建群组成功"""
        mock_message.text = "/group_create"
        
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.public_group._is_admin_user", return_value=True):
            with patch("routers.public_group.get_session", return_value=mock_session):
                with patch("routers.public_group.create_group", return_value=(Mock(), True)):
                    from routers.public_group import cmd_group_create
                    await cmd_group_create(mock_message)
                    
                    # 验证调用了 answer
                    assert mock_message.answer.called
    
    async def test_cmd_group_create_not_admin(self, mock_message):
        """测试非管理员创建群组"""
        mock_message.text = "/group_create"
        
        with patch("routers.public_group._is_admin_user", return_value=False):
            from routers.public_group import cmd_group_create
            await cmd_group_create(mock_message)
            
            # 应该调用 answer 显示提示
            assert mock_message.answer.called


class TestCmdGroupPin:
    """测试 cmd_group_pin 处理函数"""
    
    async def test_cmd_group_pin_success(self, mock_message):
        """测试置顶群组成功"""
        mock_message.text = "/group_pin 1"
        
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.public_group._is_admin_user", return_value=True):
            with patch("routers.public_group.get_session", return_value=mock_session):
                with patch("routers.public_group.pin_group", return_value=Mock()):
                    from routers.public_group import cmd_group_pin
                    await cmd_group_pin(mock_message)
                    
                    # 验证调用了 answer
                    assert mock_message.answer.called


class TestCmdGroupUnpin:
    """测试 cmd_group_unpin 处理函数"""
    
    async def test_cmd_group_unpin_success(self, mock_message):
        """测试取消置顶群组成功"""
        mock_message.text = "/group_unpin 1"
        
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.public_group._is_admin_user", return_value=True):
            with patch("routers.public_group.get_session", return_value=mock_session):
                with patch("routers.public_group.unpin_group", return_value=Mock()):
                    from routers.public_group import cmd_group_unpin
                    await cmd_group_unpin(mock_message)
                    
                    # 验证调用了 answer
                    assert mock_message.answer.called


class TestCbPublicGroupJoined:
    """测试 cb_public_group_joined 处理函数"""
    
    async def test_cb_public_group_joined_success(self, mock_callback_query):
        """测试加入群组成功"""
        mock_callback_query.data = "public_group:joined:1"
        
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.public_group.get_session", return_value=mock_session):
            with patch("routers.public_group.join_group", return_value={"reward_claimed": True, "reward_points": 100, "reward_status": "claimed"}):
                from routers.public_group import cb_public_group_joined
                await cb_public_group_joined(mock_callback_query)
                
                # 验证调用了 answer
                assert mock_callback_query.answer.called
    
    async def test_cb_public_group_joined_already_joined(self, mock_callback_query):
        """测试已经加入群组"""
        mock_callback_query.data = "public_group:joined:1"
        
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.public_group.get_session", return_value=mock_session):
            with patch("routers.public_group.join_group", return_value={"reward_claimed": False, "reward_points": 0, "reward_status": "skipped"}):
                from routers.public_group import cb_public_group_joined
                await cb_public_group_joined(mock_callback_query)
                
                # 验证调用了 answer
                assert mock_callback_query.answer.called


class TestPublicGroupHelpers:
    """测试辅助函数"""
    
    def test_is_admin_user(self):
        """测试 _is_admin_user"""
        from routers.public_group import _is_admin_user
        
        with patch("routers.public_group._is_admin", return_value=True):
            assert _is_admin_user(99999) is True
        
        with patch("routers.public_group._is_admin", return_value=False):
            assert _is_admin_user(12345) is False
        
        with patch("routers.public_group._is_admin", side_effect=Exception("test")):
            assert _is_admin_user(12345) is False
    
    def test_format_group_brief(self):
        """测试 _format_group_brief"""
        from routers.public_group import _format_group_brief
        
        mock_group = Mock()
        mock_group.id = 1
        mock_group.name = "Test Group"
        mock_group.is_pinned = False
        mock_group.pinned_until = None
        mock_group.language = None
        mock_group.tags = None
        mock_group.members_count = None
        mock_group.entry_reward_enabled = False
        mock_group.entry_reward_points = None
        
        result = _format_group_brief(mock_group)
        assert "Test Group" in result
        assert "#1" in result

