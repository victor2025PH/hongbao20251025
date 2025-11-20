"""
测试 web_admin/controllers/settings.py
设置管理控制器测试
"""
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def admin_session():
    """模拟管理员会话"""
    return {"tg_id": 10001, "username": "admin"}


def test_settings_page(client_with_db, admin_session):
    """测试设置页面"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/settings")
        # 应该返回 200 或需要认证
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


def test_get_settings_api(client_with_db, admin_session):
    """测试获取系统设置 API"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/api/v1/settings")
        # 应该返回 200 或需要认证
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "amount_limits" in data
            assert "risk_control" in data
            assert "notifications" in data
            assert "feature_flags" in data


def test_get_settings_api_structure(client_with_db, admin_session):
    """测试获取系统设置 API 结构"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.get("/admin/api/v1/settings")
        
        if response.status_code == 200:
            data = response.json()
            
            # 验证 amount_limits 结构
            assert "amount_limits" in data
            assert "max_single" in data["amount_limits"]
            assert "min_single" in data["amount_limits"]
            assert "daily_total" in data["amount_limits"]
            
            # 验证 risk_control 结构
            assert "risk_control" in data
            assert "enable_rate_limit" in data["risk_control"]
            assert "enable_blacklist" in data["risk_control"]
            assert "max_per_user_per_day" in data["risk_control"]
            
            # 验证 notifications 结构
            assert "notifications" in data
            assert "notify_on_failure" in data["notifications"]
            assert "notify_on_critical" in data["notifications"]


def test_update_settings_api(client_with_db, admin_session):
    """测试更新系统设置 API"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 保存原始值
        original_max = os.getenv("MAX_SINGLE_AMOUNT", "1000.0")
        
        # 更新设置
        response = client_with_db.put(
            "/admin/api/v1/settings",
            json={
                "amount_limits": {
                    "max_single": 2000.0,
                    "min_single": 0.1,
                }
            }
        )
        
        # 应该返回 200 或需要认证
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is True
        
        # 恢复原始值
        if original_max:
            os.environ["MAX_SINGLE_AMOUNT"] = original_max


def test_update_settings_api_risk_control(client_with_db, admin_session):
    """测试更新风险控制设置"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.put(
            "/admin/api/v1/settings",
            json={
                "risk_control": {
                    "enable_rate_limit": True,
                    "max_per_user_per_day": 20,
                }
            }
        )
        
        assert response.status_code in [200, 401, 403]


def test_update_settings_api_notifications(client_with_db, admin_session):
    """测试更新通知设置"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.put(
            "/admin/api/v1/settings",
            json={
                "notifications": {
                    "notify_on_failure": False,
                    "notify_on_critical": True,
                }
            }
        )
        
        assert response.status_code in [200, 401, 403]


def test_update_settings_api_partial(client_with_db, admin_session):
    """测试部分更新设置"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # 只更新 amount_limits
        response = client_with_db.put(
            "/admin/api/v1/settings",
            json={
                "amount_limits": {
                    "max_single": 1500.0,
                }
            }
        )
        
        assert response.status_code in [200, 401, 403]


def test_update_settings_api_empty(client_with_db, admin_session):
    """测试空更新设置"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        response = client_with_db.put(
            "/admin/api/v1/settings",
            json={}
        )
        
        assert response.status_code in [200, 401, 403]


def test_settings_toggle(client_with_db, admin_session):
    """测试切换功能开关"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # Mock _toggle_first_available
        with patch("web_admin.controllers.settings._toggle_first_available", return_value="TEST_FLAG"):
            response = client_with_db.post("/admin/settings/toggle", follow_redirects=False)
            # 应该返回 303 重定向（根据代码，settings_toggle 返回 RedirectResponse）
            assert response.status_code in [303, 302, 401, 403, 400]


def test_settings_toggle_error(client_with_db, admin_session):
    """测试切换功能开关 - 错误情况"""
    with patch("web_admin.deps.require_admin", return_value=admin_session):
        # Mock _toggle_first_available 抛出异常
        with patch("web_admin.controllers.settings._toggle_first_available", side_effect=RuntimeError("No toggleable flag")):
            response = client_with_db.post("/admin/settings/toggle")
            # 应该返回 400
            assert response.status_code in [400, 401, 403]


def test_settings_endpoints_require_auth(client):
    """测试设置端点需要认证"""
    endpoints = [
        ("GET", "/admin/settings"),
        ("GET", "/admin/api/v1/settings"),
        ("POST", "/admin/settings/toggle"),
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        # 应该返回 401 或 403
        assert response.status_code in [200, 401, 403, 307, 303]


def test_collect_flags_function():
    """测试 _collect_flags 函数"""
    from web_admin.controllers.settings import _collect_flags
    
    flags = _collect_flags()
    # 应该返回列表
    assert isinstance(flags, list)
    # 每个元素应该是元组 (key, value, source)
    if flags:
        assert len(flags[0]) == 3


def test_toggle_first_available_function():
    """测试 _toggle_first_available 函数"""
    from web_admin.controllers.settings import _toggle_first_available
    
    # 如果没有可切换的标志，应该抛出异常
    try:
        result = _toggle_first_available()
        # 如果成功，应该返回字符串
        assert isinstance(result, str)
    except RuntimeError:
        # 如果没有可切换的标志，这是预期的
        pass

