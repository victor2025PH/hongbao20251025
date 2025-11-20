"""
测试 routers/withdraw.py
提现相关路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal

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
    cb.data = "withdraw:main"
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
    msg.text = "100"
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


class TestWithdrawMain:
    """测试 withdraw_main 处理函数"""
    
    async def test_withdraw_main_success(self, mock_callback_query, mock_state):
        """测试提现主页面成功"""
        mock_callback_query.data = "withdraw:main"
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw.t", return_value="提现"):
                with patch("routers.withdraw._token_kb", return_value=Mock()):
                    from routers.withdraw import withdraw_main
                    await withdraw_main(mock_callback_query, mock_state)
                    
                    # 验证调用了 edit_text 或 answer
                    assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called
                    # 验证状态被设置
                    assert mock_state.clear.called
                    assert mock_state.set_state.called
    
    async def test_withdraw_main_telegram_bad_request(self, mock_callback_query, mock_state):
        """测试 TelegramBadRequest 时使用 answer"""
        mock_callback_query.data = "withdraw:main"
        mock_callback_query.message.edit_text = AsyncMock(
            side_effect=TelegramBadRequest(method="editMessageText", message="Bad request")
        )
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw.t", return_value="提现"):
                with patch("routers.withdraw._token_kb", return_value=Mock()):
                    from routers.withdraw import withdraw_main
                    await withdraw_main(mock_callback_query, mock_state)
                    
                    # 应该调用 answer 而不是 edit_text
                    assert mock_callback_query.message.answer.called
                    assert mock_callback_query.answer.called


class TestChooseToken:
    """测试 choose_token 处理函数"""
    
    async def test_choose_token_usdt(self, mock_callback_query, mock_state):
        """测试选择 USDT"""
        mock_callback_query.data = "withdraw:token:USDT"
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw._user_balances", return_value=(Decimal("1000"), Decimal("100"))):
                with patch("routers.withdraw.t", return_value="请输入金额"):
                    with patch("routers.withdraw._back_to_token_kb", return_value=Mock()):
                        from routers.withdraw import choose_token
                        await choose_token(mock_callback_query, mock_state)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        assert mock_callback_query.answer.called
                        # 验证状态被更新
                        assert mock_state.update_data.called
                        assert mock_state.set_state.called
    
    async def test_choose_token_ton(self, mock_callback_query, mock_state):
        """测试选择 TON"""
        mock_callback_query.data = "withdraw:token:TON"
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw._user_balances", return_value=(Decimal("1000"), Decimal("100"))):
                with patch("routers.withdraw.t", return_value="请输入金额"):
                    with patch("routers.withdraw._back_to_token_kb", return_value=Mock()):
                        from routers.withdraw import choose_token
                        await choose_token(mock_callback_query, mock_state)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestInputAmount:
    """测试 input_amount 处理函数"""
    
    async def test_input_amount_success(self, mock_message, mock_state):
        """测试输入金额成功"""
        mock_message.text = "100"
        mock_state.get_data = AsyncMock(return_value={"token": "USDT"})
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw._parse_amount", return_value=Decimal("100")):
                with patch("routers.withdraw._user_balances", return_value=(Decimal("1000"), Decimal("100"))):
                    with patch("routers.withdraw.t", return_value="请输入地址"):
                        with patch("routers.withdraw._back_to_token_kb", return_value=Mock()):
                            from routers.withdraw import input_amount
                            await input_amount(mock_message, mock_state)
                            
                            # 验证调用了 answer
                            assert mock_message.answer.called
                            # 验证状态被更新
                            assert mock_state.update_data.called
                            assert mock_state.set_state.called
    
    async def test_input_amount_invalid(self, mock_message, mock_state):
        """测试无效金额"""
        mock_message.text = "invalid"
        mock_state.get_data = AsyncMock(return_value={"token": "USDT"})
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw._parse_amount", return_value=None):
                with patch("routers.withdraw.t", return_value="金额无效"):
                    with patch("routers.withdraw._back_to_token_kb", return_value=Mock()):
                        from routers.withdraw import input_amount
                        await input_amount(mock_message, mock_state)
                        
                        # 验证调用了 answer 显示错误
                        assert mock_message.answer.called
    
    async def test_input_amount_insufficient(self, mock_message, mock_state):
        """测试余额不足"""
        mock_message.text = "1000"
        mock_state.get_data = AsyncMock(return_value={"token": "USDT"})
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw._parse_amount", return_value=Decimal("1000")):
                with patch("routers.withdraw._user_balances", return_value=(Decimal("100"), Decimal("100"))):
                    with patch("routers.withdraw.t", return_value="余额不足"):
                        with patch("routers.withdraw._back_to_token_kb", return_value=Mock()):
                            from routers.withdraw import input_amount
                            await input_amount(mock_message, mock_state)
                            
                            # 验证调用了 answer 显示错误
                            assert mock_message.answer.called


class TestInputAddress:
    """测试 input_address 处理函数"""
    
    async def test_input_address_success(self, mock_message, mock_state):
        """测试输入地址成功"""
        mock_message.text = "0x1234567890abcdef"
        mock_state.get_data = AsyncMock(return_value={"token": "USDT", "amount": "100", "fee": "0.5"})
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw._addr_ok", return_value=True):
                with patch("routers.withdraw.t", return_value="确认提现"):
                    with patch("routers.withdraw._confirm_kb", return_value=Mock()):
                        from routers.withdraw import input_address
                        await input_address(mock_message, mock_state)
                        
                        # 验证调用了 answer
                        assert mock_message.answer.called
                        # 验证状态被更新
                        assert mock_state.update_data.called
                        assert mock_state.set_state.called
    
    async def test_input_address_invalid(self, mock_message, mock_state):
        """测试无效地址"""
        mock_message.text = "invalid_address"
        mock_state.get_data = AsyncMock(return_value={"token": "USDT", "amount": "100", "fee": "0.5"})
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw._addr_ok", return_value=False):
                with patch("routers.withdraw.t", return_value="地址无效"):
                    with patch("routers.withdraw._back_to_token_kb", return_value=Mock()):
                        from routers.withdraw import input_address
                        await input_address(mock_message, mock_state)
                        
                        # 验证调用了 answer 显示错误
                        assert mock_message.answer.called


class TestWdCancel:
    """测试 wd_cancel 处理函数"""
    
    async def test_wd_cancel_success(self, mock_callback_query, mock_state):
        """测试取消提现成功"""
        mock_callback_query.data = "withdraw:cancel"
        
        with patch("routers.withdraw._user_lang", return_value="zh"):
            with patch("routers.withdraw.t", return_value="已取消"):
                with patch("routers.withdraw.back_home_kb", return_value=Mock()):
                    from routers.withdraw import wd_cancel
                    await wd_cancel(mock_callback_query, mock_state)
                    
                    # 验证调用了 answer
                    assert mock_callback_query.answer.called
                    # 验证状态被清除
                    assert mock_state.clear.called


class TestWithdrawHelpers:
    """测试辅助函数"""
    
    def test_canon_lang(self):
        """测试 _canon_lang"""
        from routers.withdraw import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("zh-CN") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("en-US") == "en"
        assert _canon_lang("fr") == "zh"  # 默认
        assert _canon_lang(None) == "zh"
        assert _canon_lang("") == "zh"
    
    def test_q6(self):
        """测试 _q6"""
        from routers.withdraw import _q6
        
        assert _q6(Decimal("100.123456789")) == Decimal("100.123456")
        assert _q6(100.123456789) == Decimal("100.123456")
        assert _q6(100) == Decimal("100.000000")

