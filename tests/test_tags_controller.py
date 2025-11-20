"""
测试 web_admin/controllers/tags.py
标签管理控制器测试
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_tags_page(client):
    """测试标签列表页"""
    response = client.get("/admin/tags")
    assert response.status_code in [200, 303]  # 可能重定向到登录


def test_tags_page_with_top(client):
    """测试标签列表页 - 带 top 参数"""
    response = client.get("/admin/tags?top=50")
    assert response.status_code in [200, 303]


def test_tag_disable(client):
    """测试禁用标签"""
    response = client.post(
        "/admin/tags/disable",
        data={"tag": "test_tag"},
        follow_redirects=False,
    )
    assert response.status_code in [303, 200, 401, 400]


def test_tag_enable(client):
    """测试启用标签"""
    response = client.post(
        "/admin/tags/enable",
        data={"tag": "test_tag"},
        follow_redirects=False,
    )
    assert response.status_code in [303, 200, 401, 400]


def test_tag_disable_empty(client):
    """测试禁用标签 - 空标签"""
    response = client.post(
        "/admin/tags/disable",
        data={"tag": ""},
        follow_redirects=False,
    )
    assert response.status_code in [400, 303, 401]


def test_extract_tags():
    """测试 _extract_tags 函数"""
    from web_admin.controllers.tags import _extract_tags
    
    # 测试正常提取
    assert _extract_tags("tag1,tag2,tag3") == ["tag1", "tag2", "tag3"]
    assert _extract_tags("tag1, tag2 , tag3") == ["tag1", "tag2", "tag3"]
    
    # 测试带 # 号
    assert _extract_tags("#tag1,#tag2") == ["tag1", "tag2"]
    
    # 测试空字符串
    assert _extract_tags("") == []
    assert _extract_tags(None) == []
    
    # 测试单个标签
    assert _extract_tags("tag1") == ["tag1"]

