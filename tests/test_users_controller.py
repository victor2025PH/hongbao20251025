"""
测试 web_admin/controllers/users.py 工具函数和 API 端点
"""
import pytest
from datetime import datetime
from web_admin.controllers.users import _parse_date, _parse_user_ref, _paginate


def test_parse_date_valid_formats():
    """测试日期解析函数"""
    # 测试 "2025-01-01" 格式
    result = _parse_date("2025-01-01")
    assert result is not None
    assert isinstance(result, datetime)
    assert result.year == 2025
    assert result.month == 1
    assert result.day == 1
    
    # 测试 "2025-01-01 12:00:00" 格式
    result = _parse_date("2025-01-01 12:00:00")
    assert result is not None
    assert isinstance(result, datetime)
    assert result.hour == 12
    
    # 测试 None
    result = _parse_date(None)
    assert result is None
    
    # 测试空字符串
    result = _parse_date("")
    assert result is None
    
    # 测试无效格式
    result = _parse_date("invalid")
    assert result is None


def test_parse_user_ref():
    """测试用户引用解析函数"""
    # 测试纯数字（tg_id）
    field, value = _parse_user_ref("123456")
    assert field == "tg_id"
    assert value == "123456"
    
    # 测试负数（tg_id）
    field, value = _parse_user_ref("-123456")
    assert field == "tg_id"
    assert value == "-123456"
    
    # 测试 @username 格式
    field, value = _parse_user_ref("@username")
    assert field == "username"
    assert value == "username"
    
    # 测试普通字符串（按 username 处理）
    field, value = _parse_user_ref("username")
    assert field == "username"
    assert value == "username"
    
    # 测试空字符串
    field, value = _parse_user_ref("")
    assert field == ""
    assert value == ""


def test_paginate():
    """测试分页函数"""
    # 测试正常分页
    limit, offset = _paginate(1, 10)
    assert limit == 10
    assert offset == 0
    
    limit, offset = _paginate(2, 10)
    assert limit == 10
    assert offset == 10
    
    limit, offset = _paginate(3, 20)
    assert limit == 20
    assert offset == 40
    
    # 测试页码小于 1（应该自动修正为 1）
    limit, offset = _paginate(0, 10)
    assert limit == 10
    assert offset == 0
    
    limit, offset = _paginate(-1, 10)
    assert limit == 10
    assert offset == 0
    
    # 测试 None（应该使用默认值）
    limit, offset = _paginate(None, 10)
    assert limit == 10
    assert offset == 0

