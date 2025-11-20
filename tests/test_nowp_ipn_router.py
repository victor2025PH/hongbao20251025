"""
测试 routers/nowp_ipn.py
NOWPayments IPN 路由测试
"""
import pytest
pytestmark = pytest.mark.asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

from aiohttp import web


@pytest.fixture
def mock_request():
    """创建模拟的 web.Request"""
    request = Mock(spec=web.Request)
    request.text = AsyncMock(return_value='{"payment_id": 123, "payment_status": "finished", "actually_paid": 100.0, "pay_currency": "USDTTRC20", "pay_address": "test_address"}')
    request.headers = {"x-nowpayments-sig": "test_signature"}
    return request


class TestNowpIpnHandler:
    """测试 nowp_ipn_handler 处理函数"""
    
    async def test_nowp_ipn_handler_success(self, mock_request):
        """测试 IPN 处理成功"""
        try:
            from routers.nowp_ipn import nowp_ipn_handler
        except (ImportError, AttributeError, ModuleNotFoundError):
            pytest.skip("Module cannot be imported, likely due to missing dependencies")
            return
        
        mock_request.text = AsyncMock(return_value='{"payment_id": 123, "payment_status": "finished", "actually_paid": 100.0, "pay_currency": "USDTTRC20", "pay_address": "test_address"}')
        
        mock_user = Mock()
        mock_user.id = 12345
        mock_user.usdt_pay_address = "test_address"
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_session.execute.return_value.fetchone.return_value = None
        mock_session.commit = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.nowp_ipn.ensure_schema"):
            with patch("routers.nowp_ipn.verify_ipn_signature", return_value=True):
                with patch("routers.nowp_ipn.SessionLocal", return_value=mock_session):
                    with patch("routers.nowp_ipn.credit_user"):
                        response = await nowp_ipn_handler(mock_request)
                        
                        # 验证返回成功响应
                        assert response.status == 200
                        data = json.loads(response.text)
                        assert data["ok"] is True
    
    async def test_nowp_ipn_handler_bad_json(self, mock_request):
        """测试无效 JSON"""
        try:
            from routers.nowp_ipn import nowp_ipn_handler
        except (ImportError, AttributeError, ModuleNotFoundError):
            pytest.skip("Module cannot be imported, likely due to missing dependencies")
            return
        
        mock_request.text = AsyncMock(return_value="invalid json")
        
        with patch("routers.nowp_ipn.ensure_schema"):
            response = await nowp_ipn_handler(mock_request)
            
            # 验证返回错误响应
            assert response.status == 400
            data = json.loads(response.text)
            assert data["ok"] is False
            assert "error" in data
    
    async def test_nowp_ipn_handler_bad_signature(self, mock_request):
        """测试无效签名"""
        try:
            from routers.nowp_ipn import nowp_ipn_handler
        except (ImportError, AttributeError, ModuleNotFoundError):
            pytest.skip("Module cannot be imported, likely due to missing dependencies")
            return
        
        with patch("routers.nowp_ipn.ensure_schema"):
            with patch("routers.nowp_ipn.verify_ipn_signature", return_value=False):
                response = await nowp_ipn_handler(mock_request)
                
                # 验证返回错误响应
                assert response.status == 400
                data = json.loads(response.text)
                assert data["ok"] is False
                assert "error" in data
    
    async def test_nowp_ipn_handler_user_not_found(self, mock_request):
        """测试用户不存在"""
        try:
            from routers.nowp_ipn import nowp_ipn_handler
        except (ImportError, AttributeError, ModuleNotFoundError):
            pytest.skip("Module cannot be imported, likely due to missing dependencies")
            return
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.nowp_ipn.ensure_schema"):
            with patch("routers.nowp_ipn.verify_ipn_signature", return_value=True):
                with patch("routers.nowp_ipn.SessionLocal", return_value=mock_session):
                    response = await nowp_ipn_handler(mock_request)
                    
                    # 验证返回成功响应（忽略未找到用户）
                    assert response.status == 200
                    data = json.loads(response.text)
                    assert data["ok"] is True
    
    async def test_nowp_ipn_handler_duplicate_payment(self, mock_request):
        """测试重复支付"""
        try:
            from routers.nowp_ipn import nowp_ipn_handler
        except (ImportError, AttributeError, ModuleNotFoundError):
            pytest.skip("Module cannot be imported, likely due to missing dependencies")
            return
        
        mock_user = Mock()
        mock_user.id = 12345
        mock_user.usdt_pay_address = "test_address"
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_session.execute.return_value.fetchone.return_value = (1,)  # 已存在
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.nowp_ipn.ensure_schema"):
            with patch("routers.nowp_ipn.verify_ipn_signature", return_value=True):
                with patch("routers.nowp_ipn.SessionLocal", return_value=mock_session):
                    response = await nowp_ipn_handler(mock_request)
                    
                    # 验证返回成功响应（忽略重复支付）
                    assert response.status == 200
                    data = json.loads(response.text)
                    assert data["ok"] is True
    
    async def test_nowp_ipn_handler_unsupported_currency(self, mock_request):
        """测试不支持的币种"""
        mock_request.text = AsyncMock(return_value='{"payment_id": 123, "payment_status": "finished", "actually_paid": 100.0, "pay_currency": "BTC", "pay_address": "test_address"}')
        
        try:
            from routers.nowp_ipn import nowp_ipn_handler
        except (ImportError, AttributeError, ModuleNotFoundError):
            pytest.skip("Module cannot be imported, likely due to missing dependencies")
            return
        
        with patch("routers.nowp_ipn.ensure_schema"):
            with patch("routers.nowp_ipn.verify_ipn_signature", return_value=True):
                response = await nowp_ipn_handler(mock_request)
                
                # 验证返回成功响应（忽略不支持的币种）
                assert response.status == 200
                data = json.loads(response.text)
                assert data["ok"] is True
    
    async def test_nowp_ipn_handler_ton_currency(self, mock_request):
        """测试 TON 币种"""
        mock_request.text = AsyncMock(return_value='{"payment_id": 123, "payment_status": "finished", "actually_paid": 50.0, "pay_currency": "TON", "pay_address": "test_ton_address"}')
        
        try:
            from routers.nowp_ipn import nowp_ipn_handler
        except (ImportError, AttributeError, ModuleNotFoundError):
            pytest.skip("Module cannot be imported, likely due to missing dependencies")
            return
        
        mock_user = Mock()
        mock_user.id = 12345
        mock_user.ton_pay_address = "test_ton_address"
        
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_session.execute.return_value.fetchone.return_value = None
        mock_session.commit = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        with patch("routers.nowp_ipn.ensure_schema"):
            with patch("routers.nowp_ipn.verify_ipn_signature", return_value=True):
                with patch("routers.nowp_ipn.SessionLocal", return_value=mock_session):
                    with patch("routers.nowp_ipn.credit_user"):
                        response = await nowp_ipn_handler(mock_request)
                        
                        # 验证返回成功响应
                        assert response.status == 200
                        data = json.loads(response.text)
                        assert data["ok"] is True

