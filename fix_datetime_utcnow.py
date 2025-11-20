#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量修复 datetime.now(UTC) 弃用警告
将所有 datetime.now(UTC) 替换为 datetime.now(UTC)
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

def fix_file(file_path: Path) -> tuple[bool, int]:
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # 检查是否需要添加 UTC 导入
        needs_utc_import = 'datetime.now(UTC)' in content
        has_utc_import = 'from datetime import' in content and 'UTC' in content
        has_datetime_import = 'from datetime import' in content or 'import datetime' in content
        
        if not needs_utc_import:
            return False, 0
        
        # 替换 datetime.now(UTC) 为 datetime.now(UTC)
        count = len(re.findall(r'datetime\.utcnow\(\)', content))
        content = re.sub(r'datetime\.utcnow\(\)', 'datetime.now(UTC)', content)
        
        # 如果需要，添加 UTC 导入
        if not has_utc_import and has_datetime_import:
            # 查找 datetime 导入行
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if re.match(r'^from datetime import', line):
                    # 如果已经有 datetime 导入，添加 UTC
                    if 'UTC' not in line:
                        lines[i] = line.rstrip() + ', UTC'
                    break
                elif re.match(r'^import datetime', line):
                    # 如果是 import datetime，改为 from datetime import datetime, UTC
                    lines[i] = 'from datetime import datetime, UTC'
                    # 需要替换所有 datetime.datetime 为 datetime
                    content = '\n'.join(lines)
                    content = re.sub(r'datetime\.datetime\.', 'datetime.', content)
                    lines = content.split('\n')
                    break
            
            content = '\n'.join(lines)
        
        # 如果内容有变化，写入文件
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True, count
        
        return False, 0
        
    except Exception as e:
        print(f"  [ERROR] 修复失败: {e}")
        return False, 0

def main():
    print("=" * 60)
    print("批量修复 datetime.now(UTC) 弃用警告")
    print("=" * 60)
    print()
    
    # 查找所有 Python 文件
    exclude_dirs = {'__pycache__', '.git', 'node_modules', '.next', 'venv', 'env', '.venv', 'dist', 'build'}
    python_files = []
    
    for root, dirs, files in os.walk('.'):
        # 排除目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                # 排除文档和报告文件
                if 'test_report' not in str(file_path) and '开发建议' not in str(file_path) and '执行清单' not in str(file_path):
                    python_files.append(file_path)
    
    print(f"找到 {len(python_files)} 个 Python 文件")
    print()
    
    fixed_files = []
    total_replacements = 0
    
    for file_path in python_files:
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            if 'datetime.now(UTC)' in content:
                print(f"修复 {file_path}...")
                fixed, count = fix_file(file_path)
                if fixed:
                    fixed_files.append((file_path, count))
                    total_replacements += count
                    print(f"  [OK] 修复了 {count} 处")
                else:
                    print(f"  [SKIP] 无需修复")
        except Exception as e:
            print(f"  [ERROR] {file_path}: {e}")
        print()
    
    print("=" * 60)
    print("修复完成")
    print("=" * 60)
    print(f"修复文件数: {len(fixed_files)}")
    print(f"总替换数: {total_replacements}")
    print()
    
    if fixed_files:
        print("修复的文件:")
        for file_path, count in fixed_files:
            print(f"  - {file_path}: {count} 处")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

