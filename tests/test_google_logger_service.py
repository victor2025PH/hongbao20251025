"""
测试 services/google_logger.py
Google 日志服务层测试
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timezone
from aiogram.types import User, Chat


def test_resolve_credential_file():
    """测试 _resolve_credential_file 函数"""
    from services.google_logger import _resolve_credential_file
    from pathlib import Path
    
    # 测试环境变量优先
    with patch.dict("os.environ", {"GOOGLE_SERVICE_ACCOUNT_PATH": "/test/path.json"}):
        result = _resolve_credential_file()
        assert result == "/test/path.json"
    
    # 测试默认路径（需要 mock Path.exists）
    with patch.dict("os.environ", {}, clear=True):
        with patch.object(Path, "exists", return_value=False):
            result = _resolve_credential_file()
            assert isinstance(result, str)
            assert len(result) > 0


def test_utc_now_iso():
    """测试 _utc_now_iso 函数"""
    from services.google_logger import _utc_now_iso
    
    result = _utc_now_iso()
    assert isinstance(result, str)
    assert "T" in result
    assert "Z" in result


def test_to_yes_no():
    """测试 _to_yes_no 函数"""
    from services.google_logger import _to_yes_no
    
    assert _to_yes_no(True) == "是"
    assert _to_yes_no(False) == "否"


def test_header_index_map():
    """测试 _header_index_map 函数"""
    from services.google_logger import _header_index_map
    
    # Mock worksheet
    mock_ws = MagicMock()
    mock_ws.row_values.return_value = ["列1", "列2", "列3"]
    
    result = _header_index_map(mock_ws)
    
    assert isinstance(result, dict)
    assert result["列1"] == 1
    assert result["列2"] == 2
    assert result["列3"] == 3


def test_build_row():
    """测试 _build_row 函数"""
    from services.google_logger import _build_row
    
    # 创建模拟用户和聊天
    mock_user = MagicMock(spec=User)
    mock_user.id = 10001
    mock_user.username = "testuser"
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.language_code = "zh"
    mock_user.is_bot = False
    
    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = -1001234567890
    mock_chat.title = "Test Chat"
    mock_chat.type = "supergroup"
    
    # 测试构建行
    row = _build_row(
        user=mock_user,
        source="test_source",
        chat=mock_chat,
        inviter_user_id=10002,
        joined_via_invite_link=True,
        note="Test note",
    )
    
    assert isinstance(row, list)
    assert len(row) > 0
    assert str(10001) in str(row)  # 用户ID应该在行中


def test_append_with_retry():
    """测试 _append_with_retry 函数"""
    from services.google_logger import _append_with_retry
    
    # Mock worksheet
    mock_ws = MagicMock()
    mock_ws.append_row.return_value = None
    
    # 测试成功追加
    result = _append_with_retry(mock_ws, ["row", "data"], retries=3)
    assert result is True
    mock_ws.append_row.assert_called_once()


def test_append_with_retry_failure():
    """测试 _append_with_retry - 失败重试"""
    from services.google_logger import _append_with_retry
    
    # Mock worksheet（第一次失败，第二次成功）
    mock_ws = MagicMock()
    # 创建一个通用异常（不依赖 gspread）
    class MockException(Exception):
        pass
    mock_ws.append_row.side_effect = [MockException("Rate limit"), None]
    
    # 测试重试
    with patch("time.sleep"):  # Mock sleep 以加快测试
        result = _append_with_retry(mock_ws, ["row", "data"], retries=3)
        assert result is True
        assert mock_ws.append_row.call_count == 2


def test_log_user_to_sheet():
    """测试 log_user_to_sheet 函数"""
    from services.google_logger import log_user_to_sheet
    
    # 创建模拟用户和聊天
    mock_user = MagicMock(spec=User)
    mock_user.id = 10001
    mock_user.username = "testuser"
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.language_code = "zh"
    mock_user.is_bot = False
    
    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = -1001234567890
    mock_chat.title = "Test Chat"
    mock_chat.type = "supergroup"
    
    # Mock 所有依赖
    with patch("services.google_logger._get_worksheet") as mock_get_ws:
        with patch("services.google_logger._header_index_map") as mock_idx_map:
            with patch("services.google_logger._ensure_cache_fresh"):
                with patch("services.google_logger.mark_member_logged_once", return_value=True):
                    with patch("services.google_logger._append_with_retry", return_value=True):
                        mock_ws = MagicMock()
                        mock_get_ws.return_value = mock_ws
                        mock_idx_map.return_value = {}
                        
                        # 测试记录用户
                        result = log_user_to_sheet(
                            user=mock_user,
                            source="test_source",
                            chat=mock_chat,
                        )
                        # 应该返回 True 或 False（取决于幂等检查）
                        assert isinstance(result, bool)


def test_log_user_to_sheet_idempotent():
    """测试 log_user_to_sheet - 幂等性"""
    from services.google_logger import log_user_to_sheet
    
    # 创建模拟用户
    mock_user = MagicMock(spec=User)
    mock_user.id = 10001
    mock_user.username = "testuser"
    
    # Mock 幂等检查返回 False（已记录过）
    with patch("services.google_logger.mark_member_logged_once", return_value=False):
        result = log_user_to_sheet(
            user=mock_user,
            source="member_join",
        )
        # 如果已记录过，应该返回 False
        assert result is False

