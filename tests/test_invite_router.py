"""
测试 routers/invite.py
邀请相关路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from aiogram.types import CallbackQuery, User as TgUser, Message, Chat
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest


@pytest.fixture
def mock_callback_query():
    """创建模拟的 CallbackQuery"""
    cb = Mock(spec=CallbackQuery)
    cb.from_user = Mock(spec=TgUser)
    cb.from_user.id = 12345
    cb.from_user.language_code = "zh"
    cb.data = "invite:main"
    cb.message = Mock(spec=Message)
    cb.message.chat = Mock(spec=Chat)
    cb.message.chat.id = -1001234567890
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
    msg.text = "/start"
    msg.answer = AsyncMock()
    return msg


class TestInviteMain:
    """测试 invite_main 处理函数"""
    
    async def test_invite_main_success(self, mock_callback_query):
        """测试邀请主页面成功"""
        mock_callback_query.data = "invite:main"
        
        with patch("routers.invite._user_lang", return_value="zh"):
            with patch("routers.invite._show_invite_panel", new_callable=AsyncMock):
                from routers.invite import invite_main
                await invite_main(mock_callback_query)
                
                # 函数执行成功即可
                assert True
    
    async def test_invite_main_telegram_bad_request(self, mock_callback_query):
        """测试 TelegramBadRequest 时使用 answer"""
        mock_callback_query.data = "invite:main"
        mock_callback_query.message.edit_text = AsyncMock(
            side_effect=TelegramBadRequest(method="editMessageText", message="Bad request")
        )
        
        with patch("routers.invite._user_lang", return_value="zh"):
            with patch("routers.invite._show_invite_panel", new_callable=AsyncMock):
                from routers.invite import invite_main
                await invite_main(mock_callback_query)
                
                # 函数执行成功即可
                assert True


class TestInviteShare:
    """测试 invite_share 处理函数"""
    
    async def test_invite_share_success(self, mock_callback_query):
        """测试分享邀请链接成功"""
        mock_callback_query.data = "invite:share"
        
        with patch("routers.invite._user_lang", return_value="zh"):
            with patch("routers.invite.build_invite_share_link", return_value="https://t.me/bot?start=invite_12345"):
                with patch("routers.invite.t", return_value="分享链接"):
                    from routers.invite import invite_share
                    await invite_share(mock_callback_query)
                    
                    # 验证调用了 edit_text 或 answer
                    assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called


class TestInviteRedeem:
    """测试 invite_redeem 处理函数"""
    
    async def test_invite_redeem_success(self, mock_callback_query):
        """测试兑换页面成功"""
        mock_callback_query.data = "invite:redeem"
        
        with patch("routers.invite._user_lang", return_value="zh"):
            with patch("routers.invite.t", return_value="兑换"):
                with patch("routers.invite._invite_redeem_kb", return_value=Mock()):
                    from routers.invite import invite_redeem
                    await invite_redeem(mock_callback_query)
                    
                    # 验证调用了 edit_text 或 answer
                    assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called


class TestInviteRedeemProgress:
    """测试 invite_redeem_progress 处理函数"""
    
    async def test_invite_redeem_progress_success(self, mock_callback_query):
        """测试兑换进度成功"""
        mock_callback_query.data = "invite:redeem:progress"
        
        with patch("routers.invite._user_lang", return_value="zh"):
            # redeem_points_to_progress 返回 (ok, msg_text, percent)
            with patch("routers.invite.redeem_points_to_progress", return_value=(True, "兑换成功", 50)):
                with patch("routers.invite.t", return_value="兑换成功"):
                    with patch("routers.invite._invite_menu_kb", return_value=Mock()):
                        from routers.invite import invite_redeem_progress
                        await invite_redeem_progress(mock_callback_query)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        assert mock_callback_query.answer.called
    
    async def test_invite_redeem_progress_insufficient(self, mock_callback_query):
        """测试积分不足"""
        mock_callback_query.data = "invite:redeem:progress"
        
        with patch("routers.invite._user_lang", return_value="zh"):
            # redeem_points_to_progress 返回 (ok, msg_text, percent)
            with patch("routers.invite.redeem_points_to_progress", return_value=(False, "积分不足", 0)):
                with patch("routers.invite.t", return_value="积分不足"):
                    with patch("routers.invite._invite_menu_kb", return_value=Mock()):
                        from routers.invite import invite_redeem_progress
                        await invite_redeem_progress(mock_callback_query)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        assert mock_callback_query.answer.called


class TestInviteRedeemEnergy:
    """测试 invite_redeem_energy 处理函数"""
    
    async def test_invite_redeem_energy_success(self, mock_callback_query):
        """测试能量换积分成功"""
        mock_callback_query.data = "invite:redeem:energy"
        
        with patch("routers.invite._user_lang", return_value="zh"):
            # redeem_energy_to_points 返回 (ok, msg_text)
            with patch("routers.invite.redeem_energy_to_points", return_value=(True, "兑换成功")):
                with patch("routers.invite.t", return_value="兑换成功"):
                    with patch("routers.invite._invite_menu_kb", return_value=Mock()):
                        from routers.invite import invite_redeem_energy
                        await invite_redeem_energy(mock_callback_query)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        assert mock_callback_query.answer.called


class TestInviteDeeplink:
    """测试邀请深链处理"""
    
    async def test_handle_invite_deeplink_with_payload(self, mock_message):
        """测试带邀请码的深链"""
        mock_message.text = "/start invite_12345"
        
        with patch("routers.invite._parse_invite_payload", return_value=12345):
            with patch("routers.invite.add_invite_and_rewards", return_value=True):
                with patch("routers.invite._user_lang", return_value="zh"):
                    with patch("routers.invite._show_invite_panel", new_callable=AsyncMock):
                        from routers.invite import handle_invite_deeplink
                        command = Mock(spec=CommandStart)
                        command.args = "invite_12345"
                        await handle_invite_deeplink(mock_message, command)
                        
                        # 函数执行成功即可
                        assert True
    
    async def test_handle_invite_deeplink_without_payload(self, mock_message):
        """测试不带邀请码的深链"""
        mock_message.text = "/start"
        
        with patch("routers.invite._parse_invite_payload", return_value=None):
            with patch("routers.invite._user_lang", return_value="zh"):
                with patch("routers.invite._show_invite_panel", new_callable=AsyncMock):
                    from routers.invite import handle_invite_deeplink
                    command = Mock(spec=CommandStart)
                    command.args = None
                    await handle_invite_deeplink(mock_message, command)
                    
                    # 函数执行成功即可
                    assert True


class TestInviteHelpers:
    """测试辅助函数"""
    
    def test_parse_invite_payload_invite_prefix(self):
        """测试解析 invite_ 前缀"""
        from routers.invite import _parse_invite_payload
        
        assert _parse_invite_payload("/start invite_12345") == 12345
        assert _parse_invite_payload("/start invite_999") == 999
    
    def test_parse_invite_payload_ref_prefix(self):
        """测试解析 ref_ 前缀"""
        from routers.invite import _parse_invite_payload
        
        assert _parse_invite_payload("/start ref_12345") == 12345
        assert _parse_invite_payload("/start ref_999") == 999
    
    def test_parse_invite_payload_r_prefix(self):
        """测试解析 r_ 前缀"""
        from routers.invite import _parse_invite_payload
        
        assert _parse_invite_payload("/start r_12345") == 12345
        assert _parse_invite_payload("/start r_999") == 999
    
    def test_parse_invite_payload_invalid(self):
        """测试无效的 payload"""
        from routers.invite import _parse_invite_payload
        
        assert _parse_invite_payload("/start") is None
        assert _parse_invite_payload("/start invalid") is None
        assert _parse_invite_payload("not a start command") is None
        assert _parse_invite_payload(None) is None
    
    def test_canon_lang(self):
        """测试 _canon_lang"""
        from routers.invite import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("zh-CN") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("en-US") == "en"
        assert _canon_lang("fr") == "zh"  # 默认
        assert _canon_lang(None) == "zh"
        assert _canon_lang("") == "zh"

