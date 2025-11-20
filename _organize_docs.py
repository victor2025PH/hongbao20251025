#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理 Markdown 文档
"""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# 排除的目录
EXCLUDE_DIRS = {'.git', '.github', 'node_modules', '.next', 'dist', 'build', 'exports', 'backups', 'static', '无用文件'}

# 根目录下的重要 README 保持不变
ROOT_READMES = {
    'README.md',
    'READMEV2.md',
    'README_DEPLOY.md',
}

# 子项目的 README 保持不变
PROJECT_READMES = {
    'frontend-next/README.md',
    'miniapp-frontend/README.md',
    'saas-demo/README.md',
}

# 文档分类规则
DESIGN_DOCS = {
    'ARCHITECTURE', '架构', 'SYSTEM_DESIGN', '系统设计', '设计', '流程规划',
    'SMART_FORMAT_CONVERTER_DESIGN', 'API_TABLE', 'DASHBOARD', '数据结构'
}

USAGE_DOCS = {
    'QUICK_START', '快速开始', 'DEPLOYMENT', '部署', 'INSTALL', '安装',
    'GUIDE', '指南', 'TROUBLESHOOTING', '故障排查', 'USAGE', '使用',
    'SETUP', '配置', 'TESTING', '测试', 'HEALTHCHECK', '健康检查',
    'SYSTEMD', 'CRON', 'SSH', '防火墙', '安全组', '密钥'
}

DEVELOPMENT_DOCS = {
    'DEVELOPMENT', '开发', 'PROGRESS', '进度', 'STATUS', '状态', 'SUMMARY', '总结',
    'FIX', '修复', 'TODO', 'PLAN', '计划', 'NEXT_STEPS', '下一步', 'CHECKLIST',
    'PUSH_TO_GITHUB', '推送', 'CLONE', '克隆', '修复', '诊断', '问题'
}

def should_exclude(path: Path) -> bool:
    """检查路径是否应排除"""
    parts = path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    return False

def classify_doc(file_path: Path) -> str:
    """分类文档"""
    name = file_path.name.upper()
    stem = file_path.stem.upper()
    
    # 先检查文件名
    if any(keyword in name for keyword in DESIGN_DOCS):
        return '设计文档'
    if any(keyword in name for keyword in USAGE_DOCS):
        return '使用说明'
    if any(keyword in name for keyword in DEVELOPMENT_DOCS):
        return '开发笔记'
    
    # 读取内容判断（只读前几行）
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_lines = ''.join(f.readlines()[:20]).upper()
            
            if any(keyword in first_lines for keyword in DESIGN_DOCS):
                return '设计文档'
            if any(keyword in first_lines for keyword in USAGE_DOCS):
                return '使用说明'
            if any(keyword in first_lines for keyword in DEVELOPMENT_DOCS):
                return '开发笔记'
    except:
        pass
    
    # 默认归类到开发笔记
    return '开发笔记'

def organize_docs(root: Path) -> Dict[str, List[Tuple[Path, str]]]:
    """整理文档"""
    result = {
        '设计文档': [],
        '使用说明': [],
        '开发笔记': [],
        '保持不变': []
    }
    
    # 查找所有 .md 文件
    for md_file in root.rglob('*.md'):
        if should_exclude(md_file):
            continue
        
        relative = md_file.relative_to(root)
        relative_str = str(relative).replace('\\', '/')
        
        # 检查是否为需要保持原位的 README
        if md_file.name in ROOT_READMES and md_file.parent == root:
            result['保持不变'].append((md_file, '根目录主 README'))
            continue
        
        if relative_str in PROJECT_READMES:
            result['保持不变'].append((md_file, '子项目 README'))
            continue
        
        # 分类
        category = classify_doc(md_file)
        result[category].append((md_file, relative_str))
    
    return result

if __name__ == '__main__':
    root = Path('.')
    print(f"整理文档目录: {root.absolute()}")
    print()
    
    organized = organize_docs(root)
    
    print("=" * 80)
    print("文档分类结果:")
    print("=" * 80)
    for category, files in organized.items():
        print(f"\n{category} ({len(files)} 个文件):")
        for file_path, info in sorted(files, key=lambda x: str(x[0])):
            print(f"  - {file_path.relative_to(root)} ({info})")

