#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本

用法：
    python init_db.py

功能：
    - 创建所有 SQLAlchemy 模型对应的数据表
    - 适用于开发环境首次启动前的数据库初始化
    - 生产环境建议使用 Alembic 迁移

注意：
    - 此脚本是幂等的，可以安全地多次执行
    - 如果表已存在，不会报错或重复创建
"""

from __future__ import annotations

import sys
import os

# 确保环境变量已加载
from config.load_env import load_env
load_env()

# 导入数据库初始化函数
from models.db import init_db

if __name__ == "__main__":
    print("=" * 60)
    print("数据库初始化脚本")
    print("=" * 60)
    print()
    
    try:
        print("正在初始化数据库表结构...")
        init_db()
        print("✅ 数据库初始化成功！")
        print()
        print("所有数据表已创建：")
        print("  - users")
        print("  - envelopes")
        print("  - ledger")
        print("  - recharge_orders")
        print("  - invites")
        print("  - ...")
        print()
        sys.exit(0)
    except Exception as e:
        print(f"❌ 数据库初始化失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

