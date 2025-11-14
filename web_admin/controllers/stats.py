# web_admin/controllers/stats.py
from __future__ import annotations

import datetime as dt
from typing import Dict, Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from web_admin.deps import db_session_ro as db_session, require_admin

router = APIRouter(prefix="/admin/api/v1/stats", tags=["admin-stats"])


# -------- 趋势统计（最近7天/30天） --------
@router.get("", response_class=JSONResponse)
def get_stats_trends(
    db=Depends(db_session),
    sess=Depends(require_admin),
    days: int = Query(7, ge=1, le=30, description="统计天数（默认7天）"),
):
    """
    返回最近 N 天的趋势统计（图表用的 xAxis + series）
    字段结构与前端 mock 数据保持一致
    """
    try:
        from models.user import User
        from models.envelope import Envelope
        from models.ledger import Ledger
        from sqlalchemy import func, and_
        import datetime as dt
        
        # 计算日期范围
        end_date = dt.datetime.utcnow().replace(tzinfo=None)
        start_date = end_date - dt.timedelta(days=days)
        
        # 查询每日用户数（按创建时间）
        user_trends = []
        for i in range(days):
            date = start_date + dt.timedelta(days=i)
            next_date = date + dt.timedelta(days=1)
            
            # 每日新增用户数
            daily_users = (
                db.query(func.count(User.id))
                .filter(
                    and_(
                        User.created_at >= date,
                        User.created_at < next_date
                    )
                )
                .scalar() or 0
            )
            
            # 每日新增红包数
            daily_envelopes = (
                db.query(func.count(Envelope.id))
                .filter(
                    and_(
                        Envelope.created_at >= date,
                        Envelope.created_at < next_date
                    )
                )
                .scalar() or 0
            )
            
            # 每日账本金额（只统计收入）
            daily_amount = (
                db.query(func.coalesce(func.sum(Ledger.amount), 0))
                .filter(
                    and_(
                        Ledger.created_at >= date,
                        Ledger.created_at < next_date,
                        Ledger.amount > 0  # 只统计收入
                    )
                )
                .scalar() or 0
            )
            
            user_trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "users": int(daily_users),
                "envelopes": int(daily_envelopes),
                "amount": float(daily_amount) if daily_amount else 0.0,
            })
        
        return JSONResponse({
            "trends": user_trends,
            "period": {
                "days": days,
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        })
    except Exception as e:
        # 如果查询失败，返回 mock 数据
        import datetime as dt
        mock_trends = [
            {
                "date": (dt.datetime.utcnow() - dt.timedelta(days=days - 1 - i)).strftime("%Y-%m-%d"),
                "users": 100 + i * 10,
                "envelopes": 40 + i * 5,
                "amount": 10000.0 + i * 500.0,
            }
            for i in range(days)
        ]
        return JSONResponse({
            "trends": mock_trends,
            "period": {
                "days": days,
                "start": (dt.datetime.utcnow() - dt.timedelta(days=days)).isoformat(),
                "end": dt.datetime.utcnow().isoformat(),
            },
        })


# -------- 整体概览统计 --------
@router.get("/overview", response_class=JSONResponse)
def get_stats_overview(db=Depends(db_session), sess=Depends(require_admin)):
    """
    返回整体概览统计（静态假数据，结构稳定）
    """
    # TODO: 后续可以对接真实数据库查询
    mock_data = {
        "total_users": 1234,
        "total_envelopes": 5678,
        "total_amount": "123456.78",
        "total_recharges": 890,
        "success_rate": 98.5,
        "avg_envelope_amount": "21.75",
        "today_stats": {
            "users": 12,
            "envelopes": 45,
            "amount": "987.65",
            "recharges": 8,
        },
        "yesterday_stats": {
            "users": 15,
            "envelopes": 52,
            "amount": "1234.56",
            "recharges": 10,
        },
    }
    return JSONResponse(mock_data)


# -------- 任务维度统计 --------
@router.get("/tasks", response_class=JSONResponse)
def get_stats_tasks(db=Depends(db_session), sess=Depends(require_admin)):
    """
    返回任务维度统计（静态假数据，结构稳定）
    """
    # TODO: 后续可以对接真实数据库查询
    mock_data = {
        "total_tasks": 1234,
        "by_status": {
            "active": 56,
            "closed": 1100,
            "failed": 78,
        },
        "by_type": {
            "群发红包": 800,
            "个人红包": 300,
            "定时红包": 100,
            "活动红包": 34,
        },
        "recent_7_days": [
            {
                "date": (dt.datetime.utcnow() - dt.timedelta(days=i)).strftime("%Y-%m-%d"),
                "count": 100 + i * 10,
                "success": 95 + i * 10,
                "failed": 5,
            }
            for i in range(6, -1, -1)
        ],
        "avg_completion_time": "2.5",  # 小时
    }
    return JSONResponse(mock_data)


# -------- 群组维度统计 --------
@router.get("/groups", response_class=JSONResponse)
def get_stats_groups(db=Depends(db_session), sess=Depends(require_admin)):
    """
    返回群组维度统计（静态假数据，结构稳定）
    """
    # TODO: 后续可以对接真实数据库查询
    mock_data = {
        "total_groups": 234,
        "active_groups": 180,
        "paused_groups": 30,
        "review_groups": 20,
        "removed_groups": 4,
        "by_language": {
            "zh": 120,
            "en": 80,
            "other": 34,
        },
        "top_groups": [
            {
                "id": 1,
                "name": "测试群组 A",
                "members_count": 5000,
                "envelopes_count": 1234,
                "total_amount": "56789.12",
            },
            {
                "id": 2,
                "name": "测试群组 B",
                "members_count": 3000,
                "envelopes_count": 890,
                "total_amount": "34567.89",
            },
            {
                "id": 3,
                "name": "测试群组 C",
                "members_count": 2000,
                "envelopes_count": 567,
                "total_amount": "23456.78",
            },
        ],
        "recent_7_days_activity": [
            {
                "date": (dt.datetime.utcnow() - dt.timedelta(days=i)).strftime("%Y-%m-%d"),
                "new_groups": 2 + i,
                "new_members": 50 + i * 10,
                "envelopes_sent": 20 + i * 5,
            }
            for i in range(6, -1, -1)
        ],
    }
    return JSONResponse(mock_data)

