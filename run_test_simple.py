#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版全自动测试（快速启动）
"""
import sys
import os
import io

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import subprocess
import time
import requests
from pathlib import Path

def main():
    print("=" * 60)
    print("简化版全自动测试")
    print("=" * 60)
    print()
    
    # 1. 自动修复
    print("[1/4] 自动修复常见错误...")
    try:
        result = subprocess.run([sys.executable, "auto_fix_common_errors.py"], 
                              capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"修复过程出错: {e}")
    print()
    
    # 2. 初始化数据库
    print("[2/4] 初始化数据库...")
    try:
        from models.db import init_db
        init_db()
        print("[OK] 数据库初始化成功")
    except Exception as e:
        print(f"[WARN] 数据库初始化失败: {e}")
    print()
    
    # 3. 启动服务
    print("[3/4] 启动服务...")
    print("注意: 服务需要在单独的终端中启动")
    print()
    print("请在新终端中执行:")
    print("  终端 1: python -m uvicorn web_admin.main:app --host 0.0.0.0 --port 8001 --reload")
    print("  终端 2: python -m uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --reload")
    print()
    input("服务启动后，按 Enter 继续...")
    print()
    
    # 4. 测试服务
    print("[4/4] 测试服务...")
    time.sleep(3)
    
    services = [
        ("Web Admin", 8001, "http://localhost:8001/healthz"),
        ("MiniApp API", 8080, "http://localhost:8080/healthz"),
    ]
    
    all_ok = True
    for name, port, url in services:
        print(f"测试 {name} (端口 {port})...")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  [OK] {name} 健康检查通过")
            else:
                print(f"  [FAIL] {name} 返回状态码: {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"  [FAIL] {name} 连接失败: {e}")
            all_ok = False
        print()
    
    # 显示结果
    print("=" * 60)
    if all_ok:
        print("所有服务测试通过！" -ForegroundColor Green)
    else:
        print("部分服务测试失败，请检查服务是否正常启动")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

