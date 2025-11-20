#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动修复常见错误
"""
import os
import sys
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
from pathlib import Path

def fix_import_errors():
    """修复导入错误"""
    print("检查导入错误...")
    try:
        # 测试关键模块导入
        from models.db import init_db
        from web_admin.main import app
        from miniapp.main import app as miniapp_app
        print("[OK] 所有关键模块导入成功")
        return True
    except ImportError as e:
        error_msg = str(e)
        # 更智能的模块名提取
        missing_module = None
        if "No module named" in error_msg:
            # 提取模块名
            parts = error_msg.split("'")
            if len(parts) >= 2:
                missing_module = parts[1]
        elif "'" in error_msg:
            missing_module = error_msg.split("'")[1]
        
        # 过滤掉明显不是模块名的内容
        if missing_module and missing_module.isidentifier() and not missing_module.isupper():
            print(f"[FIX] 检测到缺少模块: {missing_module}，正在安装...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", missing_module], 
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"[OK] {missing_module} 安装成功")
                    return True
                else:
                    print(f"[FAIL] {missing_module} 安装失败: {result.stderr[:100]}")
            except Exception as ex:
                print(f"[FAIL] {missing_module} 安装出错: {ex}")
        else:
            # 如果无法确定模块名，尝试安装 requirements.txt
            print("[WARN] 无法确定缺失模块，尝试安装所有依赖...")
            try:
                if Path("requirements.txt").exists():
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                                 timeout=120)
                    print("[OK] 依赖安装完成，请重试")
            except:
                pass
        return False

def fix_database_path():
    """修复数据库路径问题"""
    print("检查数据库路径...")
    data_dir = Path("data")
    if not data_dir.exists():
        print("[FIX] 创建数据目录...")
        data_dir.mkdir(exist_ok=True)
        print("[OK] 数据目录已创建")
    
    # 检查数据库文件权限
    db_file = Path("data.sqlite")
    if db_file.exists():
        try:
            # 测试数据库连接
            from models.db import engine
            with engine.connect() as conn:
                pass
            print("[OK] 数据库连接正常")
            return True
        except Exception as e:
            print(f"[WARN] 数据库连接问题: {e}")
    return True

def fix_port_conflicts():
    """修复端口冲突"""
    print("检查端口占用...")
    import socket
    
    ports = [8001, 8080]
    conflicts = []
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result == 0:
            conflicts.append(port)
    
    if conflicts:
        print(f"[WARN] 端口被占用: {conflicts}")
        print("[INFO] 请手动停止占用端口的进程，或修改配置使用其他端口")
        return False
    else:
        print("[OK] 端口可用")
        return True

def fix_env_file():
    """修复环境变量文件"""
    print("检查环境变量文件...")
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("[FIX] 从 .env.example 创建 .env 文件...")
            import shutil
            shutil.copy(env_example, env_file)
            print("[OK] .env 文件已创建，请根据需要修改配置")
        else:
            print("[WARN] .env 和 .env.example 都不存在")
            # 创建基本的 .env 文件
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("# 基本配置\n")
                f.write("DATABASE_URL=sqlite:///./data.sqlite\n")
                f.write("FLAG_ENABLE_PUBLIC_GROUPS=1\n")
            print("[OK] 已创建基本 .env 文件")
        return True
    else:
        print("[OK] .env 文件存在")
        return True

def fix_logging_config():
    """修复日志配置"""
    print("检查日志配置...")
    log_dir = Path("logs")
    if not log_dir.exists():
        print("[FIX] 创建日志目录...")
        log_dir.mkdir(exist_ok=True)
        print("[OK] 日志目录已创建")
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("自动修复常见错误")
    print("=" * 50)
    print()
    
    fixes = [
        ("环境变量文件", fix_env_file),
        ("导入错误", fix_import_errors),
        ("数据库路径", fix_database_path),
        ("端口冲突", fix_port_conflicts),
        ("日志配置", fix_logging_config),
    ]
    
    results = []
    for name, fix_func in fixes:
        try:
            result = fix_func()
            results.append((name, result))
            print()
        except Exception as e:
            print(f"[FAIL] {name} 修复失败: {e}\n")
            results.append((name, False))
    
    print("=" * 50)
    print("修复结果")
    print("=" * 50)
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    all_ok = all(r for _, r in results)
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

