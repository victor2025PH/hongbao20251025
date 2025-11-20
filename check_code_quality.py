#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
代码质量检查脚本
"""
import sys
import os
import io
import subprocess
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

def check_pylint():
    """运行 pylint 检查"""
    print("=" * 60)
    print("运行 Pylint 代码检查")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pylint", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print("[INFO] Pylint 未安装，跳过检查")
            print("      安装命令: pip install pylint")
            return False
    except:
        print("[INFO] Pylint 未安装，跳过检查")
        print("      安装命令: pip install pylint")
        return False
    
    directories = ["web_admin", "miniapp", "services", "models", "routers"]
    all_ok = True
    
    for directory in directories:
        if Path(directory).exists():
            print(f"检查 {directory}/...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pylint", directory, 
                     "--disable=all", "--enable=E,W", "--max-line-length=120"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"  [OK] {directory} 检查通过")
                else:
                    print(f"  [WARN] {directory} 发现问题:")
                    # 只显示前10个问题
                    lines = result.stdout.split('\n')[:10]
                    for line in lines:
                        if line.strip():
                            print(f"    {line}")
                    all_ok = False
            except Exception as e:
                print(f"  [ERROR] {directory} 检查失败: {e}")
                all_ok = False
            print()
    
    return all_ok

def check_test_coverage():
    """检查测试覆盖率"""
    print("=" * 60)
    print("检查测试覆盖率")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print("[INFO] Pytest 未安装，跳过覆盖率检查")
            return False
    except:
        print("[INFO] Pytest 未安装，跳过覆盖率检查")
        return False
    
    print("运行测试并生成覆盖率报告...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", 
             "--cov=web_admin", "--cov=miniapp", "--cov=services", "--cov=models",
             "--cov-report=term", "--cov-report=html",
             "-v", "--tb=short", "--maxfail=5"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300
        )
        
        # 显示覆盖率摘要
        output = result.stdout
        if "TOTAL" in output:
            # 提取覆盖率信息
            lines = output.split('\n')
            for line in lines:
                if "TOTAL" in line or "覆盖率" in line or "coverage" in line.lower():
                    print(f"  {line}")
        
        if result.returncode == 0:
            print("\n[OK] 测试通过，覆盖率报告已生成: htmlcov/index.html")
            return True
        else:
            print("\n[WARN] 部分测试失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] 测试超时")
        return False
    except Exception as e:
        print(f"[ERROR] 覆盖率检查失败: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("代码质量检查")
    print("=" * 60)
    print()
    
    results = {}
    
    # 1. Pylint 检查
    results['pylint'] = check_pylint()
    print()
    
    # 2. 测试覆盖率
    results['coverage'] = check_test_coverage()
    print()
    
    # 总结
    print("=" * 60)
    print("检查结果")
    print("=" * 60)
    print(f"Pylint 检查: {'通过' if results.get('pylint', False) else '跳过或有问题'}")
    print(f"测试覆盖率: {'完成' if results.get('coverage', False) else '跳过或失败'}")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

