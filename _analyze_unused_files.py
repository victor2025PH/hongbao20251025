#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析项目中的无用文件
"""
import os
import re
from pathlib import Path
from typing import Set, Dict, List, Tuple

# 排除的目录
EXCLUDE_DIRS = {
    '.git', '.github', '.idea', '.vscode', '.pytest_cache', '.mypy_cache',
    '.cache', '.turbo', '.venv', 'node_modules', 'dist', 'build', 'out',
    '.next', '.sass-cache', '__pycache__', 'exports', 'backups', 'static',
    'docs/api-testing/output', '无用文件'
}

# 程序文件扩展名
CODE_EXTENSIONS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.sh', '.ps1', '.bat'}

# 入口文件（不应移动）
ENTRY_FILES = {
    'app.py', 'web_admin/main.py', 'miniapp/main.py',
    'start.sh', 'Dockerfile', 'Dockerfile.backend',
    'docker-compose.yml', 'docker-compose.production.yml',
    'docker-compose.override.yml.example',
    'requirements.txt', 'pytest.ini', 'Makefile'
}

# 入口脚本（保留）
ENTRY_SCRIPTS = {
    'docs/deployment/deploy-local.ps1',
    'docs/deployment/deploy-production.ps1',
    'docs/deployment/dev-start-all.ps1',
    'docs/api-testing/run-full-stack-tests.ps1',
    'docs/api-testing/run-comprehensive-test-improved.ps1',
    'ops/health_watchdog.py',
    'scripts/activity_report_cron.py',
    'scripts/self_check.py'
}

def should_exclude(path: Path) -> bool:
    """检查路径是否应排除"""
    parts = path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    if path.name.endswith('.pyc'):
        return True
    if path.name.startswith('~$'):
        return True
    return False

def find_code_files(root: Path) -> Set[Path]:
    """查找所有程序文件"""
    files = set()
    for ext in CODE_EXTENSIONS:
        for f in root.rglob(f'*{ext}'):
            if not should_exclude(f):
                files.add(f)
    return files

def extract_imports(file_path: Path) -> Set[str]:
    """提取文件中的导入"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Python imports
            for pattern in [
                r'from\s+([\w.]+)\s+import',
                r'import\s+([\w.]+)',
            ]:
                for match in re.finditer(pattern, content):
                    imports.add(match.group(1).split('.')[0])
            
            # PowerShell/Script references
            if file_path.suffix in {'.ps1', '.sh', '.bat'}:
                # 查找相对路径引用
                for pattern in [
                    r'\.\\([\w\-\u4e00-\u9fff]+\.(?:ps1|sh|py))',
                    r'\./([\w\-\u4e00-\u9fff]+\.(?:ps1|sh|py))',
                    r'Invoke-Expression\s+["\']([^"\']+\.(?:ps1|sh|py))',
                    r'pwsh\s+["\']?([^"\']+\.(?:ps1|sh|py))',
                    r'bash\s+["\']?([^"\']+\.(?:ps1|sh|py))',
                    r'python\s+["\']?([^"\']+\.(?:ps1|sh|py))',
                ]:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        imports.add(match.group(1))
                
                # 查找路径拼接中的文件名
                for pattern in [
                    r'Join-Path[^"]+["\']([\w\-\u4e00-\u9fff]+\.(?:ps1|sh|py))',
                    r'[\'"]([\w\-\u4e00-\u9fff]+\.(?:ps1|sh|py))["\']',
                ]:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        imports.add(match.group(1))
            
            # 查找文件名引用（不含扩展名）
            base_name = file_path.stem
            if base_name and base_name not in {'__init__', '__main__'}:
                imports.add(base_name)
                
    except Exception as e:
        pass
    return imports

def check_file_usage(root: Path, target_file: Path, all_files: Set[Path]) -> Tuple[bool, List[str]]:
    """检查文件是否被使用"""
    reasons = []
    target_name = target_file.name
    target_stem = target_file.stem
    target_relative = str(target_file.relative_to(root))
    
    # 检查是否为入口文件
    if target_name in ENTRY_FILES:
        return True, ['入口文件']
    
    if target_relative in ENTRY_SCRIPTS:
        return True, ['入口脚本']
    
    # 检查是否在 Dockerfile 或 compose 文件中被引用
    for compose_file in ['docker-compose.yml', 'docker-compose.production.yml', 'Dockerfile', 'Dockerfile.backend']:
        compose_path = root / compose_file
        if compose_path.exists():
            try:
                content = compose_path.read_text(encoding='utf-8', errors='ignore')
                if target_name in content or target_relative in content:
                    return True, [f'被 {compose_file} 引用']
            except:
                pass
    
    # 检查是否在其他文件中被导入或引用
    referenced_by = []
    for other_file in all_files:
        if other_file == target_file:
            continue
        
        try:
            content = other_file.read_text(encoding='utf-8', errors='ignore')
            
            # 检查模块名引用
            if target_stem in content:
                # 避免误匹配
                if target_name in content or f'/{target_name}' in content or f'\\{target_name}' in content:
                    referenced_by.append(str(other_file.relative_to(root)))
                elif f'from {target_stem}' in content or f'import {target_stem}' in content:
                    referenced_by.append(str(other_file.relative_to(root)))
        
        except:
            pass
    
    if referenced_by:
        return True, [f'被引用: {", ".join(referenced_by[:3])}']
    
    return False, []

def analyze_unused_files(root: Path) -> Dict[str, List[Tuple[Path, List[str]]]]:
    """分析无用文件"""
    all_files = find_code_files(root)
    unused = {'unused': [], 'maybe_unused': []}
    
    for file_path in sorted(all_files):
        relative_path = str(file_path.relative_to(root))
        
        # 跳过入口文件和重要脚本
        if file_path.name in ENTRY_FILES or relative_path in ENTRY_SCRIPTS:
            continue
        
        is_used, reasons = check_file_usage(root, file_path, all_files)
        
        if not is_used:
            # 进一步判断是否可能是无用文件
            if file_path.suffix == '.ps1' and ('test' in file_path.stem.lower() or 'comprehensive' in file_path.stem.lower()):
                # 检查是否是旧版测试脚本
                if 'improved' not in file_path.stem.lower():
                    unused['unused'].append((file_path, ['可能是旧版测试脚本']))
                    continue
            
            if 'fix' in file_path.stem.lower() or '修复' in str(file_path) or '诊断' in str(file_path):
                unused['maybe_unused'].append((file_path, ['一次性修复/诊断脚本']))
                continue
            
            if 'deploy' in file_path.stem.lower() or '部署' in str(file_path):
                # 检查是否在部署文档或脚本中被引用
                unused['maybe_unused'].append((file_path, ['可能是旧版部署脚本']))
                continue
            
            unused['maybe_unused'].append((file_path, reasons if reasons else ['未发现引用']))
    
    return unused

if __name__ == '__main__':
    root = Path('.')
    print(f"分析项目根目录: {root.absolute()}")
    print()
    
    unused = analyze_unused_files(root)
    
    print("=" * 80)
    print("确定无用的文件（建议移动）:")
    print("=" * 80)
    for file_path, reasons in unused['unused']:
        print(f"  - {file_path.relative_to(root)}")
        for reason in reasons:
            print(f"    原因: {reason}")
    print()
    
    print("=" * 80)
    print("可能无用的文件（需要人工确认）:")
    print("=" * 80)
    for file_path, reasons in unused['maybe_unused'][:30]:  # 限制输出数量
        print(f"  - {file_path.relative_to(root)}")
        for reason in reasons:
            print(f"    原因: {reason}")
    print(f"\n... 还有 {len(unused['maybe_unused']) - 30} 个文件待确认")

