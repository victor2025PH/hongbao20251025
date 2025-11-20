"""
测试 web_admin/controllers/a11y.py
无障碍检查控制器测试
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_a11y_page(client):
    """测试无障碍检查页"""
    response = client.get("/admin/a11y")
    assert response.status_code in [200, 303]  # 可能重定向到登录


def test_i18n_probe():
    """测试 _i18n_probe 函数"""
    from web_admin.controllers.a11y import _i18n_probe
    
    result = _i18n_probe()
    
    assert isinstance(result, dict)
    assert "required" in result
    assert "missing" in result
    assert "missing_count" in result
    assert isinstance(result["required"], int)
    assert isinstance(result["missing"], list)
    assert isinstance(result["missing_count"], int)


def test_env_probe():
    """测试 _env_probe 函数"""
    from web_admin.controllers.a11y import _env_probe
    
    result = _env_probe()
    
    assert isinstance(result, dict)
    # 验证包含预期的环境变量键
    assert "ADMIN_WEB_USER" in result or len(result) > 0

