"""
测试 routers/welfare.py
福利相关路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, UTC

from aiogram.types import CallbackQuery, User as TgUser, Message, Chat
from aiogram.exceptions import TelegramBadRequest

from models.user import User
from models.ledger import Ledger, LedgerType


@pytest.fixture
def mock_callback_query():
    """创建模拟的 CallbackQuery"""
    cb = Mock(spec=CallbackQuery)
    cb.from_user = Mock(spec=TgUser)
    cb.from_user.id = 12345
    cb.from_user.language_code = "zh"
    cb.data = "wf:main"
    cb.message = Mock(spec=Message)
    cb.message.chat = Mock(spec=Chat)
    cb.message.chat.id = 12345
    cb.message.message_id = 100
    cb.message.edit_text = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def mock_db_session():
    """创建模拟的数据库会话"""
    session = Mock()
    session.query = Mock()
    session.commit = Mock()
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=None)
    return session


class TestWfMain:
    """测试 wf_main 处理函数"""
    
    async def test_wf_main_success(self, mock_callback_query):
        """测试福利主页面成功"""
        mock_callback_query.data = "wf:main"
        
        with patch("routers.welfare._user_lang", return_value="zh"):
            with patch("routers.welfare.t", return_value="福利中心"):
                with patch("routers.welfare.welfare_menu", return_value=Mock()):
                    from routers.welfare import wf_main
                    await wf_main(mock_callback_query)
                    
                    # 验证调用了 edit_text 或 answer
                    assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called
    
    async def test_wf_main_telegram_bad_request(self, mock_callback_query):
        """测试 TelegramBadRequest 时使用 answer"""
        mock_callback_query.data = "wf:main"
        mock_callback_query.message.edit_text = AsyncMock(
            side_effect=TelegramBadRequest(method="editMessageText", message="Bad request")
        )
        
        with patch("routers.welfare._user_lang", return_value="zh"):
            with patch("routers.welfare.t", return_value="福利中心"):
                with patch("routers.welfare.welfare_menu", return_value=Mock()):
                    from routers.welfare import wf_main
                    await wf_main(mock_callback_query)
                    
                    # 应该调用 answer 而不是 edit_text
                    assert mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called


class TestWfSignin:
    """测试 wf_signin 处理函数"""
    
    async def test_wf_signin_success(self, mock_callback_query, mock_db_session):
        """测试签到成功"""
        mock_callback_query.data = "wf:signin"
        
        # Mock 用户和数据库
        mock_user = Mock(spec=User)
        mock_user.tg_id = 12345
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=None)  # 今天未签到
        mock_db_session.query.return_value = mock_query
        
        with patch("routers.welfare.get_session", return_value=mock_db_session):
            with patch("routers.welfare._user_lang", return_value="zh"):
                with patch("routers.welfare.flags") as mock_flags:
                    mock_flags.get = Mock(side_effect=lambda key, default: {
                        "ENABLE_SIGNIN": True,
                        "SIGNIN_REWARD_POINTS": 100
                    }.get(key, default))
                    with patch("routers.welfare._has_signed_today", return_value=False):
                        with patch("routers.welfare.get_or_create_user", return_value=mock_user):
                            with patch("routers.welfare.update_balance"):
                                with patch("routers.welfare.add_ledger_entry"):
                                    with patch("routers.welfare.t", return_value="签到成功"):
                                        with patch("routers.welfare.welfare_menu", return_value=Mock()):
                                            from routers.welfare import wf_signin
                                            await wf_signin(mock_callback_query)
                                            
                                            # 验证调用了 edit_text 或 answer
                                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                                            assert mock_callback_query.answer.called
    
    async def test_wf_signin_already_signed(self, mock_callback_query):
        """测试已签到"""
        mock_callback_query.data = "wf:signin"
        
        with patch("routers.welfare._user_lang", return_value="zh"):
            with patch("routers.welfare.flags") as mock_flags:
                mock_flags.get = Mock(return_value=True)
                with patch("routers.welfare._has_signed_today", return_value=True):
                    with patch("routers.welfare.t", return_value="已签到"):
                        from routers.welfare import wf_signin
                        await wf_signin(mock_callback_query)
                        
                        # 应该只调用 answer 显示提示
                        assert mock_callback_query.answer.called
    
    async def test_wf_signin_feature_disabled(self, mock_callback_query):
        """测试功能未启用"""
        mock_callback_query.data = "wf:signin"
        
        with patch("routers.welfare._user_lang", return_value="zh"):
            with patch("routers.welfare.flags") as mock_flags:
                mock_flags.get = Mock(side_effect=lambda key, default: {
                    "ENABLE_SIGNIN": False
                }.get(key, default))
                with patch("routers.welfare.t", return_value="功能未启用"):
                    from routers.welfare import wf_signin
                    await wf_signin(mock_callback_query)
                    
                    # 应该调用 answer 显示提示
                    assert mock_callback_query.answer.called


class TestWfPromo:
    """测试 wf_promo 处理函数"""
    
    async def test_wf_promo_success(self, mock_callback_query):
        """测试公告页面成功"""
        mock_callback_query.data = "wf:promo"
        
        with patch("routers.welfare._user_lang", return_value="zh"):
            with patch("routers.welfare.t", return_value="公告"):
                with patch("routers.welfare.back_home_kb", return_value=Mock()):
                    from routers.welfare import wf_promo
                    await wf_promo(mock_callback_query)
                    
                    # 验证调用了 edit_text 或 answer
                    assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called


class TestWfRules:
    """测试 wf_rules 处理函数"""
    
    async def test_wf_rules_success(self, mock_callback_query):
        """测试规则页面成功"""
        mock_callback_query.data = "wf:rules"
        
        with patch("routers.welfare._user_lang", return_value="zh"):
            with patch("routers.welfare.t", return_value="规则"):
                with patch("routers.welfare.back_home_kb", return_value=Mock()):
                    from routers.welfare import wf_rules
                    await wf_rules(mock_callback_query)
                    
                    # 验证调用了 edit_text 或 answer
                    assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called


class TestWfInviteForward:
    """测试邀请转发处理函数"""
    
    async def test_wf_invite_forward_success(self, mock_callback_query):
        """测试邀请转发成功"""
        mock_callback_query.data = "wf:invite"
        
        mock_invite_main = AsyncMock()
        
        with patch("routers.welfare._user_lang", return_value="zh"):
            with patch("routers.welfare._get_invite_handlers", return_value=(mock_invite_main, None, None)):
                from routers.welfare import wf_invite_forward
                await wf_invite_forward(mock_callback_query)
                
                # 验证调用了 invite_main
                mock_invite_main.assert_called_once_with(mock_callback_query)
    
    async def test_wf_invite_forward_not_available(self, mock_callback_query):
        """测试邀请功能不可用"""
        mock_callback_query.data = "wf:invite"
        
        with patch("routers.welfare._user_lang", return_value="zh"):
            with patch("routers.welfare._get_invite_handlers", return_value=(None, None, None)):
                with patch("routers.welfare.t", return_value="不可用"):
                    from routers.welfare import wf_invite_forward
                    await wf_invite_forward(mock_callback_query)
                    
                    # 应该调用 answer 显示提示
                    assert mock_callback_query.answer.called


class TestWelfareHelpers:
    """测试辅助函数"""
    
    def test_canon_lang(self):
        """测试 _canon_lang"""
        from routers.welfare import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("zh-CN") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("en-US") == "en"
        assert _canon_lang("fr") == "zh"  # 默认
        assert _canon_lang(None) == "zh"
        assert _canon_lang("") == "zh"
    
    def test_has_signed_today_false(self, mock_db_session):
        """测试今天未签到"""
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=None)
        mock_db_session.query.return_value = mock_query
        
        with patch("routers.welfare.get_session", return_value=mock_db_session):
            from routers.welfare import _has_signed_today
            result = _has_signed_today(12345)
            assert result is False
    
    def test_has_signed_today_true(self, mock_db_session):
        """测试今天已签到"""
        from datetime import date
        
        mock_ledger = Mock(spec=Ledger)
        mock_ledger.created_at = datetime.now(UTC)
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=mock_ledger)
        mock_db_session.query.return_value = mock_query
        
        with patch("routers.welfare.get_session", return_value=mock_db_session):
            from routers.welfare import _has_signed_today
            result = _has_signed_today(12345)
            assert result is True

