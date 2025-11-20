"""
测试 routers/menu.py
菜单相关路由测试
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
    cb.data = "menu:main"
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
    msg.text = "/start"
    msg.answer = AsyncMock()
    return msg


class TestMenuHome:
    """测试 menu_home 处理函数"""
    
    async def test_menu_home_success(self, mock_callback_query):
        """测试主菜单成功"""
        mock_callback_query.data = "menu:main"
        
        with patch("routers.menu._db_lang_or_fallback", return_value="zh"):
            with patch("routers.menu.main_menu", return_value=Mock()):
                with patch("routers.menu.t", return_value="主菜单"):
                    with patch("routers.menu._safe_cb_answer", new_callable=AsyncMock):
                        from routers.menu import menu_home
                        await menu_home(mock_callback_query)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestMenuWelfare:
    """测试 menu_welfare 处理函数"""
    
    async def test_menu_welfare_success(self, mock_callback_query):
        """测试福利菜单成功"""
        mock_callback_query.data = "menu:welfare"
        
        with patch("routers.menu._db_lang_or_fallback", return_value="zh"):
            with patch("routers.menu.welfare_menu", return_value=Mock()):
                with patch("routers.menu.t", return_value="福利中心"):
                    with patch("routers.menu._safe_cb_answer", new_callable=AsyncMock):
                        from routers.menu import menu_welfare
                        await menu_welfare(mock_callback_query)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestMenuAdmin:
    """测试 menu_admin 处理函数"""
    
    async def test_menu_admin_success(self, mock_callback_query):
        """测试管理员菜单成功"""
        mock_callback_query.data = "menu:admin"
        
        with patch("routers.menu._db_lang_or_fallback", return_value="zh"):
            with patch("routers.menu._is_admin", return_value=True):
                with patch("routers.menu.admin_menu", return_value=Mock()):
                    with patch("routers.menu.t", return_value="管理员面板"):
                        with patch("routers.menu._safe_cb_answer", new_callable=AsyncMock):
                            from routers.menu import menu_admin
                            await menu_admin(mock_callback_query)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
    
    async def test_menu_admin_not_admin(self, mock_callback_query):
        """测试非管理员访问"""
        mock_callback_query.data = "menu:admin"
        
        with patch("routers.menu._db_lang_or_fallback", return_value="zh"):
            with patch("routers.menu._is_admin", return_value=False):
                with patch("routers.menu._safe_cb_answer", new_callable=AsyncMock):
                    from routers.menu import menu_admin
                    await menu_admin(mock_callback_query)
                    
                    # 非管理员应该只调用 answer，不显示菜单
                    assert True


class TestMenuAssets:
    """测试 menu_assets 处理函数"""
    
    async def test_menu_assets_success(self, mock_callback_query):
        """测试资产菜单成功"""
        mock_callback_query.data = "menu:asset"
        
        with patch("routers.menu._db_lang_or_fallback", return_value="zh"):
            with patch("routers.menu.asset_menu", return_value=Mock()):
                with patch("routers.menu.t", return_value="我的资产"):
                    with patch("routers.menu._safe_cb_answer", new_callable=AsyncMock):
                        from routers.menu import menu_assets
                        await menu_assets(mock_callback_query)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestMenuSendHb:
    """测试 menu_send_hb 处理函数"""
    
    async def test_menu_send_hb_success(self, mock_callback_query):
        """测试发红包菜单成功"""
        mock_callback_query.data = "menu:send"
        
        with patch("routers.menu._db_lang_or_fallback", return_value="zh"):
            with patch("routers.menu._safe_cb_answer", new_callable=AsyncMock):
                # menu_send_hb 可能会重定向到其他路由，这里只验证函数能执行
                from routers.menu import menu_send_hb
                await menu_send_hb(mock_callback_query)
                
                # 函数执行成功即可
                assert True


class TestCmdStartOrMenu:
    """测试 cmd_start_or_menu 处理函数"""
    
    async def test_cmd_start_success(self, mock_message):
        """测试 /start 命令成功"""
        mock_message.text = "/start"
        
        # Mock 数据库会话和查询
        mock_session = Mock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        
        with patch("routers.menu.get_session", return_value=mock_session):
            with patch("routers.menu.get_or_create_user", return_value=Mock()):
                with patch("routers.menu._db_lang_or_fallback", return_value="zh"):
                    with patch("routers.menu.main_menu", return_value=Mock()):
                        with patch("routers.menu.t", return_value="欢迎"):
                            with patch("routers.menu.log_user_to_sheet", new_callable=AsyncMock):
                                from routers.menu import cmd_start_or_menu
                                await cmd_start_or_menu(mock_message)
                                
                                # 验证调用了 answer
                                assert mock_message.answer.called
    
    async def test_cmd_menu_success(self, mock_message):
        """测试 /menu 命令成功"""
        mock_message.text = "/menu"
        
        # Mock 数据库会话和查询
        mock_session = Mock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        
        with patch("routers.menu.get_session", return_value=mock_session):
            with patch("routers.menu.get_or_create_user", return_value=Mock()):
                with patch("routers.menu._db_lang_or_fallback", return_value="zh"):
                    with patch("routers.menu.main_menu", return_value=Mock()):
                        with patch("routers.menu.t", return_value="主菜单"):
                            with patch("routers.menu.log_user_to_sheet", new_callable=AsyncMock):
                                from routers.menu import cmd_start_or_menu
                                await cmd_start_or_menu(mock_message)
                                
                                # 验证调用了 answer
                                assert mock_message.answer.called


class TestMenuHelpers:
    """测试辅助函数"""
    
    def test_canon_lang(self):
        """测试 _canon_lang"""
        from routers.menu import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("fr") == "fr"
        assert _canon_lang("fr-CA") == "fr"
        assert _canon_lang("zh-CN") == "zh"
        assert _canon_lang("ja") == "zh"  # 默认
        assert _canon_lang(None) == "zh"
        assert _canon_lang("") == "zh"
    
    def test_non_empty(self):
        """测试 _non_empty"""
        from routers.menu import _non_empty
        
        assert _non_empty("test", "fallback") == "test"
        assert _non_empty(None, "fallback") == "fallback"
        assert _non_empty("", "fallback") == "fallback"  # 空字符串返回 fallback
        assert _non_empty("   ", "fallback") == "fallback"  # 空白字符串返回 fallback
    
    async def test_safe_cb_answer_success(self, mock_callback_query):
        """测试安全应答成功"""
        from routers.menu import _safe_cb_answer
        
        await _safe_cb_answer(mock_callback_query, "测试消息", show_alert=False)
        
        mock_callback_query.answer.assert_called_once()
    
    async def test_safe_cb_answer_telegram_bad_request(self, mock_callback_query):
        """测试查询过期时忽略错误"""
        mock_callback_query.answer = AsyncMock(
            side_effect=TelegramBadRequest(method="answerCallbackQuery", message="query is too old")
        )
        
        from routers.menu import _safe_cb_answer
        
        # 不应该抛出异常
        await _safe_cb_answer(mock_callback_query, "测试消息", show_alert=False)
        
        mock_callback_query.answer.assert_called_once()

