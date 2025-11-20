"""
测试 routers/balance.py
余额相关路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal
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
    cb.data = "balance:main"
    cb.message = Mock(spec=Message)
    cb.message.edit_text = AsyncMock()
    cb.message.answer = AsyncMock()
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


class TestBalanceMain:
    """测试 balance_main 处理函数"""
    
    async def test_balance_main_success(self, mock_callback_query):
        """测试余额总览成功"""
        mock_callback_query.data = "balance:main"
        
        # Mock get_balance_summary
        mock_summary = {
            "usdt": 100.50,
            "ton": 50.25,
            "point": 1000,
            "energy": 500
        }
        
        with patch("routers.balance.get_balance_summary", return_value=mock_summary):
            with patch("routers.balance._db_lang", return_value="zh"):
                with patch("routers.balance.t", return_value="测试标题"):
                    with patch("routers.balance.asset_menu", return_value=Mock()):
                        from routers.balance import balance_main
                        await balance_main(mock_callback_query)
                        
                        # 验证调用了 edit_text 或 answer
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                        assert mock_callback_query.answer.called
    
    async def test_balance_main_telegram_bad_request(self, mock_callback_query):
        """测试 TelegramBadRequest 时使用 answer"""
        mock_callback_query.data = "balance:main"
        # TelegramBadRequest 需要 message 参数
        mock_callback_query.message.edit_text = AsyncMock(
            side_effect=TelegramBadRequest(method="editMessageText", message="Bad request")
        )
        
        mock_summary = {
            "usdt": 0.0,
            "ton": 0.0,
            "point": 0,
            "energy": 0
        }
        
        with patch("routers.balance.get_balance_summary", return_value=mock_summary):
            with patch("routers.balance._db_lang", return_value="zh"):
                with patch("routers.balance.t", return_value="测试标题"):
                    with patch("routers.balance.asset_menu", return_value=Mock()):
                        from routers.balance import balance_main
                        await balance_main(mock_callback_query)
                        
                        # 应该调用 answer 而不是 edit_text
                        assert mock_callback_query.message.answer.called
                        assert mock_callback_query.answer.called


class TestBalanceTokenDetail:
    """测试 balance_token_detail 处理函数"""
    
    async def test_balance_token_detail_usdt(self, mock_callback_query, mock_db_session):
        """测试 USDT 明细"""
        mock_callback_query.data = "balance:USDT"
        
        # Mock 数据库查询
        mock_ledger = Mock(spec=Ledger)
        mock_ledger.type = LedgerType.RECHARGE
        mock_ledger.amount = Decimal("10.50")
        mock_ledger.created_at = datetime.now(UTC)
        mock_ledger.note = "充值"
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[mock_ledger])
        mock_db_session.query.return_value = mock_query
        
        mock_summary = {"usdt": 100.50, "ton": 0.0, "point": 0}
        
        with patch("routers.balance.get_session", return_value=mock_db_session):
            with patch("routers.balance.get_balance_summary", return_value=mock_summary):
                with patch("routers.balance._db_lang", return_value="zh"):
                    with patch("routers.balance.t", return_value="USDT 明细"):
                        with patch("routers.balance.back_home_kb", return_value=Mock()):
                            from routers.balance import balance_token_detail
                            await balance_token_detail(mock_callback_query)
                            
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
                            assert mock_callback_query.answer.called
    
    async def test_balance_token_detail_point(self, mock_callback_query, mock_db_session):
        """测试 POINT 明细"""
        mock_callback_query.data = "balance:POINT"
        
        # Mock 空流水
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[])
        mock_db_session.query.return_value = mock_query
        
        mock_summary = {"usdt": 0.0, "ton": 0.0, "point": 1000}
        
        with patch("routers.balance.get_session", return_value=mock_db_session):
            with patch("routers.balance.get_balance_summary", return_value=mock_summary):
                with patch("routers.balance._db_lang", return_value="zh"):
                    with patch("routers.balance.t", return_value="积分明细"):
                        with patch("routers.balance.back_home_kb", return_value=Mock()):
                            from routers.balance import balance_token_detail
                            await balance_token_detail(mock_callback_query)
                            
                            assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestBalanceHistory:
    """测试 balance_history 处理函数"""
    
    async def test_balance_history_with_data(self, mock_callback_query, mock_db_session):
        """测试历史流水（有数据）"""
        mock_callback_query.data = "balance:history"
        
        # Mock 多条流水记录
        mock_ledgers = []
        for i in range(5):
            ledger = Mock(spec=Ledger)
            ledger.type = LedgerType.RECHARGE if i % 2 == 0 else LedgerType.WITHDRAW
            ledger.amount = Decimal(f"{10 + i}.50")
            ledger.token = "USDT" if i % 2 == 0 else "TON"
            ledger.created_at = datetime.now(UTC)
            ledger.note = f"记录{i}"
            mock_ledgers.append(ledger)
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=mock_ledgers)
        mock_db_session.query.return_value = mock_query
        
        with patch("routers.balance.get_session", return_value=mock_db_session):
            with patch("routers.balance._db_lang", return_value="zh"):
                with patch("routers.balance.t", return_value="历史记录"):
                    with patch("routers.balance.back_home_kb", return_value=Mock()):
                        from routers.balance import balance_history
                        await balance_history(mock_callback_query)
                        
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called
    
    async def test_balance_history_empty(self, mock_callback_query, mock_db_session):
        """测试历史流水（无数据）"""
        mock_callback_query.data = "balance:history"
        
        # Mock 空流水
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[])
        mock_db_session.query.return_value = mock_query
        
        with patch("routers.balance.get_session", return_value=mock_db_session):
            with patch("routers.balance._db_lang", return_value="zh"):
                with patch("routers.balance.t", return_value="无记录"):
                    with patch("routers.balance.back_home_kb", return_value=Mock()):
                        from routers.balance import balance_history
                        await balance_history(mock_callback_query)
                        
                        assert mock_callback_query.message.edit_text.called or mock_callback_query.message.answer.called


class TestBalanceHelpers:
    """测试辅助函数"""
    
    def test_canon_lang(self):
        """测试 _canon_lang"""
        from routers.balance import _canon_lang
        
        assert _canon_lang("zh") == "zh"
        assert _canon_lang("zh-CN") == "zh"
        assert _canon_lang("en") == "en"
        assert _canon_lang("en-US") == "en"
        assert _canon_lang("fr") == "zh"  # 默认
        assert _canon_lang(None) == "zh"
        assert _canon_lang("") == "zh"
    
    def test_fmt6(self):
        """测试 _fmt6"""
        from routers.balance import _fmt6
        
        assert _fmt6(10.5) == "10.50"
        assert _fmt6(100.123456) == "100.12"
        assert _fmt6(0) == "0.00"
    
    def test_fmt_token_amount(self):
        """测试 _fmt_token_amount"""
        from routers.balance import _fmt_token_amount
        
        # POINT 应该显示为整数
        assert _fmt_token_amount("POINT", 100.5) == "100"
        assert _fmt_token_amount("POINTS", 100.5) == "100"
        
        # USDT/TON 应该显示为小数
        assert _fmt_token_amount("USDT", 100.5) == "100.50"
        assert _fmt_token_amount("TON", 50.25) == "50.25"

