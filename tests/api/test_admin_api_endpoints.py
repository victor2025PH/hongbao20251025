# -*- coding: utf-8 -*-
"""
Web Admin API 端点测试

测试目标: 使用 FastAPI TestClient 进行单元测试
支持集成测试模式: 设置环境变量 API_TEST_ADMIN_BASE_URL 可切换到真实 HTTP 请求
"""

from __future__ import annotations

import os
import time
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient

# 检查是否使用集成测试模式
USE_INTEGRATION_TEST = os.getenv("API_TEST_ADMIN_BASE_URL") is not None

if USE_INTEGRATION_TEST:
    # 集成测试模式：使用真实 HTTP 请求
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    ADMIN_BASE_URL = os.getenv("API_TEST_ADMIN_BASE_URL", "http://localhost:8000").rstrip("/")
    
    @pytest.fixture(scope="module")
    def admin_session():
        """创建带重试机制的 HTTP 会话"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
else:
    # 单元测试模式：使用 FastAPI TestClient
    from web_admin.main import create_app
    
    @pytest.fixture(scope="module")
    def admin_session():
        """创建 FastAPI 测试客户端"""
        app = create_app()
        return TestClient(app)


class TestAdminHealthEndpoints:
    """Web Admin API 健康检查端点测试"""

    def test_healthz(self, admin_session):
        """测试 /healthz 端点"""
        if USE_INTEGRATION_TEST:
            # 集成测试模式
            url = f"{ADMIN_BASE_URL}/healthz"
            start_time = time.time()
            response = admin_session.get(url, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        else:
            # 单元测试模式
            start_time = time.time()
            response = admin_session.get("/healthz")
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "ok" in data, "Response should contain 'ok' field"
        assert data["ok"] is True, "ok field should be True"
        assert "ts" in data, "Response should contain 'ts' field"
        
        # 记录性能指标
        if hasattr(response, 'elapsed_ms'):
            response.elapsed_ms = elapsed_ms
        print(f"\n[PERF] /healthz: {elapsed_ms:.2f}ms")

    def test_readyz(self, admin_session):
        """测试 /readyz 端点"""
        if USE_INTEGRATION_TEST:
            url = f"{ADMIN_BASE_URL}/readyz"
            start_time = time.time()
            response = admin_session.get(url, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        else:
            start_time = time.time()
            response = admin_session.get("/readyz")
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "ready" in data, "Response should contain 'ready' field"
        assert isinstance(data["ready"], bool), "ready field should be boolean"
        assert "checks" in data, "Response should contain 'checks' field"
        
        if hasattr(response, 'elapsed_ms'):
            response.elapsed_ms = elapsed_ms
        print(f"\n[PERF] /readyz: {elapsed_ms:.2f}ms")

    def test_metrics(self, admin_session):
        """测试 /metrics 端点（Prometheus 指标）"""
        if USE_INTEGRATION_TEST:
            url = f"{ADMIN_BASE_URL}/metrics"
            start_time = time.time()
            response = admin_session.get(url, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000
        else:
            start_time = time.time()
            response = admin_session.get("/metrics")
            elapsed_ms = (time.time() - start_time) * 1000
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers.get("Content-Type", "").startswith("text/plain"), \
            "Metrics should return text/plain content"
        
        # 验证 Prometheus 格式
        content = response.text
        assert "# HELP" in content or "# TYPE" in content or "app_uptime_seconds" in content, \
            "Response should contain Prometheus format"
        
        if hasattr(response, 'elapsed_ms'):
            response.elapsed_ms = elapsed_ms
        print(f"\n[PERF] /metrics: {elapsed_ms:.2f}ms")

    def test_openapi_schema(self, admin_session):
        """测试 /openapi.json 端点"""
        if USE_INTEGRATION_TEST:
            url = f"{ADMIN_BASE_URL}/openapi.json"
            start_time = time.time()
            response = admin_session.get(url, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        else:
            start_time = time.time()
            response = admin_session.get("/openapi.json")
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "openapi" in data, "Response should contain 'openapi' field"
        assert "info" in data, "Response should contain 'info' field"
        assert "paths" in data, "Response should contain 'paths' field"
        
        if hasattr(response, 'elapsed_ms'):
            response.elapsed_ms = elapsed_ms
        print(f"\n[PERF] /openapi.json: {elapsed_ms:.2f}ms")

    @pytest.mark.skip(reason="Swagger UI is disabled in production (docs_url=None)")
    def test_docs(self, admin_session):
        """测试 /docs 端点（生产环境已禁用，跳过）"""
        if USE_INTEGRATION_TEST:
            url = f"{ADMIN_BASE_URL}/docs"
            response = admin_session.get(url, timeout=10)
        else:
            response = admin_session.get("/docs")
        # 在生产环境，这应该返回 404
        assert response.status_code == 404, "Swagger UI should be disabled in production"


class TestAdminDashboardEndpoints:
    """Web Admin API Dashboard 端点测试"""

    def test_dashboard_public(self, admin_session):
        """测试 /admin/api/v1/dashboard/public 端点（公开数据，无需认证）"""
        if USE_INTEGRATION_TEST:
            url = f"{ADMIN_BASE_URL}/admin/api/v1/dashboard/public"
            start_time = time.time()
            response = admin_session.get(url, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000
        else:
            start_time = time.time()
            response = admin_session.get("/admin/api/v1/dashboard/public")
            elapsed_ms = (time.time() - start_time) * 1000
        
        # 公开端点可能返回 200 或 404（如果没有数据）
        assert response.status_code in [200, 404], \
            f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            # 验证基本结构（具体字段取决于实现）
            assert isinstance(data, (dict, list)), "Response should be JSON object or array"
        
        if hasattr(response, 'elapsed_ms'):
            response.elapsed_ms = elapsed_ms
        print(f"\n[PERF] /admin/api/v1/dashboard/public: {elapsed_ms:.2f}ms")

    @pytest.mark.skip(reason="Requires authentication (Session Cookie or JWT)")
    def test_dashboard_authenticated(self, admin_session):
        """测试 /admin/api/v1/dashboard 端点（需要认证）"""
        if USE_INTEGRATION_TEST:
            url = f"{ADMIN_BASE_URL}/admin/api/v1/dashboard"
            response = admin_session.get(url, timeout=10)
        else:
            response = admin_session.get("/admin/api/v1/dashboard")
        
        # 未认证应该返回 401 或 302（重定向到登录页）
        assert response.status_code in [401, 302, 403], \
            f"Expected 401/302/403 for unauthenticated request, got {response.status_code}"


if __name__ == "__main__":
    if USE_INTEGRATION_TEST:
        print(f"Testing against: {ADMIN_BASE_URL}")
    else:
        print("Testing in unit test mode (using FastAPI TestClient)")
    pytest.main([__file__, "-v", "--html=../api-test-report.html", "--self-contained-html"])

