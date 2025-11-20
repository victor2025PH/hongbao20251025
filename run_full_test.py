#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整全自动测试运行脚本
- 检查服务状态
- 运行所有测试
- 生成完整报告
"""
import sys
import os
import io
import subprocess
import time
import requests
import json
from pathlib import Path
from datetime import datetime

# 修复编码
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_services():
    """检查服务状态"""
    print("=" * 60)
    print("检查服务状态")
    print("=" * 60)
    print()
    
    services = [
        ("Web Admin", 8001, "http://localhost:8001/healthz"),
        ("MiniApp API", 8080, "http://localhost:8080/healthz"),
    ]
    
    results = []
    all_ok = True
    
    for name, port, url in services:
        print(f"检查 {name} (端口 {port})...")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  [OK] {name} 运行正常")
                results.append({
                    'service': name,
                    'port': port,
                    'status': 'running',
                    'health_check': 'passed',
                    'response': response.text[:100]
                })
            else:
                print(f"  [FAIL] {name} 返回状态码: {response.status_code}")
                results.append({
                    'service': name,
                    'port': port,
                    'status': 'error',
                    'health_check': 'failed',
                    'error': f"状态码: {response.status_code}"
                })
                all_ok = False
        except Exception as e:
            print(f"  [FAIL] {name} 连接失败: {e}")
            results.append({
                'service': name,
                'port': port,
                'status': 'not_running',
                'health_check': 'failed',
                'error': str(e)
            })
            all_ok = False
        print()
    
    return all_ok, results

def run_tests():
    """运行测试套件"""
    print("=" * 60)
    print("运行测试套件")
    print("=" * 60)
    print()
    
    test_files = [
        "tests/test_regression_features.py",
        "tests/test_public_group_service.py",
        "tests/test_api_public_groups.py",
    ]
    
    results = []
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"运行 {test_file}...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=180
                )
                
                # 解析测试结果
                output = result.stdout
                if "passed" in output:
                    passed = len([l for l in output.split('\n') if 'PASSED' in l or 'passed' in l])
                    failed = len([l for l in output.split('\n') if 'FAILED' in l or 'failed' in l])
                    total_passed += passed
                    total_failed += failed
                
                if result.returncode == 0:
                    print(f"  [OK] {test_file} 测试通过")
                    results.append({
                        'file': test_file,
                        'status': 'passed',
                        'output': output[-500:]  # 最后500字符
                    })
                else:
                    print(f"  [FAIL] {test_file} 测试失败")
                    results.append({
                        'file': test_file,
                        'status': 'failed',
                        'output': output[-500:],
                        'error': result.stderr[-200:] if result.stderr else None
                    })
            except subprocess.TimeoutExpired:
                print(f"  [TIMEOUT] {test_file} 测试超时")
                results.append({
                    'file': test_file,
                    'status': 'timeout'
                })
            except Exception as e:
                print(f"  [ERROR] {test_file} 测试出错: {e}")
                results.append({
                    'file': test_file,
                    'status': 'error',
                    'error': str(e)
                })
        else:
            print(f"  [SKIP] {test_file} 不存在")
            results.append({
                'file': test_file,
                'status': 'skipped',
                'reason': '文件不存在'
            })
        print()
    
    return results, total_passed, total_failed

def test_api_endpoints():
    """测试 API 端点"""
    print("=" * 60)
    print("测试 API 端点")
    print("=" * 60)
    print()
    
    endpoints = [
        ("Web Admin - Readyz", "http://localhost:8001/readyz"),
        ("Web Admin - Metrics", "http://localhost:8001/metrics"),
        ("MiniApp API - Groups", "http://localhost:8080/v1/groups/public"),
    ]
    
    results = []
    
    for name, url in endpoints:
        print(f"测试 {name}...")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 401]:  # 401 也算正常（需要认证）
                print(f"  [OK] {name} 响应正常 (状态码: {response.status_code})")
                results.append({
                    'endpoint': name,
                    'url': url,
                    'status': 'ok',
                    'status_code': response.status_code
                })
            else:
                print(f"  [WARN] {name} 返回状态码: {response.status_code}")
                results.append({
                    'endpoint': name,
                    'url': url,
                    'status': 'warning',
                    'status_code': response.status_code
                })
        except Exception as e:
            print(f"  [FAIL] {name} 请求失败: {e}")
            results.append({
                'endpoint': name,
                'url': url,
                'status': 'failed',
                'error': str(e)
            })
        print()
    
    return results

def generate_report(service_results, test_results, api_results, total_passed, total_failed):
    """生成测试报告"""
    print("=" * 60)
    print("生成测试报告")
    print("=" * 60)
    print()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'services_running': len([r for r in service_results if r['status'] == 'running']),
            'services_total': len(service_results),
            'tests_passed': total_passed,
            'tests_failed': total_failed,
            'api_endpoints_tested': len(api_results),
            'api_endpoints_ok': len([r for r in api_results if r['status'] == 'ok'])
        },
        'services': service_results,
        'tests': test_results,
        'api_endpoints': api_results
    }
    
    report_file = f"full_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] 测试报告已保存: {report_file}")
    print()
    
    # 显示摘要
    print("=" * 60)
    print("测试摘要")
    print("=" * 60)
    print(f"服务状态: {report['summary']['services_running']}/{report['summary']['services_total']} 运行中")
    print(f"测试结果: {total_passed} 通过, {total_failed} 失败")
    print(f"API 端点: {report['summary']['api_endpoints_ok']}/{report['summary']['api_endpoints_tested']} 正常")
    print()
    
    return report_file

def main():
    print("\n" + "=" * 60)
    print("完整全自动测试系统")
    print("=" * 60)
    print()
    
    try:
        # 1. 检查服务状态
        services_ok, service_results = check_services()
        
        if not services_ok:
            print("[WARN] 部分服务未运行，但继续执行测试...")
            print()
        
        # 2. 测试 API 端点
        api_results = test_api_endpoints()
        
        # 3. 运行测试套件
        test_results, total_passed, total_failed = run_tests()
        
        # 4. 生成报告
        report_file = generate_report(service_results, test_results, api_results, total_passed, total_failed)
        
        print("=" * 60)
        print("测试完成！")
        print("=" * 60)
        print(f"\n报告文件: {report_file}")
        print("\n服务端点:")
        print("  Web Admin:   http://localhost:8001")
        print("  MiniApp API: http://localhost:8080")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

