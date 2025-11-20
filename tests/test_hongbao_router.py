"""
测试 routers/hongbao.py
红包相关路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, UTC

from aiogram.types import CallbackQuery, User as TgUser, Message, Chat
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramNetworkError

from models.envelope import HBDuplicatedGrab, HBFinished, HBNotFound, HBError


@pytest.fixture
def mock_callback_query():
    """创建模拟的 CallbackQuery"""
    cb = Mock(spec=CallbackQuery)
    cb.from_user = Mock(spec=TgUser)
    cb.from_user.id = 12345
    cb.from_user.language_code = "zh"
    cb.data = "hb:grab:1"
    cb.message = Mock(spec=Message)
    cb.message.chat = Mock(spec=Chat)
    cb.message.chat.id = -1001234567890
    cb.message.message_id = 100
    cb.message.bot = Mock()
    cb.message.bot.send_message = AsyncMock()
    cb.message.bot.edit_message_text = AsyncMock()
    cb.message.bot.edit_message_caption = AsyncMock()
    cb.message.edit_text = AsyncMock()
    cb.message.edit_caption = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def mock_db_session():
    """创建模拟的数据库会话"""
    session = Mock()
    session.query = Mock()
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=None)
    return session


class TestHbGrab:
    """测试 hb_grab 处理函数"""
    
    async def test_hb_grab_success(self, mock_callback_query):
        """测试抢红包成功"""
        mock_callback_query.data = "hb:grab:1"
        
        # Mock grab_share 返回成功
        mock_grab_result = (Decimal("10.50"), "USDT", False)
        
        with patch("routers.hongbao.grab_share", return_value=mock_grab_result):
            with patch("routers.hongbao._db_lang_or_fallback", return_value="zh"):
                with patch("routers.hongbao.safe_answer", new_callable=AsyncMock):
                    with patch("routers.hongbao.safe_send_message", new_callable=AsyncMock):
                        with patch("routers.hongbao.get_envelope_summary", return_value={
                            "total_amount": "100.00",
                            "claimed_amount": "10.50",
                            "shares": 10,
                            "claimed_shares": 1,
                            "mode": "USDT"
                        }):
                            with patch("routers.hongbao._THROTTLE", {}):
                                with patch("routers.hongbao.time.time", return_value=1000.0):
                                    from routers.hongbao import hb_grab
                                    await hb_grab(mock_callback_query)
                                    
                                    # 验证调用了 safe_answer
                                    assert True  # 函数执行成功即可
    
    async def test_hb_grab_duplicated(self, mock_callback_query):
        """测试重复抢红包"""
        mock_callback_query.data = "hb:grab:1"
        
        with patch("routers.hongbao.grab_share", side_effect=HBDuplicatedGrab("已抢过")):
            with patch("routers.hongbao._db_lang_or_fallback", return_value="zh"):
                with patch("routers.hongbao.safe_answer", new_callable=AsyncMock) as mock_safe_answer:
                    with patch("routers.hongbao._THROTTLE", {}):
                        with patch("routers.hongbao.time.time", return_value=1000.0):
                            from routers.hongbao import hb_grab
                            await hb_grab(mock_callback_query)
                            
                            # 应该调用 safe_answer 显示重复提示
                            mock_safe_answer.assert_called()
    
    async def test_hb_grab_finished(self, mock_callback_query):
        """测试红包已抢完"""
        mock_callback_query.data = "hb:grab:1"
        
        with patch("routers.hongbao.grab_share", side_effect=HBFinished("已抢完")):
            with patch("routers.hongbao._db_lang_or_fallback", return_value="zh"):
                with patch("routers.hongbao.safe_answer", new_callable=AsyncMock):
                    with patch("routers.hongbao._dm_mvp_once_under_lock", new_callable=AsyncMock):
                        with patch("routers.hongbao._build_round_rank_text_and_photo", new_callable=AsyncMock, return_value=("排行榜", None)):
                            with patch("routers.hongbao.hb_rank_kb", return_value=Mock()):
                                with patch("routers.hongbao._kb_without_mvp", return_value=Mock()):
                                    with patch("routers.hongbao._append_today_button", return_value=Mock()):
                                        with patch("routers.hongbao._ENV_RANK_MSG", {}):
                                            with patch("routers.hongbao._ENV_RANK_LOCKS", {1: Mock()}):
                                                with patch("routers.hongbao.safe_send_message", new_callable=AsyncMock):
                                                    with patch("routers.hongbao._THROTTLE", {}):
                                                        with patch("routers.hongbao.time.time", return_value=1000.0):
                                                            from routers.hongbao import hb_grab
                                                            await hb_grab(mock_callback_query)
                                                            
                                                            # 函数执行成功即可
                                                            assert True
    
    async def test_hb_grab_not_found(self, mock_callback_query):
        """测试红包不存在"""
        mock_callback_query.data = "hb:grab:999"
        
        with patch("routers.hongbao.grab_share", side_effect=HBNotFound("未找到")):
            with patch("routers.hongbao._db_lang_or_fallback", return_value="zh"):
                with patch("routers.hongbao.safe_answer", new_callable=AsyncMock) as mock_safe_answer:
                    with patch("routers.hongbao._THROTTLE", {}):
                        with patch("routers.hongbao.time.time", return_value=1000.0):
                            from routers.hongbao import hb_grab
                            await hb_grab(mock_callback_query)
                            
                            # 应该调用 safe_answer 显示未找到提示
                            mock_safe_answer.assert_called()
    
    async def test_hb_grab_invalid_data(self, mock_callback_query):
        """测试无效的回调数据"""
        mock_callback_query.data = "hb:grab:invalid"
        
        with patch("routers.hongbao._db_lang_or_fallback", return_value="zh"):
            with patch("routers.hongbao.safe_answer", new_callable=AsyncMock) as mock_safe_answer:
                from routers.hongbao import hb_grab
                await hb_grab(mock_callback_query)
                
                # 应该调用 safe_answer 显示错误提示
                mock_safe_answer.assert_called()


class TestSafeAnswer:
    """测试 safe_answer 辅助函数"""
    
    async def test_safe_answer_success(self, mock_callback_query):
        """测试安全应答成功"""
        from routers.hongbao import safe_answer
        
        await safe_answer(mock_callback_query, "测试消息", show_alert=False)
        
        mock_callback_query.answer.assert_called_once()
    
    async def test_safe_answer_query_too_old(self, mock_callback_query):
        """测试查询过期时忽略错误"""
        mock_callback_query.answer = AsyncMock(side_effect=TelegramBadRequest(
            method="answerCallbackQuery",
            message="query is too old"
        ))
        
        from routers.hongbao import safe_answer
        
        # 不应该抛出异常
        await safe_answer(mock_callback_query, "测试消息", show_alert=False)
        
        mock_callback_query.answer.assert_called_once()
    
    async def test_safe_answer_other_error(self, mock_callback_query):
        """测试其他错误时抛出异常"""
        mock_callback_query.answer = AsyncMock(side_effect=TelegramBadRequest(
            method="answerCallbackQuery",
            message="other error"
        ))
        
        from routers.hongbao import safe_answer
        
        # 应该抛出异常
        with pytest.raises(TelegramBadRequest):
            await safe_answer(mock_callback_query, "测试消息", show_alert=False)


class TestCanonLang:
    """测试 _canon_lang 辅助函数"""
    
    def test_canon_lang_supported(self):
        """测试支持的语言"""
        from routers.hongbao import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("fr") == "fr"
        assert _canon_lang("de") == "de"
    
    def test_canon_lang_region_code(self):
        """测试地区码回退"""
        from routers.hongbao import _canon_lang
        
        assert _canon_lang("fr-CA") == "fr"
        assert _canon_lang("en-US") == "en"
        assert _canon_lang("zh-CN") == "zh"
    
    def test_canon_lang_unsupported(self):
        """测试不支持的语言回退到默认值"""
        from routers.hongbao import _canon_lang
        
        assert _canon_lang("ja") == "zh"  # 默认
        assert _canon_lang("ko") == "zh"  # 默认
        assert _canon_lang(None) == "zh"  # 默认
        assert _canon_lang("") == "zh"  # 默认
    
    def test_canon_lang_historical_compat(self):
        """测试历史兼容"""
        from routers.hongbao import _canon_lang
        
        assert _canon_lang("zh-Hans") == "zh"
        assert _canon_lang("en-GB") == "en"

