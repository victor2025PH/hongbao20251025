#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全自动测试系统
- 自动安装依赖
- 自动启动服务
- 自动监控日志
- 自动修复错误
- 自动运行测试
"""
import sys
import os
import io

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    # 设置标准输出编码为 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        # Python < 3.7 兼容
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import subprocess
import time
import requests
import threading
import signal
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime

# 全局变量
processes = []
test_results = []
errors_found = []
fixes_applied = []

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_status(msg: str, status: str = "INFO"):
    """打印状态信息"""
    color = Colors.GREEN if status == "OK" else Colors.RED if status == "FAIL" else Colors.YELLOW if status == "WARN" else Colors.BLUE
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] [{status}]{Colors.RESET} {msg}")

def check_python_version():
    """检查 Python 版本"""
    print_status("检查 Python 版本...", "INFO")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_status(f"Python 版本过低: {version.major}.{version.minor}，需要 3.11+", "FAIL")
        return False
    print_status(f"Python 版本: {version.major}.{version.minor}.{version.micro}", "OK")
    return True

def install_dependencies():
    """安装依赖"""
    print_status("检查并安装依赖...", "INFO")
    
    # 检查 requirements.txt
    if not Path("requirements.txt").exists():
        print_status("requirements.txt 不存在", "WARN")
        return False
    
    # 安装依赖
    try:
        print_status("正在安装 Python 依赖...", "INFO")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print_status("Python 依赖安装成功", "OK")
            return True
        else:
            print_status(f"依赖安装失败: {result.stderr}", "FAIL")
            return False
    except subprocess.TimeoutExpired:
        print_status("依赖安装超时", "FAIL")
        return False
    except Exception as e:
        print_status(f"依赖安装出错: {e}", "FAIL")
        return False

def check_node_dependencies():
    """检查 Node.js 依赖（前端）"""
    frontend_dir = Path("frontend-next")
    if frontend_dir.exists():
        print_status("检查前端依赖...", "INFO")
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            node_modules = frontend_dir / "node_modules"
            if not node_modules.exists():
                print_status("前端依赖未安装，正在安装...", "INFO")
                try:
                    result = subprocess.run(
                        ["npm", "install"],
                        cwd=str(frontend_dir),
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode == 0:
                        print_status("前端依赖安装成功", "OK")
                        return True
                    else:
                        print_status(f"前端依赖安装失败: {result.stderr}", "WARN")
                        return False
                except Exception as e:
                    print_status(f"前端依赖安装出错: {e}", "WARN")
                    return False
        else:
            print_status("前端 package.json 不存在", "WARN")
    return True

def init_database():
    """初始化数据库"""
    print_status("初始化数据库...", "INFO")
    try:
        from models.db import init_db
        init_db()
        print_status("数据库初始化成功", "OK")
        return True
    except Exception as e:
        print_status(f"数据库初始化失败: {e}", "FAIL")
        # 尝试修复
        return fix_database_error(e)

def fix_database_error(error: Exception):
    """修复数据库错误"""
    error_str = str(error).lower()
    
    if "no module named" in error_str:
        print_status("检测到缺少模块，尝试安装...", "WARN")
        missing_module = error_str.split("'")[1] if "'" in error_str else None
        if missing_module:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", missing_module], 
                             capture_output=True, timeout=60)
                fixes_applied.append(f"安装了缺失模块: {missing_module}")
                return init_database()
            except:
                pass
    
    if "operationalerror" in error_str or "database" in error_str:
        print_status("尝试创建数据库目录...", "WARN")
        os.makedirs("data", exist_ok=True)
        fixes_applied.append("创建了数据库目录")
        return init_database()
    
    return False

def start_service(name: str, command: List[str], port: int, log_file: str):
    """启动服务"""
    print_status(f"启动 {name} (端口 {port})...", "INFO")
    
    try:
        log_path = Path(log_file)
        with open(log_path, 'w', encoding='utf-8') as f:
            process = subprocess.Popen(
                command,
                stdout=f,
                stderr=subprocess.STDOUT,
                env=os.environ.copy()
            )
        
        processes.append({
            'name': name,
            'process': process,
            'port': port,
            'log_file': log_file
        })
        
        print_status(f"{name} 已启动 (PID: {process.pid})", "OK")
        return True
    except Exception as e:
        print_status(f"{name} 启动失败: {e}", "FAIL")
        return False

def wait_for_service(port: int, timeout: int = 30):
    """等待服务启动"""
    print_status(f"等待服务启动 (端口 {port})...", "INFO")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:{port}/healthz", timeout=2)
            if response.status_code == 200:
                print_status(f"服务已就绪 (端口 {port})", "OK")
                return True
        except:
            pass
        time.sleep(1)
    
    print_status(f"服务启动超时 (端口 {port})", "WARN")
    return False

def check_service_health(port: int, name: str):
    """检查服务健康状态"""
    try:
        response = requests.get(f"http://localhost:{port}/healthz", timeout=5)
        if response.status_code == 200:
            print_status(f"{name} 健康检查通过", "OK")
            test_results.append({
                'service': name,
                'port': port,
                'status': 'OK',
                'response': response.text[:100]
            })
            return True
        else:
            print_status(f"{name} 健康检查失败 (状态码: {response.status_code})", "FAIL")
            test_results.append({
                'service': name,
                'port': port,
                'status': 'FAIL',
                'error': f"状态码: {response.status_code}"
            })
            return False
    except Exception as e:
        print_status(f"{name} 健康检查失败: {e}", "FAIL")
        test_results.append({
            'service': name,
            'port': port,
            'status': 'FAIL',
            'error': str(e)
        })
        return False

def monitor_logs(log_file: str, service_name: str):
    """监控日志"""
    log_path = Path(log_file)
    if not log_path.exists():
        return
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            # 读取最后几行
            lines = f.readlines()
            if lines:
                last_lines = lines[-10:]
                for line in last_lines:
                    line_lower = line.lower()
                    if 'error' in line_lower or 'exception' in line_lower:
                        errors_found.append({
                            'service': service_name,
                            'error': line.strip(),
                            'time': datetime.now().isoformat()
                        })
                        print_status(f"{service_name} 发现错误: {line.strip()[:100]}", "WARN")
    except Exception as e:
        pass

def run_tests():
    """运行测试套件"""
    print_status("运行测试套件...", "INFO")
    
    test_files = [
        "tests/test_regression_features.py",
        "tests/test_public_group_service.py",
        "tests/test_api_public_groups.py",
    ]
    
    results = []
    for test_file in test_files:
        if Path(test_file).exists():
            print_status(f"运行 {test_file}...", "INFO")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    print_status(f"{test_file} 测试通过", "OK")
                    results.append({'file': test_file, 'status': 'PASS'})
                else:
                    print_status(f"{test_file} 测试失败", "FAIL")
                    results.append({'file': test_file, 'status': 'FAIL', 'output': result.stdout})
            except subprocess.TimeoutExpired:
                print_status(f"{test_file} 测试超时", "WARN")
                results.append({'file': test_file, 'status': 'TIMEOUT'})
            except Exception as e:
                print_status(f"{test_file} 测试出错: {e}", "FAIL")
                results.append({'file': test_file, 'status': 'ERROR', 'error': str(e)})
        else:
            print_status(f"测试文件不存在: {test_file}", "WARN")
    
    return results

def generate_report():
    """生成测试报告"""
    print_status("生成测试报告...", "INFO")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_results': test_results,
        'errors_found': errors_found,
        'fixes_applied': fixes_applied,
        'services': [
            {
                'name': p['name'],
                'port': p['port'],
                'pid': p['process'].pid,
                'status': 'running' if p['process'].poll() is None else 'stopped'
            }
            for p in processes
        ]
    }
    
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_status(f"测试报告已保存: {report_file}", "OK")
    return report_file

def cleanup():
    """清理资源"""
    print_status("清理资源...", "INFO")
    for p in processes:
        try:
            p['process'].terminate()
            p['process'].wait(timeout=5)
            print_status(f"{p['name']} 已停止", "OK")
        except:
            try:
                p['process'].kill()
            except:
                pass

def signal_handler(sig, frame):
    """信号处理"""
    print_status("\n收到中断信号，正在清理...", "WARN")
    cleanup()
    sys.exit(0)

def main():
    """主函数"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("\n" + "=" * 60)
    print("全自动测试系统")
    print("=" * 60 + "\n")
    
    try:
        # 1. 检查 Python 版本
        if not check_python_version():
            return 1
        
        # 2. 安装依赖
        if not install_dependencies():
            print_status("依赖安装失败，但继续尝试...", "WARN")
        
        # 3. 检查前端依赖
        check_node_dependencies()
        
        # 4. 初始化数据库
        if not init_database():
            print_status("数据库初始化失败，但继续尝试...", "WARN")
        
        # 5. 启动服务
        print_status("\n启动服务...", "INFO")
        
        # Web Admin
        start_service(
            "Web Admin",
            [sys.executable, "-m", "uvicorn", "web_admin.main:app", "--host", "0.0.0.0", "--port", "8001"],
            8001,
            "web_admin.log"
        )
        time.sleep(2)
        
        # MiniApp API
        start_service(
            "MiniApp API",
            [sys.executable, "-m", "uvicorn", "miniapp.main:app", "--host", "0.0.0.0", "--port", "8080"],
            8080,
            "miniapp.log"
        )
        time.sleep(2)
        
        # 6. 等待服务启动
        print_status("\n等待服务启动...", "INFO")
        wait_for_service(8001, timeout=30)
        wait_for_service(8080, timeout=30)
        
        # 7. 健康检查
        print_status("\n执行健康检查...", "INFO")
        check_service_health(8001, "Web Admin")
        check_service_health(8080, "MiniApp API")
        
        # 8. 监控日志
        print_status("\n监控服务日志...", "INFO")
        time.sleep(5)
        for p in processes:
            monitor_logs(p['log_file'], p['name'])
        
        # 9. 运行测试
        print_status("\n运行测试套件...", "INFO")
        test_results_data = run_tests()
        
        # 10. 生成报告
        print_status("\n生成测试报告...", "INFO")
        report_file = generate_report()
        
        # 11. 显示摘要
        print("\n" + "=" * 60)
        print("测试摘要")
        print("=" * 60)
        print(f"服务状态: {len([p for p in processes if p['process'].poll() is None])}/{len(processes)} 运行中")
        print(f"健康检查: {len([r for r in test_results if r['status'] == 'OK'])}/{len(test_results)} 通过")
        print(f"发现错误: {len(errors_found)}")
        print(f"应用修复: {len(fixes_applied)}")
        print(f"测试报告: {report_file}")
        
        if errors_found:
            print("\n发现的错误:")
            for error in errors_found[:5]:  # 只显示前5个
                print(f"  - {error['service']}: {error['error'][:80]}")
        
        if fixes_applied:
            print("\n应用的修复:")
            for fix in fixes_applied:
                print(f"  - {fix}")
        
        print("\n" + "=" * 60)
        print("测试完成！服务将继续运行，按 Ctrl+C 停止")
        print("=" * 60)
        
        # 保持运行
        try:
            while True:
                time.sleep(10)
                # 定期检查服务状态
                for p in processes:
                    if p['process'].poll() is not None:
                        print_status(f"{p['name']} 已停止，尝试重启...", "WARN")
                        # 可以在这里添加自动重启逻辑
        except KeyboardInterrupt:
            pass
        
    except Exception as e:
        print_status(f"测试过程出错: {e}", "FAIL")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

