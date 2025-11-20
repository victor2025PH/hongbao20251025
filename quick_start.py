#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速启动和测试脚本
"""
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_env():
    """检查环境配置"""
    print("=" * 50)
    print("检查环境配置")
    print("=" * 50)
    
    # 检查 .env 文件
    if Path(".env").exists():
        print("[OK] .env 文件存在")
    else:
        print("[WARN] .env 文件不存在，将使用默认配置")
    
    # 检查数据库
    try:
        from models.db import init_db
        init_db()
        print("[OK] 数据库初始化成功")
    except Exception as e:
        print(f"[FAIL] 数据库初始化失败: {e}")
        return False
    
    return True

def start_services():
    """启动服务"""
    print("\n" + "=" * 50)
    print("启动服务")
    print("=" * 50)
    print("\n注意: 服务需要在单独的终端中启动")
    print("\n请在新终端中执行以下命令:\n")
    print("终端 1 - Web Admin:")
    print("  python -m uvicorn web_admin.main:app --host 0.0.0.0 --port 8001 --reload")
    print("\n终端 2 - MiniApp API:")
    print("  python -m uvicorn miniapp.main:app --host 0.0.0.0 --port 8080 --reload")
    print("\n启动后，按 Enter 继续测试...")
    input()

def test_services():
    """测试服务"""
    print("\n" + "=" * 50)
    print("测试服务")
    print("=" * 50)
    
    services = [
        {"name": "Web Admin", "url": "http://localhost:8001/healthz"},
        {"name": "MiniApp API", "url": "http://localhost:8080/healthz"},
    ]
    
    all_ok = True
    for service in services:
        print(f"\n测试 {service['name']}...")
        try:
            response = requests.get(service['url'], timeout=5)
            if response.status_code == 200:
                print(f"  [OK] {service['name']} 健康检查通过")
                print(f"  响应: {response.text[:100]}")
            else:
                print(f"  [FAIL] {service['name']} 返回状态码: {response.status_code}")
                all_ok = False
        except requests.exceptions.ConnectionError:
            print(f"  [FAIL] {service['name']} 连接失败，请确保服务已启动")
            all_ok = False
        except Exception as e:
            print(f"  [FAIL] {service['name']} 测试失败: {e}")
            all_ok = False
    
    return all_ok

def run_tests():
    """运行回归测试"""
    print("\n" + "=" * 50)
    print("运行回归测试")
    print("=" * 50)
    
    test_files = [
        "tests/test_regression_features.py",
        "tests/test_public_group_service.py",
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n运行 {test_file}...")
            result = subprocess.run(
                ["pytest", test_file, "-v"],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.returncode != 0:
                print(result.stderr)
        else:
            print(f"[WARN] 测试文件不存在: {test_file}")

def main():
    print("\n" + "=" * 50)
    print("快速启动和测试")
    print("=" * 50)
    
    # 1. 检查环境
    if not check_env():
        print("\n环境检查失败，请修复后重试")
        return 1
    
    # 2. 提示启动服务
    start_services()
    
    # 3. 测试服务
    if not test_services():
        print("\n服务测试失败，请检查服务是否正常启动")
        return 1
    
    # 4. 运行测试
    print("\n是否运行回归测试? (y/n): ", end="")
    if input().lower() == 'y':
        run_tests()
    
    print("\n" + "=" * 50)
    print("完成！")
    print("=" * 50)
    print("\n服务端点:")
    print("  Web Admin:   http://localhost:8001")
    print("  MiniApp API: http://localhost:8080")
    print("\n健康检查:")
    print("  http://localhost:8001/healthz")
    print("  http://localhost:8080/healthz")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

