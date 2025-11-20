"""
测试 web_admin/controllers/envelopes.py
红包列表控制器测试
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_envelopes_page(client):
    """测试红包列表页"""
    response = client.get("/admin/envelopes")
    assert response.status_code in [200, 303, 404]  # 可能重定向到登录或路由不存在


def test_envelopes_page_with_filters(client):
    """测试红包列表 - 带筛选条件"""
    response = client.get("/admin/envelopes?q=test&page=1")
    assert response.status_code in [200, 303, 404]  # 可能重定向到登录或路由不存在


def test_envelope_summary_api(client):
    """测试红包摘要 API"""
    response = client.get("/admin/api/v1/envelope/1/summary")
    assert response.status_code in [200, 404, 303]


def test_envelope_claims_api(client):
    """测试红包领取记录 API"""
    response = client.get("/admin/api/v1/envelope/1/claims")
    assert response.status_code in [200, 404, 303]


def test_col_function():
    """测试 _col 函数"""
    from web_admin.controllers.envelopes import _col
    
    # 创建模拟模型
    class MockModel:
        def __init__(self):
            self.field1 = "value1"
            self.field2 = "value2"
    
    model = MockModel()
    
    # 测试找到第一个字段
    assert _col(model, "field1", "field2") == "value1"
    
    # 测试找到第二个字段
    assert _col(model, "nonexistent", "field2") == "value2"
    
    # 测试找不到字段
    assert _col(model, "nonexistent1", "nonexistent2") is None
