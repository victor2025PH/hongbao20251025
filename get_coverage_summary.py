#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
获取测试覆盖率摘要
"""
import sys
import os
import io
import re
from pathlib import Path

# 修复编码
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def main():
    html_file = Path("htmlcov/index.html")
    if not html_file.exists():
        print("覆盖率报告文件不存在")
        return 1
    
    try:
        content = html_file.read_text(encoding='utf-8')
        # 查找覆盖率百分比
        match = re.search(r'<span class="pc_cov">(\d+)%</span>', content)
        if match:
            coverage = match.group(1)
            print(f"当前测试覆盖率: {coverage}%")
        else:
            print("无法从报告中提取覆盖率")
        
        # 统计测试文件
        test_files = list(Path("tests").glob("test_*.py"))
        print(f"测试文件数: {len(test_files)}")
        
        return 0
    except Exception as e:
        print(f"读取覆盖率报告失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

