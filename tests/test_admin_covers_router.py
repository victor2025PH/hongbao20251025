"""
测试 routers/admin_covers.py
管理员封面管理路由测试
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
    cb.data = "admin:covers"
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
    msg.from_user.language_code = "zh"
    msg.chat = Mock(spec=Chat)
    msg.chat.id = 12345
    msg.text = "test"
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


class TestAdminCoversEntry:
    """测试 admin_covers_entry 处理函数"""
    
    async def test_admin_covers_entry_success(self, mock_callback_query, mock_state):
        """测试封面管理入口成功"""
        mock_callback_query.data = "admin:covers"
        
        with patch("routers.admin_covers._is_admin_uid", return_value=True):
            with patch("routers.admin_covers._db_lang_or_fallback", return_value="zh"):
                with patch("routers.admin_covers.list_covers", return_value=[]):
                    with patch("routers.admin_covers._tt", return_value="封面管理"):
                        with patch("routers.admin_covers.admin_covers_kb", return_value=Mock()):
                            from routers.admin_covers import admin_covers_entry
                            await admin_covers_entry(mock_callback_query, mock_state)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                            assert mock_callback_query.answer.called
    
    async def test_admin_covers_entry_not_admin(self, mock_callback_query, mock_state):
        """测试非管理员访问"""
        mock_callback_query.data = "admin:covers"
        
        with patch("routers.admin_covers._is_admin_uid", return_value=False):
            with patch("routers.admin_covers._tt", return_value="无权限"):
                from routers.admin_covers import admin_covers_entry
                await admin_covers_entry(mock_callback_query, mock_state)
                
                # 应该调用 answer 显示提示
                assert mock_callback_query.answer.called


class TestCoversAddAsk:
    """测试 covers_add_ask 处理函数"""
    
    async def test_covers_add_ask_success(self, mock_callback_query, mock_state):
        """测试添加封面提示成功"""
        mock_callback_query.data = "admin:covers:add"
        mock_callback_query.message.edit_text = AsyncMock()
        
        with patch("routers.admin_covers._is_admin_uid", return_value=True):
            with patch("routers.admin_covers._db_lang_or_fallback", return_value="zh"):
                with patch("routers.admin_covers._tt", return_value="请转发消息"):
                    with patch("routers.admin_covers._kb", return_value=Mock()):
                        with patch("routers.admin_covers._btn", return_value=Mock()):
                            from routers.admin_covers import covers_add_ask
                            await covers_add_ask(mock_callback_query, mock_state)
                            
                            # 验证调用了 edit_text
                            assert mock_callback_query.message.edit_text.called
                            # 验证状态被设置
                            assert mock_state.set_state.called


class TestCoversListPaged:
    """测试 covers_list_paged 处理函数"""
    
    async def test_covers_list_paged_success(self, mock_callback_query):
        """测试分页列表成功"""
        mock_callback_query.data = "admin:covers:list:1"
        mock_callback_query.message.edit_text = AsyncMock()
        mock_callback_query.message.edit_reply_markup = AsyncMock(side_effect=TelegramBadRequest(method="editReplyMarkup", message="Bad request"))
        
        with patch("routers.admin_covers._is_admin_uid", return_value=True):
            with patch("routers.admin_covers._db_lang_or_fallback", return_value="zh"):
                with patch("routers.admin_covers.list_covers", return_value=([], 0)):
                    with patch("routers.admin_covers._list_kb", return_value=Mock()):
                        with patch("routers.admin_covers._tt", return_value="封面列表"):
                            from routers.admin_covers import covers_list_paged
                            await covers_list_paged(mock_callback_query)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                            assert mock_callback_query.answer.called


class TestCoversDeleteOne:
    """测试 covers_delete_one 处理函数"""
    
    async def test_covers_delete_one_success(self, mock_callback_query):
        """测试删除封面成功"""
        mock_callback_query.data = "admin:covers:del:1"
        mock_callback_query.message.edit_reply_markup = AsyncMock()
        
        with patch("routers.admin_covers._is_admin_uid", return_value=True):
            with patch("routers.admin_covers._db_lang_or_fallback", return_value="zh"):
                with patch("routers.admin_covers.get_cover_by_id", return_value=Mock()):
                    with patch("routers.admin_covers.delete_cover", return_value=True):
                        with patch("routers.admin_covers.list_covers", return_value=([], 0)):
                            with patch("routers.admin_covers._list_kb", return_value=Mock()):
                                with patch("routers.admin_covers._tt", return_value="已删除"):
                                    from routers.admin_covers import covers_delete_one
                                    await covers_delete_one(mock_callback_query)
                                    
                                    # 验证调用了 answer
                                    assert mock_callback_query.answer.called


class TestCoversToggleOne:
    """测试 covers_toggle_one 处理函数"""
    
    async def test_covers_toggle_one_success(self, mock_callback_query):
        """测试切换封面状态成功"""
        mock_callback_query.data = "admin:covers:toggle:1"
        mock_callback_query.message.edit_reply_markup = AsyncMock()
        
        mock_cover = Mock()
        mock_cover.enabled = True
        
        with patch("routers.admin_covers._is_admin_uid", return_value=True):
            with patch("routers.admin_covers._db_lang_or_fallback", return_value="zh"):
                with patch("routers.admin_covers.get_cover_by_id", return_value=mock_cover):
                    with patch("routers.admin_covers.set_cover_enabled", return_value=True):
                        with patch("routers.admin_covers.list_covers", return_value=([], 0)):
                            with patch("routers.admin_covers._list_kb", return_value=Mock()):
                                with patch("routers.admin_covers._tt", return_value="已切换"):
                                    from routers.admin_covers import covers_toggle_one
                                    await covers_toggle_one(mock_callback_query)
                                    
                                    # 验证调用了 answer
                                    assert mock_callback_query.answer.called


class TestCoversViewOne:
    """测试 covers_view_one 处理函数"""
    
    async def test_covers_view_one_success(self, mock_callback_query):
        """测试查看封面成功"""
        mock_callback_query.data = "admin:covers:view:1"
        mock_callback_query.message.edit_reply_markup = AsyncMock(
            side_effect=TelegramBadRequest(method="editReplyMarkup", message="Bad request")
        )
        
        mock_cover = Mock()
        mock_cover.file_id = "test_file_id"
        mock_cover.media_type = "photo"
        mock_cover.channel_id = -1001234567890
        mock_cover.message_id = 100
        
        mock_bot = Mock()
        mock_bot.copy_message = AsyncMock(side_effect=Exception("test"))
        mock_bot.send_photo = AsyncMock()
        mock_callback_query.message.bot = mock_bot
        
        with patch("routers.admin_covers._is_admin_uid", return_value=True):
            with patch("routers.admin_covers._db_lang_or_fallback", return_value="zh"):
                with patch("routers.admin_covers.get_cover_by_id", return_value=mock_cover):
                    with patch("routers.admin_covers.list_covers", return_value=([], 0)):
                        with patch("routers.admin_covers._list_kb", return_value=Mock()):
                            with patch("routers.admin_covers._tt", return_value="封面详情"):
                                from routers.admin_covers import covers_view_one
                                await covers_view_one(mock_callback_query)
                                
                                # 验证调用了 send_photo 或 copy_message
                                assert mock_bot.send_photo.called or mock_bot.copy_message.called
                                # 验证在异常时调用了 answer
                                assert mock_callback_query.answer.called


class TestAdminCoversHelpers:
    """测试辅助函数"""
    
    def test_canon_lang(self):
        """测试 _canon_lang"""
        from routers.admin_covers import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("zh-CN") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("en-US") == "en"
        assert _canon_lang("fr") == "zh"  # 默认
        assert _canon_lang(None) == "zh"
        assert _canon_lang("") == "zh"
    
    def test_is_admin_uid(self):
        """测试 _is_admin_uid"""
        from routers.admin_covers import _is_admin_uid
        
        with patch("routers.admin_covers._is_admin", return_value=True):
            assert _is_admin_uid(99999) is True
        
        with patch("routers.admin_covers._is_admin", return_value=False):
            assert _is_admin_uid(12345) is False
        
        with patch("routers.admin_covers._is_admin", side_effect=Exception("test")):
            assert _is_admin_uid(12345) is False

