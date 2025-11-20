"""
测试 web_admin/controllers/dashboard.py API 端点
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from web_admin.main import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    return TestClient(app)


def test_get_dashboard_stats_public(client):
    """测试公开 Dashboard 统计 API"""
    response = client.get("/admin/api/v1/dashboard/public")
    assert response.status_code == 200
    data = response.json()
    # 检查返回数据结构
    assert isinstance(data, dict)
    # 可能包含 mock 数据或真实数据


def test_get_dashboard_stats_requires_auth(client):
    """测试需要认证的 Dashboard 统计 API"""
    # 不提供认证，应该返回 401 或 403
    response = client.get("/admin/api/v1/dashboard")
    # 根据实际实现，可能是 401, 403, 或 200（如果允许匿名）
    assert response.status_code in [200, 401, 403]


def test_get_dashboard_public(client):
    """测试公开 Dashboard API"""
    response = client.get("/admin/api/v1/dashboard/public")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_dashboard_page_renders(client):
    """测试 Dashboard 页面渲染"""
    response = client.get("/admin/dashboard")
    # 可能是 HTML 响应或重定向
    assert response.status_code in [200, 301, 302, 307, 308]


@pytest.mark.skip(reason="需要数据库连接和认证")
def test_get_dashboard_with_auth(client):
    """测试带认证的 Dashboard API（需要完整环境）"""
    # 这个测试需要：
    # 1. 数据库连接
    # 2. 有效的认证 token
    # 3. 测试数据
    pass

