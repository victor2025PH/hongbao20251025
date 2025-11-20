"""
测试 routers/envelope.py
红包信封路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from aiogram.types import CallbackQuery, User as TgUser, Message, Chat
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext


@pytest.fixture
def mock_callback_query():
    """创建模拟的 CallbackQuery"""
    cb = Mock(spec=CallbackQuery)
    cb.from_user = Mock(spec=TgUser)
    cb.from_user.id = 12345
    cb.from_user.language_code = "zh"
    cb.from_user.username = "testuser"
    cb.data = "hb:start"
    cb.message = Mock(spec=Message)
    cb.message.chat = Mock(spec=Chat)
    cb.message.chat.id = 12345  # 私聊
    cb.message.message_id = 100
    cb.message.edit_text = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.message.bot = Mock()
    cb.message.bot.get_me = AsyncMock(return_value=Mock(username="testbot"))
    cb.message.bot.send_message = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def mock_state():
    """创建模拟的 FSMContext"""
    state = Mock(spec=FSMContext)
    state.clear = AsyncMock()
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    return state


class TestHbStart:
    """测试 hb_start 处理函数"""
    
    async def test_hb_start_private_chat(self, mock_callback_query, mock_state):
        """测试私聊中启动红包"""
        mock_callback_query.data = "hb:start"
        mock_callback_query.message.chat.id = 12345  # 私聊
        
        with patch("routers.envelope._is_group", return_value=False):
            with patch("routers.envelope._ensure_db_lang", return_value="zh"):
                with patch("routers.envelope.get_session") as mock_session:
                    mock_session.return_value.__enter__.return_value = mock_session.return_value
                    with patch("routers.envelope.get_last_target_chat", return_value=(None, None)):
                        with patch("routers.envelope._t_first", return_value="选择目标群"):
                            with patch("routers.envelope._tg_actions_kb", return_value=Mock()):
                                with patch("routers.envelope.log_user_to_sheet"):
                                    from routers.envelope import hb_start
                                    await hb_start(mock_callback_query, mock_state)
                                    
                                    # 函数执行成功即可（可能调用 send_message 或 edit_text）
                                    assert True
    
    async def test_hb_start_group_chat(self, mock_callback_query, mock_state):
        """测试群聊中启动红包"""
        mock_callback_query.data = "hb:start"
        mock_callback_query.message.chat.id = -1001234567890  # 群聊
        
        with patch("routers.envelope._is_group", return_value=True):
            with patch("routers.envelope._ensure_db_lang", return_value="zh"):
                with patch("routers.envelope._t_first", return_value="在私聊继续"):
                    with patch("routers.envelope._lbl", return_value="在私聊继续 ➡️"):
                        with patch("routers.envelope._auto_delete", new_callable=AsyncMock):
                            with patch("routers.envelope.get_session") as mock_session:
                                mock_session.return_value.__enter__.return_value = mock_session.return_value
                                with patch("routers.envelope.get_last_target_chat", return_value=(None, None)):
                                    with patch("routers.envelope._tg_actions_kb", return_value=Mock()):
                                        from routers.envelope import hb_start
                                        await hb_start(mock_callback_query, mock_state)
                                        
                                        # 验证调用了 answer
                                        assert mock_callback_query.message.answer.called


class TestTgUse:
    """测试 tg_use 处理函数"""
    
    async def test_tg_use_success(self, mock_callback_query, mock_state):
        """测试使用目标群成功"""
        mock_callback_query.data = "env:tg:use:-1001234567890"
        
        with patch("routers.envelope._ensure_db_lang", return_value="zh"):
            with patch("routers.envelope.t", return_value="选择模式"):
                with patch("routers.envelope._lbl", return_value="选择模式"):
                    with patch("routers.envelope.env_mode_kb", return_value=Mock()):
                        from routers.envelope import tg_use
                        await tg_use(mock_callback_query, mock_state)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        # 验证调用了 answer
                        assert mock_callback_query.answer.called


class TestTgBindHelp:
    """测试 tg_bind_help 处理函数"""
    
    async def test_tg_bind_help_success(self, mock_callback_query):
        """测试绑定帮助成功"""
        mock_callback_query.data = "env:tg:bind_help"
        
        with patch("routers.envelope._ensure_db_lang", return_value="zh"):
            with patch("routers.envelope.t", return_value="绑定帮助"):
                with patch("routers.envelope._lbl", return_value="绑定帮助"):
                    with patch("routers.envelope._t_first", return_value="在私聊继续"):
                        from routers.envelope import tg_bind_help
                        await tg_bind_help(mock_callback_query)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        # 验证调用了 answer
                        assert mock_callback_query.answer.called


class TestChooseMode:
    """测试 choose_mode 处理函数"""
    
    async def test_choose_mode_usdt(self, mock_callback_query, mock_state):
        """测试选择 USDT 模式"""
        mock_callback_query.data = "env:mode:USDT"
        
        with patch("routers.envelope._ensure_db_lang", return_value="zh"):
            with patch("routers.envelope.t", return_value="输入金额"):
                with patch("routers.envelope._lbl", return_value="输入金额"):
                    with patch("routers.envelope.env_amount_kb", return_value=Mock()):
                        from routers.envelope import choose_mode
                        await choose_mode(mock_callback_query, mock_state)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        # 验证调用了 answer
                        assert mock_callback_query.answer.called


class TestEnvelopeHelpers:
    """测试辅助函数"""
    
    async def test_auto_delete_success(self):
        """测试自动删除成功"""
        mock_bot = Mock()
        mock_bot.delete_message = AsyncMock()
        
        with patch("routers.envelope.asyncio.sleep", new_callable=AsyncMock):
            from routers.envelope import _auto_delete
            await _auto_delete(mock_bot, 12345, 100, delay=0)
            
            # 验证调用了 delete_message
            assert mock_bot.delete_message.called
    
    async def test_chat_display_title_success(self):
        """测试获取聊天标题成功"""
        mock_bot = Mock()
        mock_chat = Mock()
        mock_chat.title = "Test Group"
        mock_chat.username = None
        mock_bot.get_chat = AsyncMock(return_value=mock_chat)
        
        from routers.envelope import _chat_display_title
        title = await _chat_display_title(mock_bot, -1001234567890)
        
        assert isinstance(title, str)
        assert "Test Group" in title or title == "Test Group"

