"""
测试 routers/rank.py
排行榜路由测试
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
    cb.data = "rank:round:1"
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
    msg.text = "/start rank_1"
    msg.answer = AsyncMock()
    return msg


class TestRankRound:
    """测试 rank_round 处理函数"""
    
    async def test_rank_round_success(self, mock_callback_query):
        """测试排行榜成功"""
        mock_callback_query.data = "rank:round:1"
        
        with patch("routers.rank._db_lang_or_fallback", return_value="zh"):
            with patch("routers.rank.list_envelope_claims", return_value=[]):
                with patch("routers.rank.get_lucky_winner", return_value=None):
                    with patch("routers.rank.get_envelope_summary", return_value=Mock()):
                        with patch("routers.rank.t", return_value="排行榜"):
                            with patch("routers.rank.hb_rank_kb", return_value=Mock()):
                                from routers.rank import rank_round
                                await rank_round(mock_callback_query)
                                
                                # 验证调用了 edit_text 或 answer
                                assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                                assert mock_callback_query.answer.called
    
    async def test_rank_round_not_found(self, mock_callback_query):
        """测试红包不存在"""
        mock_callback_query.data = "rank:round:999"
        
        from routers.rank import HBNotFound
        
        with patch("routers.rank._db_lang_or_fallback", return_value="zh"):
            with patch("routers.rank.list_envelope_claims", side_effect=HBNotFound()):
                with patch("routers.rank.t", return_value="未找到"):
                    with patch("routers.rank.hb_rank_kb", return_value=Mock()):
                        from routers.rank import rank_round
                        await rank_round(mock_callback_query)
                        
                        # 函数执行成功即可
                        assert True


class TestDeeplinkRank:
    """测试 deeplink_rank 处理函数"""
    
    async def test_deeplink_rank_success(self, mock_message):
        """测试深链排行榜成功"""
        mock_message.text = "/start rank_1"
        
        with patch("routers.rank._db_lang_or_fallback", return_value="zh"):
            with patch("routers.rank.list_envelope_claims", return_value=[]):
                with patch("routers.rank.get_lucky_winner", return_value=None):
                    with patch("routers.rank.get_envelope_summary", return_value=Mock()):
                        with patch("routers.rank.t", return_value="排行榜"):
                            with patch("routers.rank.hb_rank_kb", return_value=Mock()):
                                from routers.rank import deeplink_rank
                                await deeplink_rank(mock_message)
                                
                                # 验证调用了 answer
                                assert mock_message.answer.called


class TestRankMain:
    """测试 rank_main 处理函数"""
    
    async def test_rank_main_success(self, mock_callback_query):
        """测试排行榜主页面成功"""
        mock_callback_query.data = "rank:main"
        
        # 创建模拟的键盘对象，包含 inline_keyboard 属性
        mock_kb = Mock()
        mock_kb.inline_keyboard = []
        
        with patch("routers.rank._db_lang_or_fallback", return_value="zh"):
            with patch("routers.rank._t_first", return_value="排行榜已下线"):
                with patch("routers.rank.flags") as mock_flags:
                    mock_flags.get = Mock(return_value=False)
                    with patch("routers.rank.back_home_kb", return_value=mock_kb):
                        from routers.rank import rank_main
                        await rank_main(mock_callback_query)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        assert mock_callback_query.answer.called


class TestRankHelpers:
    """测试辅助函数"""
    
    def test_canon_lang(self):
        """测试 _canon_lang"""
        from routers.rank import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("zh-CN") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("en-US") == "en"
        assert _canon_lang("fr") == "zh"  # 默认
        assert _canon_lang(None) == "zh"
        assert _canon_lang("") == "zh"
    
    def test_fmt_amount(self):
        """测试 _fmt_amount"""
        from routers.rank import _fmt_amount
        
        assert _fmt_amount("USDT", 100.123) == "100.12"
        assert _fmt_amount("TON", 50.456) == "50.46"
        assert _fmt_amount("POINT", 100.7) == "101"
        assert _fmt_amount("POINT", 100.2) == "100"
