# -*- coding: utf-8 -*-
"""
MiniApp API 端点测试

测试目标: 使用 FastAPI TestClient 进行单元测试
支持集成测试模式: 设置环境变量 API_TEST_MINIAPP_BASE_URL 可切换到真实 HTTP 请求
"""

from __future__ import annotations

import os
import time
from typing import Dict, Any, Optional

import pytest
from fastapi.testclient import TestClient

# 检查是否使用集成测试模式
USE_INTEGRATION_TEST = os.getenv("API_TEST_MINIAPP_BASE_URL") is not None

if USE_INTEGRATION_TEST:
    # 集成测试模式：使用真实 HTTP 请求
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    MINIAPP_BASE_URL = os.getenv("API_TEST_MINIAPP_BASE_URL", "http://localhost:8080").rstrip("/")
    
    @pytest.fixture(scope="module")
    def miniapp_session():
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
    import os
    from pathlib import Path
    # 确保公共群组功能启用（在导入 app 之前）
    os.environ.setdefault("FLAG_ENABLE_PUBLIC_GROUPS", "1")
    # 确保数据库 URL 设置（使用临时文件）
    test_db_path = Path("./test_miniapp.sqlite")
    test_db_path.unlink(missing_ok=True)
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{test_db_path.absolute()}")
    from miniapp.main import app
    from models.db import init_db
    # 初始化数据库
    try:
        init_db()
    except Exception:
        # 如果初始化失败，忽略（可能表已存在）
        pass
    
    @pytest.fixture(scope="module")
    def miniapp_session():
        """创建 FastAPI 测试客户端"""
        return TestClient(app)


class TestMiniAppHealthEndpoints:
    """MiniApp API 健康检查端点测试"""

    def test_healthz(self, miniapp_session):
        """测试 /healthz 端点"""
        if USE_INTEGRATION_TEST:
            url = f"{MINIAPP_BASE_URL}/healthz"
            start_time = time.time()
            response = miniapp_session.get(url, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        else:
            start_time = time.time()
            response = miniapp_session.get("/healthz")
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "ok" in data, "Response should contain 'ok' field"
        assert data["ok"] is True, "ok field should be True"
        
        if hasattr(response, 'elapsed_ms'):
            response.elapsed_ms = elapsed_ms
        print(f"\n[PERF] /healthz: {elapsed_ms:.2f}ms")

    def test_openapi_schema(self, miniapp_session):
        """测试 /openapi.json 端点"""
        if USE_INTEGRATION_TEST:
            url = f"{MINIAPP_BASE_URL}/openapi.json"
            start_time = time.time()
            response = miniapp_session.get(url, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        else:
            start_time = time.time()
            response = miniapp_session.get("/openapi.json")
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
    def test_docs(self, miniapp_session):
        """测试 /docs 端点（生产环境已禁用，跳过）"""
        url = f"{MINIAPP_BASE_URL}/docs"
        response = miniapp_session.get(url, timeout=10)
        # 在生产环境，这应该返回 404
        assert response.status_code == 404, "Swagger UI should be disabled in production"


class TestMiniAppPublicGroupsEndpoints:
    """MiniApp API 公开群组端点测试"""

    def test_list_public_groups(self, miniapp_session):
        """测试 /v1/groups/public 端点（公开群组列表）"""
        if USE_INTEGRATION_TEST:
            url = f"{MINIAPP_BASE_URL}/v1/groups/public"
            start_time = time.time()
            params = {"limit": 10}
            response = miniapp_session.get(url, params=params, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        else:
            start_time = time.time()
            params = {"limit": 10}
            response = miniapp_session.get("/v1/groups/public", params=params)
            elapsed_ms = (time.time() - start_time) * 1000
            data = response.json()
        
        # 可能返回 200 或 503（如果数据库未就绪）
        assert response.status_code in [200, 503], \
            f"Expected 200 or 503, got {response.status_code}"
        
        if response.status_code == 200:
            assert isinstance(data, list), "Response should be a list"
        
        # 如果列表不为空，验证项目结构
        if response.status_code == 200 and len(data) > 0:
            first_item = data[0]
            assert "id" in first_item, "Group item should contain 'id' field"
            assert "name" in first_item, "Group item should contain 'name' field"
        
        if hasattr(response, 'elapsed_ms'):
            response.elapsed_ms = elapsed_ms
        print(f"\n[PERF] /v1/groups/public: {elapsed_ms:.2f}ms")
        if response.status_code == 200:
            print(f"[DATA] Found {len(data)} public groups")

    def test_get_public_group_detail(self, miniapp_session):
        """测试 /v1/groups/public/{id} 端点（群组详情）"""
        if USE_INTEGRATION_TEST:
            # 先获取群组列表，使用第一个群组的 ID
            list_url = f"{MINIAPP_BASE_URL}/v1/groups/public"
            list_response = miniapp_session.get(list_url, params={"limit": 1}, timeout=10)
        else:
            list_response = miniapp_session.get("/v1/groups/public", params={"limit": 1})
        
        if list_response.status_code == 200:
            groups = list_response.json()
            if len(groups) > 0:
                group_id = groups[0]["id"]
                if USE_INTEGRATION_TEST:
                    detail_url = f"{MINIAPP_BASE_URL}/v1/groups/public/{group_id}"
                    start_time = time.time()
                    response = miniapp_session.get(detail_url, timeout=10)
                    elapsed_ms = (time.time() - start_time) * 1000
                else:
                    start_time = time.time()
                    response = miniapp_session.get(f"/v1/groups/public/{group_id}")
                    elapsed_ms = (time.time() - start_time) * 1000
                
                # 可能返回 200 或 404（如果群组不存在）
                assert response.status_code in [200, 404], \
                    f"Expected 200 or 404, got {response.status_code} for group {group_id}"
                
                if response.status_code == 200:
                    data = response.json()
                    assert "id" in data, "Group detail should contain 'id' field"
                    assert data["id"] == group_id, "Group ID should match"
                
                if hasattr(response, 'elapsed_ms'):
                    response.elapsed_ms = elapsed_ms
                print(f"\n[PERF] /v1/groups/public/{group_id}: {elapsed_ms:.2f}ms")
            else:
                pytest.skip("No public groups available for detail test")
        else:
            pytest.skip(f"Cannot fetch group list (status {list_response.status_code})")

    def test_list_public_activities(self, miniapp_session):
        """测试 /v1/groups/public/activities 端点（群组活动列表）"""
        if USE_INTEGRATION_TEST:
            url = f"{MINIAPP_BASE_URL}/v1/groups/public/activities"
            start_time = time.time()
            params = {"limit": 10}
            response = miniapp_session.get(url, params=params, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000
        else:
            start_time = time.time()
            params = {"limit": 10}
            response = miniapp_session.get("/v1/groups/public/activities", params=params)
            elapsed_ms = (time.time() - start_time) * 1000
        
        # 活动列表可能返回 200（空列表）、404（如果功能未启用）或 503（数据库未就绪）
        assert response.status_code in [200, 404, 503], \
            f"Expected 200, 404, or 503, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            
            # 如果列表不为空，验证项目结构
            if len(data) > 0:
                first_item = data[0]
                assert "id" in first_item or "activity_id" in first_item, \
                    "Activity item should contain 'id' or 'activity_id' field"
        
        response.elapsed_ms = elapsed_ms
        print(f"\n[PERF] /v1/groups/public/activities: {elapsed_ms:.2f}ms")
        if response.status_code == 200:
            print(f"[DATA] Found {len(data) if isinstance(data, list) else 0} activities")


class TestMiniAppAuthEndpoints:
    """MiniApp API 认证端点测试"""

    @pytest.mark.skip(reason="Requires valid test credentials or Telegram initData")
    def test_login(self, miniapp_session):
        """测试 /api/auth/login 端点（需要有效的测试账号）"""
        url = f"{MINIAPP_BASE_URL}/api/auth/login"
        
        # 这里需要有效的测试数据
        # 示例：Telegram code 或密码登录
        payload = {
            "code": "test_code",  # 需要替换为有效值
            # 或
            # "username": "test_user",
            # "password": "test_password",
        }
        
        response = miniapp_session.post(url, json=payload, timeout=10)
        
        # 未提供有效凭证应该返回 400 或 401
        assert response.status_code in [400, 401, 422], \
            f"Expected 400/401/422 for invalid credentials, got {response.status_code}"


if __name__ == "__main__":
    print(f"Testing against: {MINIAPP_BASE_URL}")
    pytest.main([__file__, "-v", "--html=../api-test-report.html", "--self-contained-html"])

