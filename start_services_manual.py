#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动启动服务脚本（用于测试）
"""
import sys
import os
import io
import subprocess
import time

# 修复编码
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def start_web_admin():
    """启动 Web Admin"""
    print("启动 Web Admin (端口 8001)...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "web_admin.main:app", "--host", "0.0.0.0", "--port", "8001"],
            stdout=open("web_admin.log", "w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            env=os.environ.copy()
        )
        print(f"[OK] Web Admin 已启动 (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"[FAIL] Web Admin 启动失败: {e}")
        return None

def start_miniapp():
    """启动 MiniApp API"""
    print("启动 MiniApp API (端口 8080)...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "miniapp.main:app", "--host", "0.0.0.0", "--port", "8080"],
            stdout=open("miniapp.log", "w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            env=os.environ.copy()
        )
        print(f"[OK] MiniApp API 已启动 (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"[FAIL] MiniApp API 启动失败: {e}")
        return None

def main():
    print("=" * 60)
    print("手动启动服务")
    print("=" * 60)
    print()
    
    # 初始化数据库
    print("初始化数据库...")
    try:
        from models.db import init_db
        init_db()
        print("[OK] 数据库初始化成功")
    except Exception as e:
        print(f"[WARN] 数据库初始化失败: {e}")
    print()
    
    # 启动服务
    processes = []
    
    web_admin = start_web_admin()
    if web_admin:
        processes.append(("Web Admin", web_admin))
    print()
    
    time.sleep(2)
    
    miniapp = start_miniapp()
    if miniapp:
        processes.append(("MiniApp API", miniapp))
    print()
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(10)
    
    # 测试服务
    print("\n测试服务健康状态...")
    import requests
    
    for name, process in processes:
        port = 8001 if "Web Admin" in name else 8080
        url = f"http://localhost:{port}/healthz"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[OK] {name} 健康检查通过")
            else:
                print(f"[FAIL] {name} 返回状态码: {response.status_code}")
        except Exception as e:
            print(f"[WARN] {name} 尚未就绪: {e}")
    
    print("\n" + "=" * 60)
    print("服务启动完成！")
    print("=" * 60)
    print("\n服务端点:")
    print("  Web Admin:   http://localhost:8001")
    print("  MiniApp API: http://localhost:8080")
    print("\n日志文件:")
    print("  web_admin.log")
    print("  miniapp.log")
    print("\n按 Ctrl+C 停止服务")
    
    try:
        # 保持运行
        while True:
            time.sleep(1)
            # 检查进程是否还在运行
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n[WARN] {name} 已停止 (退出码: {process.returncode})")
    except KeyboardInterrupt:
        print("\n\n正在停止服务...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"[OK] {name} 已停止")
            except:
                try:
                    process.kill()
                except:
                    pass

if __name__ == "__main__":
    main()

