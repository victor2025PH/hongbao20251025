"""
测试 routers/admin_adjust.py
管理员调整功能路由测试
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
    cb.from_user.id = 99999  # 管理员 ID
    cb.from_user.language_code = "zh"
    cb.data = "admin:adjust"
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
    msg.from_user.id = 99999  # 管理员 ID
    msg.from_user.username = "admin"
    msg.from_user.language_code = "zh"
    msg.chat = Mock(spec=Chat)
    msg.chat.id = 12345
    msg.text = "/adjust"
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def mock_state():
    """创建模拟的 FSMContext"""
    state = Mock(spec=FSMContext)
    state.clear = AsyncMock()
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    return state


class TestAdminAdjustEntry:
    """测试 admin_adjust_entry 处理函数"""
    
    async def test_admin_adjust_entry_success(self, mock_callback_query, mock_state):
        """测试调整入口成功"""
        mock_callback_query.data = "admin:adjust"
        
        with patch("routers.admin_adjust._is_admin_uid", return_value=True):
            with patch("routers.admin_adjust._db_lang_or_fallback", return_value="zh"):
                with patch("routers.admin_adjust.t", return_value="调整余额"):
                    with patch("routers.admin_adjust._kb", return_value=Mock()):
                        with patch("routers.admin_adjust._btn", return_value=Mock()):
                            from routers.admin_adjust import admin_adjust_entry
                            await admin_adjust_entry(mock_callback_query, mock_state)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestAdminAdjustCmd:
    """测试 admin_adjust_cmd 处理函数"""
    
    async def test_admin_adjust_cmd_success(self, mock_message, mock_state):
        """测试 /adjust 命令成功"""
        mock_message.text = "/adjust"
        
        with patch("routers.admin_adjust._is_admin_uid", return_value=True):
            with patch("routers.admin_adjust._db_lang_or_fallback", return_value="zh"):
                with patch("routers.admin_adjust.t", return_value="调整余额"):
                    with patch("routers.admin_adjust._kb", return_value=Mock()):
                        with patch("routers.admin_adjust._btn", return_value=Mock()):
                            from routers.admin_adjust import admin_adjust_cmd
                            await admin_adjust_cmd(mock_message, mock_state)
                            
                            # 验证调用了 answer
                            assert mock_message.answer.called


class TestAdjCancel:
    """测试 adj_cancel 处理函数"""
    
    async def test_adj_cancel_success(self, mock_callback_query, mock_state):
        """测试取消调整成功"""
        mock_callback_query.data = "adj:cancel"
        
        with patch("routers.admin_adjust._is_admin_uid", return_value=True):
            with patch("routers.admin_adjust._db_lang_or_fallback", return_value="zh"):
                with patch("routers.admin_adjust.t", return_value="已取消"):
                    with patch("routers.admin_adjust._kb", return_value=Mock()):
                        with patch("routers.admin_adjust._btn", return_value=Mock()):
                            from routers.admin_adjust import adj_cancel
                            await adj_cancel(mock_callback_query, mock_state)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestAdminAdjustHelpers:
    """测试辅助函数"""
    
    async def test_resolve_targets_success(self):
        """测试解析目标用户成功"""
        mock_bot = Mock()
        mock_bot.get_chat = AsyncMock(return_value=Mock(id=12345))
        
        with patch("routers.admin_adjust.get_or_create_user", return_value=Mock(id=12345)):
            from routers.admin_adjust import _resolve_targets
            tg_ids, errors = await _resolve_targets("12345", "zh", mock_bot)
            
            assert len(tg_ids) > 0
            assert isinstance(tg_ids, list)
            assert isinstance(errors, list)

