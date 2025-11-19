#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动所有服务（后端、前端、Bot）并监控日志
自动识别错误并记录
"""
import sys
import os
import io
import subprocess
import time
import signal
import threading
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 确保在项目根目录
os.chdir(Path(__file__).parent.absolute())

class ServiceManager:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.log_files: Dict[str, Path] = {}
        self.error_log: List[Dict] = []
        self.warning_log: List[Dict] = []
        self.running = True
        
        # 服务配置
        self.services = {
            'web_admin': {
                'name': 'Web Admin',
                'command': [sys.executable, '-m', 'uvicorn', 'web_admin.main:app', '--host', '0.0.0.0', '--port', '8001'],
                'port': 8001,
                'health_url': 'http://localhost:8001/healthz',
                'log_file': Path('logs/web_admin.log'),
                'error_log_file': Path('logs/web_admin_error.log'),
            },
            'miniapp_api': {
                'name': 'MiniApp API',
                'command': [sys.executable, '-m', 'uvicorn', 'miniapp.main:app', '--host', '0.0.0.0', '--port', '8080'],
                'port': 8080,
                'health_url': 'http://localhost:8080/healthz',
                'log_file': Path('logs/miniapp.log'),
                'error_log_file': Path('logs/miniapp_error.log'),
            },
            'bot': {
                'name': 'Telegram Bot',
                'command': [sys.executable, 'app.py'],
                'port': None,
                'health_url': None,
                'log_file': Path('logs/bot.log'),
                'error_log_file': Path('logs/bot_error.log'),
            },
        }
        
        # 前端服务（需要检查是否安装 Node.js）
        self.frontend_services = {
            'frontend_next': {
                'name': 'Next.js Frontend',
                'dir': Path('frontend-next'),
                'command': ['npm', 'run', 'dev'],
                'port': 3001,
                'health_url': 'http://localhost:3001',
                'log_file': Path('logs/frontend_next.log'),
                'error_log_file': Path('logs/frontend_next_error.log'),
            },
            'miniapp_frontend': {
                'name': 'MiniApp Frontend',
                'dir': Path('miniapp-frontend'),
                'command': ['npm', 'run', 'dev'],
                'port': 5173,
                'health_url': 'http://localhost:5173',
                'log_file': Path('logs/miniapp_frontend.log'),
                'error_log_file': Path('logs/miniapp_frontend_error.log'),
            },
        }
        
        # 确保 logs 目录存在
        Path('logs').mkdir(exist_ok=True)
        
    def check_dependencies(self) -> bool:
        """检查依赖"""
        print("\n[1/6] 检查依赖...")
        
        # 检查 Python
        try:
            result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
            print(f"  ✓ Python: {result.stdout.strip()}")
        except Exception as e:
            print(f"  ✗ Python 检查失败: {e}")
            return False
        
        # 检查 Node.js（可选）
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            print(f"  ✓ Node.js: {result.stdout.strip()}")
        except:
            print(f"  ⚠ Node.js 未安装（前端服务将跳过）")
        
        # 检查数据库
        try:
            from models.db import init_db
            init_db()
            print(f"  ✓ 数据库初始化成功")
        except Exception as e:
            print(f"  ⚠ 数据库初始化失败: {e}")
        
        return True
    
    def check_ports(self):
        """检查端口占用"""
        print("\n[2/6] 检查端口占用...")
        
        import socket
        
        ports_to_check = [8001, 8080, 3001, 5173]
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"  ⚠ 端口 {port} 已被占用")
            else:
                print(f"  ✓ 端口 {port} 可用")
    
    def start_service(self, service_key: str, service_config: Dict) -> bool:
        """启动单个服务"""
        name = service_config['name']
        command = service_config['command']
        log_file = service_config['log_file']
        error_log_file = service_config['error_log_file']
        
        print(f"\n  启动 {name}...")
        print(f"    命令: {' '.join(command)}")
        
        try:
            # 确保日志目录存在
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 打开日志文件
            log_handle = open(log_file, 'w', encoding='utf-8')
            error_handle = open(error_log_file, 'w', encoding='utf-8')
            
            # 启动进程
            process = subprocess.Popen(
                command,
                stdout=log_handle,
                stderr=error_handle,
                cwd=service_config.get('dir', Path.cwd()),
                env=os.environ.copy(),
            )
            
            self.processes[service_key] = process
            self.log_files[service_key] = log_file
            
            print(f"    ✓ {name} 已启动 (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"    ✗ {name} 启动失败: {e}")
            return False
    
    def start_frontend_service(self, service_key: str, service_config: Dict) -> bool:
        """启动前端服务"""
        name = service_config['name']
        dir_path = service_config['dir']
        
        # 检查目录是否存在
        if not dir_path.exists():
            print(f"    ⚠ {name} 目录不存在，跳过")
            return False
        
        # 检查是否有 node_modules
        if not (dir_path / 'node_modules').exists():
            print(f"    ⚠ {name} 未安装依赖，尝试安装...")
            try:
                subprocess.run(['npm', 'install'], cwd=dir_path, check=True, timeout=120)
                print(f"    ✓ {name} 依赖安装成功")
            except Exception as e:
                print(f"    ✗ {name} 依赖安装失败: {e}")
                return False
        
        return self.start_service(service_key, service_config)
    
    def start_all_services(self):
        """启动所有服务"""
        print("\n[3/6] 启动后端服务...")
        
        # 启动后端服务
        for key, config in self.services.items():
            # Bot 服务需要检查 BOT_TOKEN
            if key == 'bot':
                bot_token = os.getenv('BOT_TOKEN', '')
                if not bot_token or bot_token == 'PLEASE_SET_BOT_TOKEN':
                    print(f"    ⚠ {config['name']} 需要 BOT_TOKEN，跳过")
                    continue
            
            self.start_service(key, config)
            time.sleep(2)  # 等待服务启动
        
        print("\n[4/6] 启动前端服务...")
        
        # 检查 Node.js
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            node_available = True
        except:
            node_available = False
            print("  ⚠ Node.js 未安装，跳过前端服务")
        
        if node_available:
            for key, config in self.frontend_services.items():
                self.start_frontend_service(key, config)
                time.sleep(2)
    
    def check_health(self, service_key: str, service_config: Dict) -> bool:
        """检查服务健康状态"""
        health_url = service_config.get('health_url')
        if not health_url:
            return True  # 没有健康检查 URL 的服务认为正常
        
        try:
            response = requests.get(health_url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def monitor_log(self, service_key: str, service_config: Dict, last_position: int = 0) -> int:
        """监控日志文件"""
        log_file = service_config['log_file']
        if not log_file.exists():
            return last_position
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                current_position = f.tell()
                
                for line in new_lines:
                    self.analyze_line(service_config['name'], line)
                
                return current_position
        except Exception as e:
            print(f"[ERROR] 读取日志失败 {log_file}: {e}")
            return last_position
    
    def analyze_line(self, service_name: str, line: str):
        """分析日志行，识别错误和警告"""
        line_lower = line.lower().strip()
        if not line_lower:
            return
        
        # 检测 JSON 格式的日志（结构化日志）
        if line.strip().startswith('{') and '"level"' in line_lower:
            try:
                import json
                log_data = json.loads(line.strip())
                log_level = log_data.get('level', '').lower()
                log_message = log_data.get('message', '')
                
                if log_level in ['error', 'critical', 'fatal']:
                    error_entry = {
                        'service': service_name,
                        'time': log_data.get('time', datetime.now().isoformat()),
                        'message': log_message[:500],
                        'type': 'error',
                        'level': log_level,
                    }
                    if log_data.get('exc_info'):
                        error_entry['traceback'] = str(log_data['exc_info'])[:1000]
                    self.error_log.append(error_entry)
                    print(f"\n[ERROR] {service_name}: {log_message[:150]}")
                elif log_level == 'warning':
                    warning_entry = {
                        'service': service_name,
                        'time': log_data.get('time', datetime.now().isoformat()),
                        'message': log_message[:500],
                        'type': 'warning',
                    }
                    self.warning_log.append(warning_entry)
                    print(f"\n[WARN] {service_name}: {log_message[:150]}")
                return
            except Exception:
                # 如果不是有效的 JSON，继续使用普通检测
                pass
        
        # 检测错误
        error_keywords = ['error', 'exception', 'traceback', 'failed', 'critical', 'fatal']
        if any(kw in line_lower for kw in error_keywords):
            if 'warning' not in line_lower:
                error_entry = {
                    'service': service_name,
                    'time': datetime.now().isoformat(),
                    'message': line.strip()[:500],
                    'type': 'error',
                }
                self.error_log.append(error_entry)
                print(f"\n[ERROR] {service_name}: {line.strip()[:150]}")
        
        # 检测警告
        elif 'warning' in line_lower or 'warn' in line_lower:
            warning_entry = {
                'service': service_name,
                'time': datetime.now().isoformat(),
                'message': line.strip()[:500],
                'type': 'warning',
            }
            self.warning_log.append(warning_entry)
            print(f"\n[WARN] {service_name}: {line.strip()[:150]}")
    
    def monitor_services(self, duration: int = 300):
        """监控服务"""
        print("\n[5/6] 开始监控服务...")
        print(f"  监控时长: {duration} 秒")
        print("  按 Ctrl+C 停止监控\n")
        
        log_positions = {key: 0 for key in self.services.keys()}
        log_positions.update({key: 0 for key in self.frontend_services.keys() if key in self.processes})
        
        start_time = time.time()
        last_health_check = 0
        
        try:
            while time.time() - start_time < duration and self.running:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # 每10秒检查一次健康状态
                if time.time() - last_health_check >= 10:
                    print(f"\n[{current_time}] 健康检查:")
                    for key, config in self.services.items():
                        if key in self.processes:
                            is_healthy = self.check_health(key, config)
                            status = "✓" if is_healthy else "✗"
                            process = self.processes[key]
                            process_status = "运行中" if process.poll() is None else "已停止"
                            print(f"  {status} {config['name']}: {process_status}")
                    
                    for key, config in self.frontend_services.items():
                        if key in self.processes:
                            is_healthy = self.check_health(key, config)
                            status = "✓" if is_healthy else "✗"
                            process = self.processes[key]
                            process_status = "运行中" if process.poll() is None else "已停止"
                            print(f"  {status} {config['name']}: {process_status}")
                    
                    last_health_check = time.time()
                    print()
                
                # 监控日志
                for key, config in self.services.items():
                    if key in self.processes:
                        log_positions[key] = self.monitor_log(key, config, log_positions[key])
                
                for key, config in self.frontend_services.items():
                    if key in self.processes:
                        log_positions[key] = self.monitor_log(key, config, log_positions[key])
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\n监控已停止")
        finally:
            self.running = False
    
    def save_error_report(self):
        """保存错误报告"""
        print("\n[6/6] 生成错误报告...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'errors': self.error_log,
            'warnings': self.warning_log,
            'summary': {
                'total_errors': len(self.error_log),
                'total_warnings': len(self.warning_log),
                'services': {}
            }
        }
        
        # 按服务统计
        for error in self.error_log:
            service = error['service']
            if service not in report['summary']['services']:
                report['summary']['services'][service] = {'errors': 0, 'warnings': 0}
            report['summary']['services'][service]['errors'] += 1
        
        for warning in self.warning_log:
            service = warning['service']
            if service not in report['summary']['services']:
                report['summary']['services'][service] = {'errors': 0, 'warnings': 0}
            report['summary']['services'][service]['warnings'] += 1
        
        # 保存 JSON 报告
        report_file = Path(f"logs/error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 错误报告已保存: {report_file}")
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("错误报告摘要")
        print("=" * 60)
        print(f"总错误数: {len(self.error_log)}")
        print(f"总警告数: {len(self.warning_log)}")
        
        if self.error_log:
            print("\n最近的错误:")
            for error in self.error_log[-10:]:
                print(f"  [{error['time']}] {error['service']}: {error['message'][:100]}")
        
        if self.warning_log:
            print("\n最近的警告:")
            for warning in self.warning_log[-10:]:
                print(f"  [{warning['time']}] {warning['service']}: {warning['message'][:100]}")
        
        return report
    
    def stop_all_services(self):
        """停止所有服务"""
        print("\n正在停止所有服务...")
        
        for key, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"  ✓ {key} 已停止")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"  ✓ {key} 已强制停止")
            except Exception as e:
                print(f"  ✗ {key} 停止失败: {e}")
    
    def run(self, monitor_duration: int = 300):
        """运行完整的启动和监控流程"""
        print("=" * 60)
        print("启动所有服务并监控日志")
        print("=" * 60)
        
        try:
            # 1. 检查依赖
            if not self.check_dependencies():
                print("\n✗ 依赖检查失败")
                return 1
            
            # 2. 检查端口
            self.check_ports()
            
            # 3. 启动服务
            self.start_all_services()
            
            # 4. 等待服务启动
            print("\n等待服务启动...")
            time.sleep(5)
            
            # 5. 监控服务
            self.monitor_services(monitor_duration)
            
            # 6. 生成报告
            report = self.save_error_report()
            
            return 0
            
        except KeyboardInterrupt:
            print("\n\n用户中断")
            return 1
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            self.stop_all_services()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='启动所有服务并监控日志')
    parser.add_argument('-d', '--duration', type=int, default=300, help='监控时长（秒），默认 300')
    args = parser.parse_args()
    
    manager = ServiceManager()
    sys.exit(manager.run(args.duration))


if __name__ == "__main__":
    main()

