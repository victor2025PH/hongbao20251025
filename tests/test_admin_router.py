"""
测试 routers/admin.py
管理员功能路由测试
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
    cb.data = "admin:main"
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
    msg.text = "/admin"
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


class TestCmdAdmin:
    """测试 cmd_admin 处理函数"""
    
    async def test_cmd_admin_success(self, mock_message, mock_state):
        """测试 /admin 命令成功"""
        mock_message.text = "/admin"
        
        with patch("routers.admin._must_admin", return_value=True):
            with patch("routers.admin._db_lang", return_value="zh"):
                with patch("routers.admin._t_first", return_value="管理员面板"):
                    with patch("routers.admin._admin_menu", return_value=Mock()):
                        from routers.admin import cmd_admin
                        await cmd_admin(mock_message, mock_state)
                        
                        # 验证调用了 answer
                        assert mock_message.answer.called


class TestAdminMain:
    """测试 admin_main 处理函数"""
    
    async def test_admin_main_success(self, mock_callback_query, mock_state):
        """测试管理员主页面成功"""
        mock_callback_query.data = "admin:main"
        
        with patch("routers.admin._must_admin", return_value=True):
            with patch("routers.admin._db_lang", return_value="zh"):
                with patch("routers.admin._t_first", return_value="管理员面板"):
                    with patch("routers.admin._admin_menu", return_value=Mock()):
                        from routers.admin import admin_main
                        await admin_main(mock_callback_query, mock_state)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        # 验证调用了 answer
                        assert mock_callback_query.answer.called
    
    async def test_admin_main_not_admin(self, mock_callback_query, mock_state):
        """测试非管理员访问"""
        mock_callback_query.data = "admin:main"
        
        with patch("routers.admin._must_admin", return_value=False):
            from routers.admin import admin_main
            await admin_main(mock_callback_query, mock_state)
            
            # 非管理员时直接返回，不调用任何方法
            assert not mock_callback_query.message.edit_text.called
            assert not mock_callback_query.answer.called


class TestAdminCoversEntry:
    """测试 admin_covers_entry 处理函数"""
    
    async def test_admin_covers_entry_success(self, mock_callback_query, mock_state):
        """测试封面管理入口成功"""
        mock_callback_query.data = "admin:covers"
        
        with patch("routers.admin._must_admin", return_value=True):
            with patch("routers.admin.list_covers", return_value=[]):
                with patch("routers.admin._db_lang", return_value="zh"):
                    with patch("routers.admin._t_first", return_value="封面管理"):
                        with patch("routers.admin._admin_menu", return_value=Mock()):
                            with patch("routers.admin._cb_safe_answer", new_callable=AsyncMock):
                                from routers.admin import admin_covers_entry
                                await admin_covers_entry(mock_callback_query, mock_state)
                                
                                # 验证调用了 edit_text 或 answer
                                assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestAdminCoverList:
    """测试 admin_cover_list 处理函数"""
    
    async def test_admin_cover_list_success(self, mock_callback_query, mock_state):
        """测试封面列表成功"""
        mock_callback_query.data = "admin:covers:list"
        
        with patch("routers.admin._must_admin", return_value=True):
            with patch("routers.admin.list_covers", return_value=[]):
                with patch("routers.admin._show_covers_page", new_callable=AsyncMock):
                    with patch("routers.admin._cb_safe_answer", new_callable=AsyncMock):
                        from routers.admin import admin_cover_list
                        await admin_cover_list(mock_callback_query, mock_state)
                        
                        # 函数执行成功即可
                        assert True


class TestAdminHelpers:
    """测试辅助函数"""
    
    async def test_must_admin_true(self, mock_callback_query):
        """测试管理员检查成功"""
        with patch("routers.admin._is_admin", return_value=True):
            from routers.admin import _must_admin
            result = await _must_admin(mock_callback_query)
            assert result is True
    
    async def test_must_admin_false(self, mock_callback_query):
        """测试非管理员"""
        with patch("routers.admin._is_admin", return_value=False):
            from routers.admin import _must_admin
            result = await _must_admin(mock_callback_query)
            assert result is False
    
    async def test_cb_safe_answer_success(self, mock_callback_query):
        """测试安全应答成功"""
        from routers.admin import _cb_safe_answer
        await _cb_safe_answer(mock_callback_query, "测试消息", show_alert=False)
        
        mock_callback_query.answer.assert_called_once()
    
    async def test_cb_safe_answer_telegram_bad_request(self, mock_callback_query):
        """测试查询过期时忽略错误"""
        mock_callback_query.answer = AsyncMock(
            side_effect=TelegramBadRequest(method="answerCallbackQuery", message="query is too old")
        )
        
        from routers.admin import _cb_safe_answer
        # 不应该抛出异常
        await _cb_safe_answer(mock_callback_query, "测试消息", show_alert=False)
        
        mock_callback_query.answer.assert_called_once()

