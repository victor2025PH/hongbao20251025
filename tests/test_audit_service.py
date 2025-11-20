"""
测试 web_admin/services/audit_service.py
审计服务层测试
"""
import pytest
from datetime import datetime, UTC
from web_admin.services.audit_service import (
    AuditEntry,
    clear_audit_entries,
    record_audit,
    list_audit_entries,
    audit_as_json,
)


def test_audit_entry_dataclass():
    """测试 AuditEntry 数据类"""
    entry = AuditEntry(
        seq=1,
        action="test_action",
        operator=10001,
        timestamp=datetime.now(UTC),
        payload={"key": "value"},
    )
    assert entry.seq == 1
    assert entry.action == "test_action"
    assert entry.operator == 10001
    assert isinstance(entry.timestamp, datetime)
    assert entry.payload == {"key": "value"}


def test_clear_audit_entries():
    """测试 clear_audit_entries 函数"""
    # 先记录一些条目
    record_audit("test_action", 10001, {"test": "data"})
    record_audit("test_action2", 10002, {"test2": "data2"})
    
    # 清空
    clear_audit_entries()
    
    # 验证已清空
    entries = list_audit_entries()
    assert len(entries) == 0


def test_record_audit_success():
    """测试 record_audit - 成功记录"""
    clear_audit_entries()
    
    # 记录审计条目
    result = record_audit("export_all", 10001, {"status": "success"})
    assert result is True
    
    # 验证已记录
    entries = list_audit_entries()
    assert len(entries) == 1
    assert entries[0].action == "export_all"
    assert entries[0].operator == 10001
    assert entries[0].payload == {"status": "success"}


def test_record_audit_invalid_operator():
    """测试 record_audit - 无效的操作者"""
    clear_audit_entries()
    
    # 测试无效操作者（<= 0）
    result = record_audit("test_action", 0)
    assert result is False
    
    result = record_audit("test_action", -1)
    assert result is False
    
    # 验证未记录
    entries = list_audit_entries()
    assert len(entries) == 0


def test_record_audit_duplicate():
    """测试 record_audit - 重复记录"""
    clear_audit_entries()
    
    # 记录第一次
    result1 = record_audit("test_action", 10001, {"key": "value"})
    assert result1 is True
    
    # 尝试记录相同的条目（应该失败）
    result2 = record_audit("test_action", 10001, {"key": "value"})
    assert result2 is False
    
    # 验证只有一条记录
    entries = list_audit_entries()
    assert len(entries) == 1


def test_record_audit_different_payload():
    """测试 record_audit - 不同 payload"""
    clear_audit_entries()
    
    # 记录第一条
    result1 = record_audit("test_action", 10001, {"key": "value1"})
    assert result1 is True
    
    # 记录不同 payload（应该成功）
    result2 = record_audit("test_action", 10001, {"key": "value2"})
    assert result2 is True
    
    # 验证有两条记录
    entries = list_audit_entries()
    assert len(entries) == 2


def test_list_audit_entries_all():
    """测试 list_audit_entries - 列出所有条目"""
    clear_audit_entries()
    
    # 记录多条
    record_audit("action1", 10001, {"test": "1"})
    record_audit("action2", 10002, {"test": "2"})
    record_audit("action3", 10003, {"test": "3"})
    
    # 列出所有
    entries = list_audit_entries()
    assert len(entries) == 3


def test_list_audit_entries_filter_by_action():
    """测试 list_audit_entries - 按 action 筛选"""
    clear_audit_entries()
    
    # 记录多条
    record_audit("export_all", 10001, {})
    record_audit("export_users", 10002, {})
    record_audit("export_all", 10003, {})
    
    # 筛选特定 action
    entries = list_audit_entries(action="export_all")
    assert len(entries) == 2
    assert all(e.action == "export_all" for e in entries)


def test_list_audit_entries_filter_by_operator():
    """测试 list_audit_entries - 按 operator 筛选"""
    clear_audit_entries()
    
    # 记录多条
    record_audit("action1", 10001, {})
    record_audit("action2", 10001, {})
    record_audit("action3", 10002, {})
    
    # 筛选特定 operator
    entries = list_audit_entries(operator=10001)
    assert len(entries) == 2
    assert all(e.operator == 10001 for e in entries)


def test_list_audit_entries_reverse():
    """测试 list_audit_entries - 反向排序"""
    clear_audit_entries()
    
    # 记录多条
    record_audit("action1", 10001, {})
    record_audit("action2", 10002, {})
    record_audit("action3", 10003, {})
    
    # 正常排序
    entries_normal = list_audit_entries(reverse=False)
    # 反向排序
    entries_reverse = list_audit_entries(reverse=True)
    
    assert len(entries_normal) == 3
    assert len(entries_reverse) == 3
    # 验证顺序相反
    assert entries_normal[0].seq == entries_reverse[-1].seq


def test_audit_as_json():
    """测试 audit_as_json 函数"""
    clear_audit_entries()
    
    # 记录一些条目
    record_audit("export_all", 10001, {"status": "success"})
    record_audit("export_users", 10002, {"count": 10})
    
    # 获取 JSON
    json_str = audit_as_json()
    assert isinstance(json_str, str)
    assert "export_all" in json_str
    assert "export_users" in json_str
    assert "10001" in json_str
    assert "10002" in json_str


def test_audit_as_json_empty():
    """测试 audit_as_json - 空列表"""
    clear_audit_entries()
    
    # 获取 JSON（应该为空数组）
    json_str = audit_as_json()
    assert json_str == "[]"


def test_record_audit_without_payload():
    """测试 record_audit - 不带 payload"""
    clear_audit_entries()
    
    # 记录不带 payload 的条目
    result = record_audit("test_action", 10001)
    assert result is True
    
    # 验证已记录
    entries = list_audit_entries()
    assert len(entries) == 1
    assert entries[0].payload == {}

