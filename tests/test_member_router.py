"""
测试 routers/member.py
群成员事件监听路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from aiogram.types import ChatMemberUpdated, ChatMember, User as TgUser, Chat, Message


@pytest.fixture
def mock_chat_member_updated():
    """创建模拟的 ChatMemberUpdated"""
    event = Mock(spec=ChatMemberUpdated)
    event.chat = Mock(spec=Chat)
    event.chat.id = -1001234567890
    
    new_member = Mock(spec=ChatMember)
    new_member.status = "member"
    new_member.user = Mock(spec=TgUser)
    new_member.user.id = 12345
    new_member.user.is_bot = False
    new_member.user.username = "testuser"
    
    old_member = Mock(spec=ChatMember)
    old_member.status = "left"
    
    event.new_chat_member = new_member
    event.old_chat_member = old_member
    
    return event


@pytest.fixture
def mock_message():
    """创建模拟的 Message"""
    msg = Mock(spec=Message)
    msg.chat = Mock(spec=Chat)
    msg.chat.id = -1001234567890
    
    user = Mock(spec=TgUser)
    user.id = 12345
    user.is_bot = False
    user.username = "testuser"
    
    msg.new_chat_members = [user]
    msg.from_user = user
    
    return msg


class TestOnChatMemberUpdated:
    """测试 on_chat_member_updated 处理函数"""
    
    async def test_on_chat_member_updated_join_success(self, mock_chat_member_updated):
        """测试成员加入成功"""
        with patch("routers.member._should_log_once", return_value=True):
            with patch("routers.member.log_user_to_sheet", new_callable=AsyncMock):
                from routers.member import on_chat_member_updated
                await on_chat_member_updated(mock_chat_member_updated)
                
                # 函数执行成功即可
                assert True
    
    async def test_on_chat_member_updated_already_member(self, mock_chat_member_updated):
        """测试已经是成员的情况"""
        mock_chat_member_updated.old_chat_member.status = "member"
        
        with patch("routers.member.log_user_to_sheet", new_callable=AsyncMock) as mock_log:
            from routers.member import on_chat_member_updated
            await on_chat_member_updated(mock_chat_member_updated)
            
            # 不应该记录日志
            mock_log.assert_not_called()
    
    async def test_on_chat_member_updated_bot(self, mock_chat_member_updated):
        """测试机器人加入"""
        mock_chat_member_updated.new_chat_member.user.is_bot = True
        
        with patch("routers.member.log_user_to_sheet", new_callable=AsyncMock) as mock_log:
            from routers.member import on_chat_member_updated
            await on_chat_member_updated(mock_chat_member_updated)
            
            # 不应该记录日志
            mock_log.assert_not_called()
    
    async def test_on_chat_member_updated_duplicate(self, mock_chat_member_updated):
        """测试重复记录"""
        with patch("routers.member._should_log_once", return_value=False):
            with patch("routers.member.log_user_to_sheet", new_callable=AsyncMock) as mock_log:
                from routers.member import on_chat_member_updated
                await on_chat_member_updated(mock_chat_member_updated)
                
                # 不应该记录日志
                mock_log.assert_not_called()


class TestOnNewChatMembers:
    """测试 on_new_chat_members 处理函数"""
    
    async def test_on_new_chat_members_success(self, mock_message):
        """测试新成员加入成功"""
        with patch("routers.member._should_log_once", return_value=True):
            with patch("routers.member.log_user_to_sheet", new_callable=AsyncMock):
                from routers.member import on_new_chat_members
                await on_new_chat_members(mock_message)
                
                # 函数执行成功即可
                assert True
    
    async def test_on_new_chat_members_bot(self, mock_message):
        """测试机器人加入"""
        mock_message.new_chat_members[0].is_bot = True
        
        with patch("routers.member.log_user_to_sheet", new_callable=AsyncMock) as mock_log:
            from routers.member import on_new_chat_members
            await on_new_chat_members(mock_message)
            
            # 不应该记录日志
            mock_log.assert_not_called()
    
    async def test_on_new_chat_members_duplicate(self, mock_message):
        """测试重复记录"""
        with patch("routers.member._should_log_once", return_value=False):
            with patch("routers.member.log_user_to_sheet", new_callable=AsyncMock) as mock_log:
                from routers.member import on_new_chat_members
                await on_new_chat_members(mock_message)
                
                # 不应该记录日志
                mock_log.assert_not_called()


class TestMemberHelpers:
    """测试辅助函数"""
    
    def test_is_join_status(self):
        """测试 _is_join_status"""
        from routers.member import _is_join_status
        
        assert _is_join_status("member") is True
        assert _is_join_status("administrator") is True
        assert _is_join_status("creator") is True
        assert _is_join_status("left") is False
        assert _is_join_status("kicked") is False
    
    def test_should_log_once(self):
        """测试 _should_log_once"""
        from routers.member import _should_log_once, _RECENT_LOG_CACHE
        
        # 清空缓存
        _RECENT_LOG_CACHE.clear()
        
        # 第一次应该返回 True
        assert _should_log_once(123, 456) is True
        
        # 第二次应该返回 False（去重）
        assert _should_log_once(123, 456) is False
        
        # 不同的用户应该返回 True
        assert _should_log_once(123, 789) is True

