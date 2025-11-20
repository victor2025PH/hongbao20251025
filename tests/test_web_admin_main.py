"""
测试 web_admin/main.py 核心功能
"""
import pytest
from fastapi.testclient import TestClient
from web_admin.main import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    return TestClient(app)


def test_healthz_endpoint(client):
    """测试健康检查端点"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert "ok" in data
    assert data["ok"] is True
    assert "ts" in data


def test_readyz_endpoint(client):
    """测试就绪检查端点"""
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert isinstance(data["ready"], bool)
    assert "checks" in data


def test_metrics_endpoint(client):
    """测试 Prometheus 指标端点"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
    content = response.text
    assert "app_uptime_seconds" in content
    assert "app_info" in content


def test_root_redirect(client):
    """测试根路径重定向"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [301, 302, 307, 308]  # 重定向状态码


def test_admin_dashboard_redirect(client):
    """测试 /admin 路径"""
    response = client.get("/admin", follow_redirects=False)
    # 可能是重定向或正常响应
    assert response.status_code in [200, 301, 302, 307, 308]


def test_app_creation():
    """测试应用创建"""
    app = create_app()
    assert app is not None
    # 检查应用标题（可能是 "Admin Console" 或其他）
    assert hasattr(app, "title")
    assert app.title is not None
    # 检查关键路由
    route_paths = [route.path for route in app.routes]
    assert "/healthz" in route_paths
    assert "/readyz" in route_paths
    assert "/metrics" in route_paths

