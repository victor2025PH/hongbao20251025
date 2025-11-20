#!/usr/bin/env python3
"""
Webhook 接收器 - 接收 GitHub Webhook 并触发部署
运行方式: python deploy/scripts/webhook_receiver.py
"""

import hmac
import hashlib
import json
import os
import subprocess
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from typing import Dict, Optional

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/redpacket/logs/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-secret-key-here')
DEPLOY_SCRIPT = os.getenv('DEPLOY_SCRIPT', '/opt/redpacket/deploy/scripts/auto_deploy.sh')
ALLOWED_BRANCHES = ['master', 'main']  # 只允许这些分支触发部署


def verify_signature(payload_body: bytes, signature: str) -> bool:
    """
    验证 GitHub Webhook 签名
    """
    if not signature:
        return False
    
    # GitHub 签名格式: sha256=hash
    if not signature.startswith('sha256='):
        return False
    
    signature_hash = signature[7:]  # 移除 'sha256=' 前缀
    
    # 计算期望的签名
    mac = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_hash = mac.hexdigest()
    
    # 使用安全比较避免时序攻击
    return hmac.compare_digest(signature_hash, expected_hash)


def trigger_deployment(payload: Dict) -> Dict[str, str]:
    """
    触发部署脚本
    """
    try:
        # 提取推送信息
        ref = payload.get('ref', '')
        branch = ref.split('/')[-1] if ref.startswith('refs/heads/') else ''
        
        commits = payload.get('commits', [])
        if not commits:
            return {'status': 'ignored', 'message': '没有新的提交'}
        
        # 检查是否是指定分支
        if branch not in ALLOWED_BRANCHES:
            return {'status': 'ignored', 'message': f'分支 {branch} 不在允许列表中'}
        
        # 提取提交信息
        commit = commits[-1]
        commit_id = commit.get('id', '')[:7]
        commit_msg = commit.get('message', '')
        author = commit.get('author', {}).get('name', 'Unknown')
        
        logger.info(f"触发部署: 分支={branch}, 提交={commit_id}, 作者={author}")
        
        # 执行部署脚本
        result = subprocess.run(
            [DEPLOY_SCRIPT],
            capture_output=True,
            text=True,
            timeout=1800  # 30 分钟超时
        )
        
        if result.returncode == 0:
            logger.info(f"部署成功: {commit_id}")
            return {
                'status': 'success',
                'message': f'部署成功: {commit_id}',
                'output': result.stdout[-1000:]  # 最后 1000 字符
            }
        else:
            logger.error(f"部署失败: {commit_id}\n{result.stderr}")
            return {
                'status': 'failed',
                'message': f'部署失败: {commit_id}',
                'error': result.stderr[-1000:]  # 最后 1000 字符
            }
            
    except subprocess.TimeoutExpired:
        logger.error("部署超时")
        return {'status': 'timeout', 'message': '部署超时（超过30分钟）'}
    except Exception as e:
        logger.exception(f"部署异常: {e}")
        return {'status': 'error', 'message': str(e)}


@app.route('/healthz', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'ok', 'service': 'webhook-receiver'})


@app.route('/webhook/deploy', methods=['POST'])
def webhook_deploy():
    """
    接收 GitHub Webhook
    """
    # 获取签名
    signature = request.headers.get('X-Hub-Signature-256', '')
    
    # 获取请求体
    payload_body = request.get_data()
    
    # 验证签名
    if not verify_signature(payload_body, signature):
        logger.warning("无效的 Webhook 签名")
        return jsonify({'error': 'Invalid signature'}), 401
    
    # 解析 JSON
    try:
        payload = json.loads(payload_body.decode('utf-8'))
    except json.JSONDecodeError:
        logger.error("无效的 JSON 格式")
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # 检查事件类型
    event_type = request.headers.get('X-GitHub-Event', '')
    logger.info(f"收到 Webhook 事件: {event_type}")
    
    # 只处理 push 事件
    if event_type != 'push':
        return jsonify({'status': 'ignored', 'message': f'事件类型 {event_type} 不支持'})
    
    # 触发部署
    result = trigger_deployment(payload)
    
    return jsonify(result)


@app.route('/webhook/deploy', methods=['GET'])
def webhook_info():
    """Webhook 信息（用于测试）"""
    return jsonify({
        'service': 'webhook-receiver',
        'endpoint': '/webhook/deploy',
        'allowed_branches': ALLOWED_BRANCHES,
        'status': 'running'
    })


if __name__ == '__main__':
    # 确保日志目录存在
    os.makedirs('/opt/redpacket/logs', exist_ok=True)
    
    # 启动服务器
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    )

