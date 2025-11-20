"""
测试 routers/today.py
今日战绩路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, UTC
from zoneinfo import ZoneInfo

from aiogram.types import CallbackQuery, User as TgUser, Message, Chat
from aiogram.exceptions import TelegramBadRequest


@pytest.fixture
def mock_callback_query():
    """创建模拟的 CallbackQuery"""
    cb = Mock(spec=CallbackQuery)
    cb.from_user = Mock(spec=TgUser)
    cb.from_user.id = 12345
    cb.from_user.language_code = "zh"
    cb.data = "today:main"
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
    msg.from_user.language_code = "zh"
    msg.chat = Mock(spec=Chat)
    msg.chat.id = 12345
    msg.text = "/today"
    msg.answer = AsyncMock()
    return msg


class TestTodayMe:
    """测试 today_me 处理函数"""
    
    async def test_today_me_success(self, mock_callback_query):
        """测试今日战绩成功"""
        mock_callback_query.data = "today:main"
        
        tz = ZoneInfo("Asia/Manila")
        with patch("routers.today._db_lang", return_value="zh"):
            with patch("routers.today._today_range_for_user", return_value=(datetime.now(UTC), datetime.now(UTC), tz)):
                with patch("routers.today.get_session") as mock_session:
                    mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.filter.return_value.all.return_value = []
                    with patch("routers.today.t", return_value="今日战绩"):
                        with patch("routers.today.back_home_kb", return_value=Mock()):
                            from routers.today import today_me
                            await today_me(mock_callback_query)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                            assert mock_callback_query.answer.called
    
    async def test_today_me_telegram_bad_request(self, mock_callback_query):
        """测试 TelegramBadRequest 时使用 answer"""
        mock_callback_query.data = "today:main"
        mock_callback_query.message.edit_text = AsyncMock(
            side_effect=TelegramBadRequest(method="editMessageText", message="Bad request")
        )
        
        tz = ZoneInfo("Asia/Manila")
        with patch("routers.today._db_lang", return_value="zh"):
            with patch("routers.today._today_range_for_user", return_value=(datetime.now(UTC), datetime.now(UTC), tz)):
                with patch("routers.today.get_session") as mock_session:
                    mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.filter.return_value.all.return_value = []
                    with patch("routers.today.t", return_value="今日战绩"):
                        with patch("routers.today.back_home_kb", return_value=Mock()):
                            from routers.today import today_me
                            await today_me(mock_callback_query)
                            
                            # 应该调用 answer 而不是 edit_text
                            assert mock_callback_query.message.answer.called
                            assert mock_callback_query.answer.called


class TestTodayCmd:
    """测试 today_cmd 处理函数"""
    
    async def test_today_cmd_success(self, mock_message):
        """测试 /today 命令成功"""
        mock_message.text = "/today"
        
        tz = ZoneInfo("Asia/Manila")
        with patch("routers.today._db_lang", return_value="zh"):
            with patch("routers.today._today_range_for_user", return_value=(datetime.now(UTC), datetime.now(UTC), tz)):
                with patch("routers.today.get_session") as mock_session:
                    mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.filter.return_value.all.return_value = []
                    with patch("routers.today.t", return_value="今日战绩"):
                        with patch("routers.today.back_home_kb", return_value=Mock()):
                            from routers.today import today_cmd
                            await today_cmd(mock_message)
                            
                            # 验证调用了 answer
                            assert mock_message.answer.called


class TestTodayHelpers:
    """测试辅助函数"""
    
    def test_canon_lang(self):
        """测试 _canon_lang"""
        from routers.today import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("zh-CN") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("en-US") == "en"
        assert _canon_lang("fr") == "zh"  # 默认
        assert _canon_lang(None) == "zh"
        assert _canon_lang("") == "zh"
    
    def test_grab_types(self):
        """测试 _grab_types"""
        from routers.today import _grab_types
        
        types = _grab_types()
        assert isinstance(types, list)
        assert len(types) > 0
    
    def test_amount_attr(self):
        """测试 _amount_attr"""
        from routers.today import _amount_attr
        
        attr = _amount_attr()
        assert attr in ("amount", "value")
