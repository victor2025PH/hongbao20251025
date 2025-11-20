#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试所有服务的健康检查端点
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
from typing import Dict, List

SERVICES = [
    {
        "name": "Web Admin",
        "url": "http://localhost:8001/healthz",
        "port": 8001,
        "endpoints": [
            "http://localhost:8001/healthz",
            "http://localhost:8001/readyz",
            "http://localhost:8001/metrics",
        ]
    },
    {
        "name": "MiniApp API",
        "url": "http://localhost:8080/healthz",
        "port": 8080,
        "endpoints": [
            "http://localhost:8080/healthz",
        ]
    }
]


def test_service(service: Dict) -> Dict:
    """测试单个服务"""
    result = {
        "name": service["name"],
        "port": service["port"],
        "status": "未启动",
        "health_check": "失败",
        "endpoints": []
    }
    
    try:
        # 测试健康检查
        response = requests.get(service["url"], timeout=5)
        if response.status_code == 200:
            result["status"] = "运行中"
            result["health_check"] = "通过"
            result["response"] = response.text[:100]  # 只取前100字符
        else:
            result["status"] = "运行中"
            result["health_check"] = f"失败 (状态码: {response.status_code})"
    except requests.exceptions.ConnectionError:
        result["status"] = "未启动"
        result["health_check"] = "连接失败"
    except requests.exceptions.Timeout:
        result["status"] = "运行中"
        result["health_check"] = "超时"
    except Exception as e:
        result["status"] = "未知"
        result["health_check"] = f"错误: {str(e)}"
    
    # 测试其他端点
    for endpoint in service.get("endpoints", []):
        try:
            resp = requests.get(endpoint, timeout=3)
            result["endpoints"].append({
                "url": endpoint,
                "status": resp.status_code,
                "ok": resp.status_code == 200
            })
        except:
            result["endpoints"].append({
                "url": endpoint,
                "status": "失败",
                "ok": False
            })
    
    return result


def main():
    print("=" * 50)
    print("测试所有服务")
    print("=" * 50)
    print()
    
    results = []
    for service in SERVICES:
        print(f"测试 {service['name']} (端口 {service['port']})...")
        result = test_service(service)
        results.append(result)
        
        # 显示结果
        status_icon = "[OK]" if result["health_check"] == "通过" else "[FAIL]"
        print(f"  {status_icon} 状态: {result['status']}")
        print(f"  {status_icon} 健康检查: {result['health_check']}")
        if "response" in result:
            print(f"    响应: {result['response']}")
        print()
    
    # 显示摘要
    print("=" * 50)
    print("测试结果摘要")
    print("=" * 50)
    for result in results:
        status_icon = "[OK]" if result["health_check"] == "通过" else "[FAIL]"
        print(f"{status_icon} {result['name']}: {result['status']} (端口 {result['port']}) - {result['health_check']}")
    
    print()
    print("=" * 50)
    print("服务端点")
    print("=" * 50)
    print("Web Admin:")
    print("  - 健康检查: http://localhost:8001/healthz")
    print("  - 就绪检查: http://localhost:8001/readyz")
    print("  - 指标:     http://localhost:8001/metrics")
    print("  - Dashboard: http://localhost:8001/admin/dashboard")
    print()
    print("MiniApp API:")
    print("  - 健康检查: http://localhost:8080/healthz")
    print("  - 公开群组: http://localhost:8080/v1/groups/public")
    print()
    
    # 返回退出码
    all_ok = all(r["health_check"] == "通过" for r in results)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

