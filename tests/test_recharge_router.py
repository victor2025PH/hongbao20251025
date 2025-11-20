"""
测试 routers/recharge.py
充值相关路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal

from aiogram.types import CallbackQuery, User as TgUser, Message, Chat
from aiogram.exceptions import TelegramBadRequest


@pytest.fixture
def mock_callback_query():
    """创建模拟的 CallbackQuery"""
    cb = Mock(spec=CallbackQuery)
    cb.from_user = Mock(spec=TgUser)
    cb.from_user.id = 12345
    cb.from_user.language_code = "zh"
    cb.data = "recharge:main"
    cb.message = Mock(spec=Message)
    cb.message.chat = Mock(spec=Chat)
    cb.message.chat.id = 12345
    cb.message.message_id = 100
    cb.message.edit_text = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.message.answer_photo = AsyncMock()
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
    msg.text = "/recharge"
    msg.answer = AsyncMock()
    return msg


class TestRechargeMain:
    """测试 recharge_main 处理函数"""
    
    async def test_recharge_main_success(self, mock_callback_query):
        """测试充值主页面成功"""
        mock_callback_query.data = "recharge:main"
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._clear_pending"):
                with patch("routers.recharge._tt", return_value="充值中心"):
                    with patch("routers.recharge._tt_first", return_value="选择充值方式"):
                        with patch("routers.recharge.recharge_main_kb", return_value=Mock()):
                            from routers.recharge import recharge_main
                            await recharge_main(mock_callback_query)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                            assert mock_callback_query.answer.called
    
    async def test_recharge_main_telegram_bad_request(self, mock_callback_query):
        """测试 TelegramBadRequest 时使用 answer"""
        mock_callback_query.data = "recharge:main"
        mock_callback_query.message.edit_text = AsyncMock(
            side_effect=TelegramBadRequest(method="editMessageText", message="Bad request")
        )
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._clear_pending"):
                with patch("routers.recharge._tt", return_value="充值中心"):
                    with patch("routers.recharge._tt_first", return_value="选择充值方式"):
                        with patch("routers.recharge.recharge_main_kb", return_value=Mock()):
                            from routers.recharge import recharge_main
                            await recharge_main(mock_callback_query)
                            
                            # 应该调用 answer 而不是 edit_text
                            assert mock_callback_query.message.answer.called
                            assert mock_callback_query.answer.called


class TestRechargeChooseToken:
    """测试 recharge_choose_token 处理函数"""
    
    async def test_recharge_choose_token_usdt(self, mock_callback_query):
        """测试选择 USDT"""
        mock_callback_query.data = "recharge:new:USDT"
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._clear_pending"):
                with patch("routers.recharge._PENDING_TOKEN", {}):
                    with patch("routers.recharge._tt", return_value="充值"):
                        with patch("routers.recharge._amount_kb_usd", return_value=Mock()):
                            from routers.recharge import recharge_choose_token
                            await recharge_choose_token(mock_callback_query)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                            assert mock_callback_query.answer.called
    
    async def test_recharge_choose_token_ton(self, mock_callback_query):
        """测试选择 TON"""
        mock_callback_query.data = "recharge:new:TON"
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._clear_pending"):
                with patch("routers.recharge._PENDING_TOKEN", {}):
                    with patch("routers.recharge._tt", return_value="充值"):
                        with patch("routers.recharge._amount_kb_usd", return_value=Mock()):
                            from routers.recharge import recharge_choose_token
                            await recharge_choose_token(mock_callback_query)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestRechargeAmountQuick:
    """测试 recharge_amount_quick 处理函数"""
    
    async def test_recharge_amount_quick_success(self, mock_callback_query):
        """测试快捷金额充值成功"""
        mock_callback_query.data = "recharge:amt:100"
        
        # Mock 订单对象
        mock_order = Mock()
        mock_order.id = 1
        mock_order.pay_address = "test_address"
        mock_order.pay_url = "https://payment.example.com"
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._PENDING_TOKEN", {12345: "USDT"}):
                with patch("routers.recharge._AWAITING_AMOUNT", {}):
                    with patch("routers.recharge._start_fake_loader", new_callable=AsyncMock, return_value=AsyncMock()):
                        with patch("routers.recharge._svc_new_order", return_value=lambda **kwargs: mock_order):
                            with patch("routers.recharge._svc_ensure_payment", return_value=lambda order: order):
                                with patch("routers.recharge._order_pay_url_from_obj", return_value="https://payment.example.com"):
                                    with patch("routers.recharge._build_qr_bytes", return_value=None):
                                        with patch("routers.recharge._order_card_text", return_value="订单详情"):
                                            with patch("routers.recharge.recharge_order_kb", return_value=Mock()):
                                                from routers.recharge import recharge_amount_quick
                                                await recharge_amount_quick(mock_callback_query)
                                                
                                                # 函数执行成功即可
                                                assert True


class TestRechargeRefresh:
    """测试 recharge_refresh 处理函数"""
    
    async def test_recharge_refresh_success(self, mock_callback_query):
        """测试刷新订单成功"""
        mock_callback_query.data = "recharge:refresh:1"
        
        # Mock 订单对象
        mock_order = Mock()
        mock_order.id = 1
        mock_order.status = "pending"
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._svc_get_order", return_value=lambda order_id: mock_order):
                with patch("routers.recharge._svc_refresh", return_value=lambda order: order):
                    with patch("routers.recharge._order_card_text", return_value="订单详情"):
                        with patch("routers.recharge.recharge_order_kb", return_value=Mock()):
                            from routers.recharge import recharge_refresh
                            await recharge_refresh(mock_callback_query)
                            
                            # 验证调用了 edit_text 或 answer
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                            assert mock_callback_query.answer.called
    
    async def test_recharge_refresh_not_found(self, mock_callback_query):
        """测试订单不存在"""
        mock_callback_query.data = "recharge:refresh:999"
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._svc_get_order", return_value=lambda order_id: None):
                with patch("routers.recharge._tt", return_value="订单不存在"):
                    with patch("routers.recharge.recharge_main_kb", return_value=Mock()):
                        from routers.recharge import recharge_refresh
                        await recharge_refresh(mock_callback_query)
                        
                        # 函数执行成功即可
                        assert True


class TestRechargeCopyAddress:
    """测试 recharge_copy_address 处理函数"""
    
    async def test_recharge_copy_address_success(self, mock_callback_query):
        """测试复制地址成功"""
        mock_callback_query.data = "recharge:copy_addr:1"
        
        # Mock 订单对象
        mock_order = Mock()
        mock_order.id = 1
        mock_order.pay_address = "test_address_12345"
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._svc_get_order", return_value=lambda order_id: mock_order):
                with patch("routers.recharge._tt", return_value="地址已复制"):
                    from routers.recharge import recharge_copy_address
                    await recharge_copy_address(mock_callback_query)
                    
                    # 验证调用了 answer
                    assert mock_callback_query.answer.called


class TestRechargeCopyAmount:
    """测试 recharge_copy_amount 处理函数"""
    
    async def test_recharge_copy_amount_success(self, mock_callback_query):
        """测试复制金额成功"""
        mock_callback_query.data = "recharge:copy_amt:1"
        
        # Mock 订单对象
        mock_order = Mock()
        mock_order.id = 1
        mock_order.amount = Decimal("100.00")
        mock_order.token = "USDT"
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._svc_get_order", return_value=lambda order_id: mock_order):
                with patch("routers.recharge._tt", return_value="金额已复制"):
                    from routers.recharge import recharge_copy_amount
                    await recharge_copy_amount(mock_callback_query)
                    
                    # 验证调用了 answer
                    assert mock_callback_query.answer.called


class TestCmdRecharge:
    """测试 cmd_recharge 处理函数"""
    
    async def test_cmd_recharge_success(self, mock_message):
        """测试充值命令成功"""
        mock_message.text = "/recharge"
        
        with patch("routers.recharge._db_lang_or_fallback", return_value="zh"):
            with patch("routers.recharge._clear_pending"):
                with patch("routers.recharge._tt", return_value="充值中心"):
                    with patch("routers.recharge._tt_first", return_value="选择充值方式"):
                        with patch("routers.recharge.recharge_main_kb", return_value=Mock()):
                            from routers.recharge import cmd_recharge
                            await cmd_recharge(mock_message)
                            
                            # 验证调用了 answer
                            assert mock_message.answer.called
