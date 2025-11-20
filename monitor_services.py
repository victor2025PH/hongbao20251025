#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实时监控服务日志和状态
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

import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class ServiceMonitor:
    def __init__(self):
        self.services = [
            {
                'name': 'Web Admin',
                'port': 8001,
                'log_file': 'web_admin.log',
                'health_url': 'http://localhost:8001/healthz'
            },
            {
                'name': 'MiniApp API',
                'port': 8080,
                'log_file': 'miniapp.log',
                'health_url': 'http://localhost:8080/healthz'
            }
        ]
        self.errors = []
        self.warnings = []
        
    def check_health(self, service: Dict) -> bool:
        """检查服务健康状态"""
        try:
            response = requests.get(service['health_url'], timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def monitor_log(self, log_file: str, service_name: str, last_position: int = 0):
        """监控日志文件"""
        log_path = Path(log_file)
        if not log_path.exists():
            return last_position
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                current_position = f.tell()
                
                for line in new_lines:
                    line_lower = line.lower().strip()
                    if not line_lower:
                        continue
                    
                    # 检测错误
                    if any(keyword in line_lower for keyword in ['error', 'exception', 'traceback', 'failed']):
                        if 'error' not in line_lower or 'warning' not in line_lower:
                            self.errors.append({
                                'service': service_name,
                                'time': datetime.now().strftime("%H:%M:%S"),
                                'message': line.strip()[:200]
                            })
                            print(f"\n[ERROR] {service_name}: {line.strip()[:100]}")
                    
                    # 检测警告
                    elif 'warning' in line_lower or 'warn' in line_lower:
                        self.warnings.append({
                            'service': service_name,
                            'time': datetime.now().strftime("%H:%M:%S"),
                            'message': line.strip()[:200]
                        })
                        print(f"\n[WARN] {service_name}: {line.strip()[:100]}")
                
                return current_position
        except Exception as e:
            print(f"[ERROR] 读取日志失败 {log_file}: {e}")
            return last_position
    
    def auto_fix_error(self, error: Dict):
        """自动修复错误"""
        error_msg = error['message'].lower()
        service = error['service']
        
        # 数据库连接错误
        if 'database' in error_msg or 'sqlite' in error_msg:
            print(f"[FIX] 检测到数据库错误，尝试修复...")
            try:
                from models.db import init_db
                init_db()
                print(f"[OK] 数据库已重新初始化")
                return True
            except Exception as e:
                print(f"[FAIL] 数据库修复失败: {e}")
        
        # 导入错误
        if 'no module named' in error_msg or 'import' in error_msg:
            print(f"[FIX] 检测到导入错误，尝试安装缺失模块...")
            # 这里可以添加自动安装逻辑
            return False
        
        # 端口占用
        if 'address already in use' in error_msg or 'port' in error_msg:
            print(f"[FIX] 检测到端口占用，请手动处理")
            return False
        
        return False
    
    def run(self, duration: int = 300):
        """运行监控"""
        print("=" * 60)
        print("服务监控系统")
        print("=" * 60)
        print(f"监控时长: {duration} 秒")
        print("按 Ctrl+C 停止监控\n")
        
        log_positions = {s['log_file']: 0 for s in self.services}
        start_time = time.time()
        check_interval = 5  # 每5秒检查一次
        last_health_check = 0
        
        try:
            while time.time() - start_time < duration:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # 每10秒检查一次健康状态
                if time.time() - last_health_check >= 10:
                    print(f"\n[{current_time}] 健康检查:")
                    for service in self.services:
                        is_healthy = self.check_health(service)
                        status = "✓" if is_healthy else "✗"
                        print(f"  {status} {service['name']} (端口 {service['port']})")
                    last_health_check = time.time()
                    print()
                
                # 监控日志
                for service in self.services:
                    log_file = service['log_file']
                    log_positions[log_file] = self.monitor_log(
                        log_file,
                        service['name'],
                        log_positions[log_file]
                    )
                    
                    # 自动修复错误
                    if self.errors:
                        latest_error = self.errors[-1]
                        if latest_error['service'] == service['name']:
                            self.auto_fix_error(latest_error)
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n监控已停止")
        
        # 显示摘要
        print("\n" + "=" * 60)
        print("监控摘要")
        print("=" * 60)
        print(f"发现错误: {len(self.errors)}")
        print(f"发现警告: {len(self.warnings)}")
        
        if self.errors:
            print("\n最近的错误:")
            for error in self.errors[-5:]:
                print(f"  [{error['time']}] {error['service']}: {error['message'][:80]}")
        
        if self.warnings:
            print("\n最近的警告:")
            for warning in self.warnings[-5:]:
                print(f"  [{warning['time']}] {warning['service']}: {warning['message'][:80]}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='监控服务日志和状态')
    parser.add_argument('-d', '--duration', type=int, default=300, help='监控时长（秒）')
    args = parser.parse_args()
    
    monitor = ServiceMonitor()
    monitor.run(args.duration)

if __name__ == "__main__":
    main()

