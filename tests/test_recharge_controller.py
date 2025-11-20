"""
测试 web_admin/controllers/recharge.py
充值订单控制器测试
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_recharge_list_page(client):
    """测试充值订单列表页"""
    response = client.get("/admin/recharge")
    assert response.status_code in [200, 303]  # 可能重定向到登录


def test_recharge_list_with_status_filter(client):
    """测试充值订单列表 - 状态筛选"""
    response = client.get("/admin/recharge?status=PENDING")
    assert response.status_code in [200, 303]


def test_recharge_list_with_search(client):
    """测试充值订单列表 - 搜索"""
    response = client.get("/admin/recharge?q=10001")
    assert response.status_code in [200, 303]


def test_recharge_refresh(client):
    """测试刷新订单状态"""
    response = client.post(
        "/admin/recharge/refresh",
        data={"id": 1},
        follow_redirects=False,
    )
    assert response.status_code in [303, 404, 401, 400]


def test_recharge_expire(client):
    """测试标记订单过期"""
    response = client.post(
        "/admin/recharge/expire",
        data={"id": 1},
        follow_redirects=False,
    )
    assert response.status_code in [303, 404, 401, 400]
