"""
测试 routers/help.py
帮助相关路由测试
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
    cb.data = "help:main"
    cb.message = Mock(spec=Message)
    cb.message.chat = Mock(spec=Chat)
    cb.message.chat.id = 12345
    cb.message.message_id = 100
    cb.message.answer = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def mock_message():
    """创建模拟的 Message"""
    msg = Mock(spec=Message)
    msg.from_user = Mock(spec=TgUser)
    msg.from_user.id = 12345
    msg.from_user.language_code = "zh"
    msg.chat = Mock(spec=Chat)
    msg.chat.id = 12345
    msg.text = "测试问题"
    msg.answer = AsyncMock()
    return msg


class TestHelpMain:
    """测试 help_main 处理函数"""
    
    async def test_help_main_success(self, mock_callback_query):
        """测试帮助主页面成功"""
        mock_callback_query.data = "help:main"
        
        with patch("routers.help._get_user_lang", return_value="zh"):
            with patch("routers.help.t", return_value="帮助"):
                from routers.help import help_main
                await help_main(mock_callback_query)
                
                # 验证调用了 answer
                assert mock_callback_query.message.answer.called
                assert mock_callback_query.answer.called


class TestHelpFaq:
    """测试 help_faq 处理函数"""
    
    async def test_help_faq_send(self, mock_callback_query):
        """测试发送红包 FAQ"""
        mock_callback_query.data = "help:faq:send"
        
        with patch("routers.help._get_user_lang", return_value="zh"):
            with patch("routers.help._faq_text", return_value="发送红包说明"):
                with patch("routers.help.t", return_value="返回"):
                    from routers.help import help_faq
                    await help_faq(mock_callback_query)
                    
                    # 验证调用了 answer
                    assert mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called
    
    async def test_help_faq_grab(self, mock_callback_query):
        """测试抢红包 FAQ"""
        mock_callback_query.data = "help:faq:grab"
        
        with patch("routers.help._get_user_lang", return_value="zh"):
            with patch("routers.help._faq_text", return_value="抢红包说明"):
                with patch("routers.help.t", return_value="返回"):
                    from routers.help import help_faq
                    await help_faq(mock_callback_query)
                    
                    # 验证调用了 answer
                    assert mock_callback_query.message.answer.called


class TestHelpAskAi:
    """测试 help_ask_ai 处理函数"""
    
    async def test_help_ask_ai_success(self, mock_callback_query):
        """测试进入 AI 模式成功"""
        mock_callback_query.data = "help:ask_ai"
        
        with patch("routers.help._get_user_lang", return_value="zh"):
            with patch("routers.help.t", return_value="AI 助手"):
                with patch("routers.help._AI_ACTIVE_USERS", set()):
                    from routers.help import help_ask_ai
                    await help_ask_ai(mock_callback_query)
                    
                    # 验证调用了 answer
                    assert mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called
                    # 验证用户被添加到 AI 活跃用户集合
                    from routers.help import _AI_ACTIVE_USERS
                    assert 12345 in _AI_ACTIVE_USERS


class TestHelpExitAi:
    """测试 help_exit_ai 处理函数"""
    
    async def test_help_exit_ai_success(self, mock_callback_query):
        """测试退出 AI 模式成功"""
        mock_callback_query.data = "help:exit_ai"
        
        with patch("routers.help._get_user_lang", return_value="zh"):
            with patch("routers.help.t", return_value="已退出"):
                with patch("routers.help._AI_ACTIVE_USERS", {12345}):
                    from routers.help import help_exit_ai
                    await help_exit_ai(mock_callback_query)
                    
                    # 验证调用了 answer
                    assert mock_callback_query.answer.called
                    # 验证用户从 AI 活跃用户集合中移除
                    from routers.help import _AI_ACTIVE_USERS
                    assert 12345 not in _AI_ACTIVE_USERS


class TestHelpHelpers:
    """测试辅助函数"""
    
    def test_canon_lang(self):
        """测试 _canon_lang"""
        from routers.help import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("zh-CN") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("en-US") == "en"
        assert _canon_lang("fr") == "zh"  # 默认
        assert _canon_lang(None) == "zh"
        assert _canon_lang("") == "zh"

