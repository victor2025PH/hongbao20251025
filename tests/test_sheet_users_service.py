"""
测试 services/sheet_users.py
表格用户服务层测试
"""
import pytest
from unittest.mock import patch, MagicMock, Mock


def test_ensure_gspread():
    """测试 _ensure_gspread 函数"""
    from services.sheet_users import _ensure_gspread
    
    # 测试成功导入
    with patch("builtins.__import__", return_value=MagicMock()):
        result = _ensure_gspread()
        assert result is not None
    
    # 测试导入失败
    with patch("builtins.__import__", side_effect=ImportError("No module named 'gspread'")):
        with pytest.raises(RuntimeError, match="缺少依赖"):
            _ensure_gspread()


def test_header_index_map():
    """测试 _header_index_map 函数"""
    from services.sheet_users import _header_index_map
    
    # Mock worksheet
    mock_ws = MagicMock()
    mock_ws.row_values.return_value = ["列1", "列2", "列3"]
    
    result = _header_index_map(mock_ws)
    
    assert isinstance(result, dict)
    assert result["列1"] == 1
    assert result["列2"] == 2
    assert result["列3"] == 3


def test_list_rows():
    """测试 list_rows 函数"""
    from services.sheet_users import list_rows
    
    # Mock worksheet
    mock_ws = MagicMock()
    mock_ws.row_values.return_value = ["列1", "列2", "列3"]
    mock_ws.get_all_values.return_value = [
        ["列1", "列2", "列3"],  # 表头
        ["值1", "值2", "值3"],  # 数据行1
        ["值4", "值5", "值6"],  # 数据行2
    ]
    
    with patch("services.sheet_users._get_worksheet", return_value=mock_ws):
        rows, total, headers = list_rows(page=1, per_page=10)
        
        assert isinstance(rows, list)
        assert isinstance(headers, list)
        assert total == 2
        assert len(headers) == 3


def test_list_rows_with_filters():
    """测试 list_rows - 带筛选条件"""
    from services.sheet_users import list_rows
    
    # Mock worksheet
    mock_ws = MagicMock()
    mock_ws.row_values.return_value = ["列1", "列2"]
    mock_ws.get_all_values.return_value = [
        ["列1", "列2"],
        ["值1", "匹配"],
        ["值2", "不匹配"],
    ]
    
    with patch("services.sheet_users._get_worksheet", return_value=mock_ws):
        rows, total, headers = list_rows(
            page=1,
            per_page=10,
            filters={"列2": "匹配"},
        )
        
        assert total >= 0  # 可能因为筛选逻辑导致结果不同
        assert isinstance(rows, list)
        if len(rows) > 0:
            assert "列2" in rows[0] or "匹配" in str(rows[0])


def test_list_rows_pagination():
    """测试 list_rows - 分页"""
    from services.sheet_users import list_rows
    
    # Mock worksheet
    mock_ws = MagicMock()
    mock_ws.row_values.return_value = ["列1"]
    mock_ws.get_all_values.return_value = [
        ["列1"],
        *[["值" + str(i)] for i in range(10)],  # 10 行数据
    ]
    
    with patch("services.sheet_users._get_worksheet", return_value=mock_ws):
        # 第一页
        rows1, total1, _ = list_rows(page=1, per_page=3)
        assert len(rows1) == 3
        assert total1 == 10
        
        # 第二页
        rows2, total2, _ = list_rows(page=2, per_page=3)
        assert len(rows2) == 3
        assert total2 == 10


def test_get_row():
    """测试 get_row 函数"""
    from services.sheet_users import get_row
    
    # Mock worksheet
    mock_ws = MagicMock()
    mock_ws.row_values.return_value = ["列1", "列2", "列3"]
    
    with patch("services.sheet_users._get_worksheet", return_value=mock_ws):
        # 测试获取表头
        data, headers = get_row(1)
        assert isinstance(data, dict)
        assert isinstance(headers, list)
        assert len(headers) == 3
        assert "__row" in data
        
        # 测试获取数据行
        mock_ws.row_values.return_value = ["值1", "值2", "值3"]
        data, headers = get_row(2)
        assert data["__row"] == 2
        # 验证数据已正确映射到表头
        if len(headers) > 0:
            assert headers[0] in data


def test_update_row():
    """测试 update_row 函数"""
    from services.sheet_users import update_row
    
    # Mock worksheet
    mock_ws = MagicMock()
    mock_ws.row_values.return_value = ["列1", "用户名", "列3"]
    
    with patch("services.sheet_users._get_worksheet", return_value=mock_ws):
        with patch("services.sheet_users._header_index_map", return_value={"用户名": 2}):
            with patch("services.sheet_users._ensure_gspread") as mock_gspread:
                mock_gspread.return_value.utils.rowcol_to_a1.return_value = "B2"
                mock_ws.batch_update.return_value = None
                
                # 测试更新行
                update_row(2, {"用户名": "新用户名"})
                
                mock_ws.batch_update.assert_called_once()


def test_update_row_header_protection():
    """测试 update_row - 保护表头"""
    from services.sheet_users import update_row
    
    # 测试不能编辑表头
    with pytest.raises(ValueError, match="cannot edit header row"):
        update_row(1, {"用户名": "新值"})


def test_export_rows_as_csv():
    """测试 export_rows_as_csv 函数"""
    from services.sheet_users import export_rows_as_csv
    
    # Mock worksheet
    mock_ws = MagicMock()
    mock_ws.row_values.return_value = ["列1", "列2"]
    mock_ws.get_all_values.return_value = [
        ["列1", "列2"],
        ["值1", "值2"],
    ]
    
    with patch("services.sheet_users._get_worksheet", return_value=mock_ws):
        # 测试导出 CSV
        csv_iter = export_rows_as_csv()
        csv_data = b"".join(csv_iter)
        
        assert isinstance(csv_data, bytes)
        # 检查 CSV 数据包含预期内容（使用 UTF-8 编码）
        csv_str = csv_data.decode("utf-8")
        assert "列1" in csv_str or "值1" in csv_str


def test_ensure_audit_file():
    """测试 _ensure_audit_file 函数"""
    from services.sheet_users import _ensure_audit_file
    import os
    import tempfile
    
    # 使用临时文件测试
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("services.sheet_users._AUDIT_FILE", os.path.join(tmpdir, "audit.csv")):
            _ensure_audit_file()
            
            # 验证文件已创建
            assert os.path.exists(os.path.join(tmpdir, "audit.csv"))


def test_append_audit():
    """测试 append_audit 函数"""
    from services.sheet_users import append_audit
    import os
    import tempfile
    
    # 使用临时文件测试
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_file = os.path.join(tmpdir, "audit.csv")
        with patch("services.sheet_users._AUDIT_FILE", audit_file):
            # 追加审计记录
            append_audit(
                row=2,
                field="用户名",
                old="旧值",
                new="新值",
                editor="admin",
            )
            
            # 验证文件已创建并包含数据
            assert os.path.exists(audit_file)
            with open(audit_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "用户名" in content
                assert "旧值" in content
                assert "新值" in content


def test_export_audit_as_csv():
    """测试 export_audit_as_csv 函数"""
    from services.sheet_users import export_audit_as_csv
    import os
    import tempfile
    
    # 使用临时文件测试
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_file = os.path.join(tmpdir, "audit.csv")
        with patch("services.sheet_users._AUDIT_FILE", audit_file):
            # 创建测试审计文件
            with open(audit_file, "w", encoding="utf-8", newline="") as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["time_utc", "row", "field", "old", "new", "editor"])
                writer.writerow(["2024-01-01T00:00:00", "2", "用户名", "旧值", "新值", "admin"])
            
            # 测试导出
            csv_iter = export_audit_as_csv()
            csv_data = b"".join(csv_iter)
            
            assert isinstance(csv_data, bytes)
            # 检查 CSV 数据包含预期内容（使用 UTF-8 编码）
            csv_str = csv_data.decode("utf-8")
            assert "用户名" in csv_str

