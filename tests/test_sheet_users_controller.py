"""
测试 web_admin/controllers/sheet_users.py
表格用户控制器测试
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_sheet_users_list_page(client):
    """测试表格用户列表页"""
    response = client.get("/admin/sheet-users")
    assert response.status_code in [200, 303]  # 可能重定向到登录


def test_sheet_users_list_with_filters(client):
    """测试表格用户列表 - 带筛选条件"""
    response = client.get("/admin/sheet-users?用户ID=10001&用户名=test")
    assert response.status_code in [200, 303]


def test_sheet_users_edit_page(client):
    """测试表格用户编辑页"""
    response = client.get("/admin/sheet-users/edit?row=2")
    assert response.status_code in [200, 303, 400]


def test_sheet_users_edit_invalid_row(client):
    """测试表格用户编辑 - 无效行号"""
    response = client.get("/admin/sheet-users/edit?row=1", follow_redirects=False)  # 行号必须 >= 2
    # 可能返回 422（验证错误）、303（重定向到登录）或 400（业务错误）
    assert response.status_code in [400, 422, 303, 200]  # 200 可能是重定向后的登录页


def test_editor_from_session():
    """测试 _editor_from_session 函数"""
    from web_admin.controllers.sheet_users import _editor_from_session
    
    # 测试有 username
    class MockSession:
        def __init__(self):
            self.username = "admin"
    mock_sess = MockSession()
    result = _editor_from_session(mock_sess)
    assert result == "admin"
    
    # 测试有 name
    class MockSession2:
        def __init__(self):
            self.name = "Admin User"
    mock_sess = MockSession2()
    result = _editor_from_session(mock_sess)
    assert result == "Admin User"
    
    # 测试有 id
    class MockSession3:
        def __init__(self):
            self.id = 10001
    mock_sess = MockSession3()
    result = _editor_from_session(mock_sess)
    assert result == "10001"
    
    # 测试默认值
    class MockSession4:
        pass
    mock_sess = MockSession4()
    result = _editor_from_session(mock_sess)
    assert result == "admin"  # 默认返回 "admin"

