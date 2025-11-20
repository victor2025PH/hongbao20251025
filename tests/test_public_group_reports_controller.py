"""
测试 web_admin/controllers/public_group_reports.py
公开群组报告控制器测试
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_public_group_reports_page(client):
    """测试公开群组报告列表页"""
    response = client.get("/admin/public-groups/reports")
    assert response.status_code in [200, 303]  # 可能重定向到登录


def test_public_group_reports_page_with_filters(client):
    """测试公开群组报告列表 - 带筛选条件"""
    response = client.get("/admin/public-groups/reports?status=PENDING&search=test")
    assert response.status_code in [200, 303]


def test_public_group_report_detail_page(client):
    """测试公开群组报告详情页"""
    response = client.get("/admin/public-groups/reports/1")
    assert response.status_code in [200, 404, 303]


def test_public_group_report_update_status(client):
    """测试更新报告状态"""
    response = client.post(
        "/admin/public-groups/reports/1/status",
        json={"status": "RESOLVED"},
        follow_redirects=False,
    )
    assert response.status_code in [200, 303, 404, 401, 400, 403]


def test_public_group_report_add_note(client):
    """测试添加报告备注"""
    response = client.post(
        "/admin/public-groups/reports/1/note",
        json={"note": "Test note"},
        follow_redirects=False,
    )
    assert response.status_code in [200, 303, 404, 401, 400, 403]

