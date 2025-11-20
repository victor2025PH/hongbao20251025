"""
测试 web_admin/controllers/ipn.py
支付回调控制器测试
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


def test_ipn_health(client):
    """测试 IPN 健康检查"""
    response = client.get("/api/np/ipn/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True


def test_ipn_nowpayments_empty_body(client):
    """测试 IPN 回调 - 空请求体"""
    response = client.post(
        "/api/np/ipn",
        headers={"X-Nowpayments-Sig": "test_signature"},
        content=b"",
    )
    # 应该返回 400
    assert response.status_code == 400


def test_ipn_nowpayments_missing_signature(client):
    """测试 IPN 回调 - 缺少签名头"""
    response = client.post(
        "/api/np/ipn",
        json={"order_id": "123", "payment_status": "finished"},
    )
    # 应该返回 400
    assert response.status_code == 400


def test_ipn_nowpayments_invalid_signature(client):
    """测试 IPN 回调 - 无效签名"""
    # 需要 patch 控制器中导入的函数
    with patch("web_admin.controllers.ipn.verify_ipn_signature", return_value=False):
        response = client.post(
            "/api/np/ipn",
            headers={"X-Nowpayments-Sig": "invalid_signature", "Content-Type": "application/json"},
            json={"order_id": "123", "payment_status": "finished"},
        )
        # 应该返回 403（验证失败）
        assert response.status_code == 403


def test_ipn_nowpayments_invalid_json(client):
    """测试 IPN 回调 - 无效 JSON"""
    # 需要 patch 控制器中导入的函数
    with patch("web_admin.controllers.ipn.verify_ipn_signature", return_value=True):
        response = client.post(
            "/api/np/ipn",
            headers={"X-Nowpayments-Sig": "valid_signature", "Content-Type": "application/json"},
            content=b"invalid json",
        )
        # 应该返回 400
        assert response.status_code == 400


def test_ipn_nowpayments_invalid_order_id(client):
    """测试 IPN 回调 - 无效订单ID"""
    # 需要 patch 控制器中导入的函数
    with patch("web_admin.controllers.ipn.verify_ipn_signature", return_value=True):
        response = client.post(
            "/api/np/ipn",
            headers={"X-Nowpayments-Sig": "valid_signature", "Content-Type": "application/json"},
            json={"order_id": "invalid", "payment_status": "finished"},
        )
        # 应该返回 400
        assert response.status_code == 400


def test_ipn_nowpayments_success(client):
    """测试 IPN 回调 - 成功状态"""
    # 需要 patch services.recharge_service 中的函数
    # 同时 mock 数据库访问，避免订单不存在的问题
    # 需要 patch 控制器中导入的函数，而不是服务中的函数
    with patch("web_admin.controllers.ipn.verify_ipn_signature", return_value=True):
        with patch("web_admin.controllers.ipn.mark_order_success") as mock_success:
            # Mock mark_order_success 不抛出异常
            mock_success.return_value = True
            # FastAPI Header 参数使用 alias="X-Nowpayments-Sig"
            response = client.post(
                "/api/np/ipn",
                headers={"X-Nowpayments-Sig": "valid_signature", "Content-Type": "application/json"},
                json={
                    "order_id": "123",
                    "payment_status": "finished",
                    "payment_id": "pay_123",
                    "pay_address": "test_address",
                },
            )
            # 应该返回 200
            if response.status_code != 200:
                print(f"Response status: {response.status_code}")
                print(f"Response text: {response.text}")
            assert response.status_code == 200
            data = response.json()
            assert data.get("ok") is True
            assert data.get("order_id") == 123
            # 验证调用了 mark_order_success
            mock_success.assert_called_once()


def test_ipn_nowpayments_failed(client):
    """测试 IPN 回调 - 失败状态"""
    # 需要 patch 控制器中导入的函数
    with patch("web_admin.controllers.ipn.verify_ipn_signature", return_value=True):
        with patch("web_admin.controllers.ipn.mark_order_failed") as mock_failed:
            mock_failed.return_value = True
            response = client.post(
                "/api/np/ipn",
                headers={"X-Nowpayments-Sig": "valid_signature", "Content-Type": "application/json"},
                json={
                    "order_id": "123",
                    "payment_status": "failed",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get("ok") is True
            # 验证调用了 mark_order_failed
            mock_failed.assert_called_once()


def test_ipn_nowpayments_expired(client):
    """测试 IPN 回调 - 过期状态"""
    # 需要 patch 控制器中导入的函数
    with patch("web_admin.controllers.ipn.verify_ipn_signature", return_value=True):
        with patch("web_admin.controllers.ipn.mark_order_expired") as mock_expired:
            mock_expired.return_value = True
            response = client.post(
                "/api/np/ipn",
                headers={"X-Nowpayments-Sig": "valid_signature", "Content-Type": "application/json"},
                json={
                    "order_id": "123",
                    "payment_status": "expired",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get("ok") is True
            # 验证调用了 mark_order_expired
            mock_expired.assert_called_once()


def test_ipn_nowpayments_pending(client):
    """测试 IPN 回调 - 待处理状态"""
    # 需要 patch 控制器中导入的函数
    with patch("web_admin.controllers.ipn.verify_ipn_signature", return_value=True):
        with patch("web_admin.controllers.ipn.refresh_status_if_needed") as mock_refresh:
            mock_refresh.return_value = True
            response = client.post(
                "/api/np/ipn",
                headers={"X-Nowpayments-Sig": "valid_signature", "Content-Type": "application/json"},
                json={
                    "order_id": "123",
                    "payment_status": "pending",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data.get("ok") is True
            # 验证调用了 refresh_status_if_needed
            mock_refresh.assert_called_once()


def test_map_status_function():
    """测试 _map_status 函数"""
    from web_admin.controllers.ipn import _map_status
    from models.recharge import OrderStatus
    
    # 测试成功状态
    assert _map_status("finished") == OrderStatus.SUCCESS
    assert _map_status("confirmed") == OrderStatus.SUCCESS
    assert _map_status("paid") == OrderStatus.SUCCESS
    
    # 测试失败状态
    assert _map_status("failed") == OrderStatus.FAILED
    assert _map_status("refunded") == OrderStatus.FAILED
    
    # 测试过期状态
    assert _map_status("expired") == OrderStatus.EXPIRED
    
    # 测试待处理状态
    assert _map_status("pending") == OrderStatus.PENDING
    assert _map_status("unknown") == OrderStatus.PENDING
    assert _map_status(None) == OrderStatus.PENDING

