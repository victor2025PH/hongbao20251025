#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Stack Test Report Generator
全栈测试报告生成器

生成统一的 HTML 报告，整合所有测试结果（PowerShell CSV、pytest HTML、前端测试报告等）
"""

from __future__ import annotations

import argparse
import json
import os
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


def read_json(filepath: str) -> Dict[str, Any]:
    """读取 JSON 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_csv(filepath: str) -> List[Dict[str, Any]]:
    """读取 CSV 文件"""
    if not os.path.exists(filepath):
        return []
    
    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results


def read_log_preview(filepath: str, max_lines: int = 20) -> str:
    """读取日志文件的前 N 行作为预览"""
    if not os.path.exists(filepath):
        return ""
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()[:max_lines]
            return ''.join(lines)
    except Exception as e:
        return f"Error reading log: {e}"


def render_html_report(
    summary_json: str,
    output_html: str,
    base_dir: Optional[str] = None
) -> None:
    """生成 HTML 报告"""
    
    # 读取汇总数据
    summary = read_json(summary_json)
    
    # 确定基础目录
    if base_dir is None:
        base_dir = os.path.dirname(summary_json)
    
    base_dir_path = Path(base_dir)
    
    # 读取 PowerShell API 测试结果
    ps_test_csv = base_dir_path / "api-powershell-tests.csv"
    ps_results = read_csv(str(ps_test_csv)) if ps_test_csv.exists() else []
    
    # 读取错误日志
    ps_error_log = base_dir_path / "api-powershell-error.log"
    backend_pytest_log = base_dir_path / "backend-pytest-output.log"
    frontend_smoke_log = base_dir_path / "frontend-smoke-test-output.log"
    
    # 尝试从前端测试阶段推断前端地址
    frontend_base_url = ""
    for stage in summary.get("Stages", []):
        if "Frontend" in stage.get("Name", ""):
            # 尝试从 AdminBaseUrl 推断前端地址
            admin_url = summary.get("AdminBaseUrl", "")
            if admin_url:
                admin_host = admin_url.replace("http://", "").replace("https://", "").split(":")[0]
                frontend_base_url = f"http://{admin_host}:3001"
            else:
                frontend_base_url = "http://localhost:3001"
            break
    
    # 计算汇总统计
    total_tests = sum(stage.get("Total", 0) for stage in summary.get("Stages", []))
    total_passed = sum(stage.get("Passed", 0) for stage in summary.get("Stages", []))
    total_failed = sum(stage.get("Failed", 0) for stage in summary.get("Stages", []))
    total_skipped = sum(stage.get("Skipped", 0) for stage in summary.get("Stages", []))
    total_duration_ms = sum(stage.get("DurationMs", 0) for stage in summary.get("Stages", []))
    
    success_rate = (total_passed / (total_tests - total_skipped) * 100) if (total_tests - total_skipped) > 0 else 0
    
    # 计算平均响应时间（从 PowerShell 测试结果）
    avg_response_time = None
    if ps_results:
        response_times = [float(r.get("ResponseTime", 0)) for r in ps_results if r.get("ResponseTime") and r.get("Status") == "Pass"]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
    
    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Full Stack Test Report - {summary.get('Timestamp', 'Unknown')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }}
        
        h3 {{
            color: #555;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        
        .summary-card.success {{
            border-left-color: #27ae60;
        }}
        
        .summary-card.failed {{
            border-left-color: #e74c3c;
        }}
        
        .summary-card.warning {{
            border-left-color: #f39c12;
        }}
        
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
        }}
        
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .summary-card.success .value {{
            color: #27ae60;
        }}
        
        .summary-card.failed .value {{
            color: #e74c3c;
        }}
        
        .summary-card.warning .value {{
            color: #f39c12;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        
        .status-fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        
        .status-skipped {{
            color: #f39c12;
            font-weight: bold;
        }}
        
        .log-preview {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
            margin: 10px 0;
        }}
        
        .link {{
            color: #3498db;
            text-decoration: none;
        }}
        
        .link:hover {{
            text-decoration: underline;
        }}
        
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        
        .info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #2196f3;
            margin: 15px 0;
        }}
        
        .warning {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }}
        
        .error {{
            background: #f8d7da;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #dc3545;
            margin: 15px 0;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Full Stack Test Report</h1>
        
        <div class="info">
            <strong>测试时间:</strong> {summary.get('Timestamp', 'Unknown')}<br>
            <strong>Admin API:</strong> {summary.get('AdminBaseUrl', 'Unknown')}<br>
            <strong>MiniApp API:</strong> {summary.get('MiniAppBaseUrl', 'Unknown')}<br>
            <strong>Frontend:</strong> {frontend_base_url if frontend_base_url else 'N/A (not tested)'}<br>
            <strong>输出目录:</strong> {summary.get('OutputDir', 'Unknown')}
        </div>
        
        <h2>📊 Test Summary</h2>
        <div class="summary">
            <div class="summary-card success">
                <h3>Total Tests</h3>
                <div class="value">{total_tests}</div>
            </div>
            <div class="summary-card success">
                <h3>Passed ✅</h3>
                <div class="value">{total_passed}</div>
            </div>
            <div class="summary-card failed">
                <h3>Failed ❌</h3>
                <div class="value">{total_failed}</div>
            </div>
            <div class="summary-card warning">
                <h3>Skipped ⏭️</h3>
                <div class="value">{total_skipped}</div>
            </div>
            <div class="summary-card {'success' if success_rate >= 90 else 'failed' if success_rate < 50 else 'warning'}">
                <h3>Success Rate</h3>
                <div class="value">{success_rate:.1f}%</div>
            </div>
            <div class="summary-card">
                <h3>Total Duration</h3>
                <div class="value">{total_duration_ms / 1000:.2f}s</div>
            </div>
        </div>
        
        <h2>📈 Performance Metrics</h2>
        <div class="section">
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Total Test Duration</td>
                        <td>{total_duration_ms / 1000:.2f} seconds</td>
                    </tr>
"""
    
    if avg_response_time:
        html += f"""                    <tr>
                        <td>Average Response Time (PowerShell Tests)</td>
                        <td>{avg_response_time:.2f} ms</td>
                    </tr>
"""
    
    html += f"""                </tbody>
            </table>
        </div>
        
        <h2>📋 Test Stages</h2>
        <div class="section">
            <table>
                <thead>
                    <tr>
                        <th>Stage</th>
                        <th>Total</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Skipped</th>
                        <th>Duration</th>
                        <th>Report</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for stage in summary.get("Stages", []):
        status_class = "success" if stage.get("Failed", 0) == 0 else "failed"
        report_link = f'<a href="{stage.get("ReportFile", "")}" class="link">View Report</a>' if stage.get("ReportFile") else "-"
        
        html += f"""                    <tr>
                        <td><strong>{stage.get('Name', 'Unknown')}</strong></td>
                        <td>{stage.get('Total', 0)}</td>
                        <td class="status-pass">{stage.get('Passed', 0)}</td>
                        <td class="status-fail">{stage.get('Failed', 0)}</td>
                        <td class="status-skipped">{stage.get('Skipped', 0)}</td>
                        <td>{stage.get('DurationMs', 0) / 1000:.2f}s</td>
                        <td>{report_link}</td>
                    </tr>
"""
    
    html += """                </tbody>
            </table>
        </div>
        
        <h2>🔍 Detailed Test Results</h2>
"""
    
    # PowerShell API 测试结果
    if ps_results:
        html += """        <h3>PowerShell API Tests</h3>
        <div class="section">
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>URL</th>
                        <th>Status</th>
                        <th>Status Code</th>
                        <th>Response Time (ms)</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for result in ps_results:
            status = result.get("Status", "Unknown")
            status_class = "status-pass" if status == "Pass" else "status-fail" if status == "Fail" else "status-skipped"
            status_symbol = "✅" if status == "Pass" else "❌" if status == "Fail" else "⏭️"
            
            html += f"""                    <tr>
                        <td>{result.get('Name', 'Unknown')}</td>
                        <td><code>{result.get('Url', 'Unknown')}</code></td>
                        <td class="{status_class}">{status_symbol} {status}</td>
                        <td>{result.get('StatusCode', '-')}</td>
                        <td>{result.get('ResponseTime', '-')}</td>
                    </tr>
"""
        
        html += """                </tbody>
            </table>
        </div>
"""
    
    # 前端测试结果（如果有）
    frontend_stage = next((s for s in summary.get("Stages", []) if "Frontend" in s.get("Name", "")), None)
    if frontend_stage and frontend_stage.get("Total", 0) > 0:
        html += f"""        <h2>🎨 Frontend Test Results</h2>
        <div class="section">
            <table>
                <thead>
                    <tr>
                        <th>Test Stage</th>
                        <th>Total</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Skipped</th>
                        <th>Duration</th>
                        <th>Report</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>{frontend_stage.get('Name', 'Frontend Tests')}</strong></td>
                        <td>{frontend_stage.get('Total', 0)}</td>
                        <td class="status-pass">{frontend_stage.get('Passed', 0)}</td>
                        <td class="status-fail">{frontend_stage.get('Failed', 0)}</td>
                        <td class="status-skipped">{frontend_stage.get('Skipped', 0)}</td>
                        <td>{frontend_stage.get('DurationMs', 0) / 1000:.2f}s</td>
                        <td>
"""
        if frontend_stage.get("ReportFile"):
            html += f'                            <a href="{frontend_stage.get("ReportFile")}" class="link">View Report</a>'
        else:
            html += "                            -"
        html += """                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
"""
    
    # 错误日志摘要
    html += """        <h2>📝 Error Logs Preview</h2>
"""
    
    if ps_error_log.exists():
        ps_log_preview = read_log_preview(str(ps_error_log))
        if ps_log_preview:
            html += f"""        <h3>PowerShell API Test Errors</h3>
        <div class="log-preview">{ps_log_preview}</div>
        <p><strong>Full log:</strong> <a href="{ps_error_log.name}" class="link">{ps_error_log.name}</a></p>
"""
    
    if backend_pytest_log.exists():
        backend_log_preview = read_log_preview(str(backend_pytest_log))
        if backend_log_preview:
            html += f"""        <h3>Backend pytest Test Output</h3>
        <div class="log-preview">{backend_log_preview}</div>
        <p><strong>Full log:</strong> <a href="{backend_pytest_log.name}" class="link">{backend_pytest_log.name}</a></p>
"""
    
    if frontend_smoke_log.exists():
        frontend_log_preview = read_log_preview(str(frontend_smoke_log))
        if frontend_log_preview:
            html += f"""        <h3>Frontend Smoke Test Output</h3>
        <div class="log-preview">{frontend_log_preview}</div>
        <p><strong>Full log:</strong> <a href="{frontend_smoke_log.name}" class="link">{frontend_smoke_log.name}</a></p>
"""
    
    html += f"""        <div class="footer">
            <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Full Stack Test Report Generator v1.0</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 写入 HTML 文件
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Report generated: {output_html}")


def main():
    parser = argparse.ArgumentParser(description='Generate full stack test report')
    parser.add_argument('--summary', required=True, help='Path to summary.json')
    parser.add_argument('--output', required=True, help='Path to output HTML file')
    parser.add_argument('--base-dir', help='Base directory for test output files')
    
    args = parser.parse_args()
    
    render_html_report(args.summary, args.output, args.base_dir)


if __name__ == '__main__':
    main()

