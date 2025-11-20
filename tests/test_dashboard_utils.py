"""
测试 web_admin/controllers/dashboard.py 工具函数
"""
import pytest
from unittest.mock import MagicMock
from web_admin.controllers.dashboard import _col


def test_col_function():
    """测试 _col 容错字段选择函数"""
    # 创建一个模拟模型
    class MockModel:
        def __init__(self):
            self.name = "test"
            self.id = 123
    
    model = MockModel()
    
    # 测试找到第一个存在的字段
    result = _col(model, "name", "title")
    assert result == "test"
    
    # 测试找到第二个字段（第一个不存在）
    result = _col(model, "nonexistent", "id")
    assert result == 123
    
    # 测试所有字段都不存在
    result = _col(model, "nonexistent1", "nonexistent2")
    assert result is None
    
    # 测试空参数
    result = _col(model)
    assert result is None

