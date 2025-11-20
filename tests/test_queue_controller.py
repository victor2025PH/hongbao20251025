"""
测试 web_admin/controllers/queue.py
队列管理控制器测试
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pathlib import Path


def test_queue_page(client):
    """测试队列列表页"""
    response = client.get("/admin/queue")
    assert response.status_code in [200, 303]  # 可能重定向到登录


def test_queue_enqueue_all_users_ledger(client):
    """测试入队 - 全部用户和账本"""
    response = client.post(
        "/admin/queue/enqueue",
        data={"kind": "ALL_USERS_LEDGER"},
        follow_redirects=False,
    )
    assert response.status_code in [303, 200, 401]  # 可能重定向或需要认证


def test_queue_enqueue_users_only(client):
    """测试入队 - 仅用户"""
    response = client.post(
        "/admin/queue/enqueue",
        data={"kind": "USERS_ONLY"},
        follow_redirects=False,
    )
    assert response.status_code in [303, 200, 401]


def test_queue_enqueue_ledger_only(client):
    """测试入队 - 仅账本"""
    response = client.post(
        "/admin/queue/enqueue",
        data={"kind": "LEDGER_ONLY"},
        follow_redirects=False,
    )
    assert response.status_code in [303, 200, 401]


def test_queue_enqueue_selected_merged(client):
    """测试入队 - 选中用户合并"""
    response = client.post(
        "/admin/queue/enqueue",
        data={"kind": "SELECTED_MERGED", "users": "10001,10002"},
        follow_redirects=False,
    )
    assert response.status_code in [303, 200, 401, 400]


def test_queue_enqueue_invalid_kind(client):
    """测试入队 - 无效类型"""
    response = client.post(
        "/admin/queue/enqueue",
        data={"kind": "INVALID"},
        follow_redirects=False,
    )
    assert response.status_code in [400, 303, 401]


def test_queue_status(client):
    """测试队列状态查询"""
    response = client.get("/admin/queue/status?id=1")
    assert response.status_code in [200, 404, 401]


def test_queue_download(client):
    """测试队列下载"""
    response = client.get("/admin/queue/download/1")
    assert response.status_code in [200, 404, 400, 401]


def test_split_users():
    """测试 _split_users 函数"""
    from web_admin.controllers.queue import _split_users
    
    # 测试正常分割
    assert _split_users("10001,10002,10003") == ["10001", "10002", "10003"]
    assert _split_users("10001\n10002\n10003") == ["10001", "10002", "10003"]
    assert _split_users("10001\t10002\t10003") == ["10001", "10002", "10003"]
    
    # 测试空字符串
    assert _split_users("") == []
    assert _split_users("   ") == []
    
    # 测试带空格
    assert _split_users("10001, 10002 , 10003") == ["10001", "10002", "10003"]

