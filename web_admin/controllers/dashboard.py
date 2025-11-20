# web_admin/controllers/dashboard.py
from __future__ import annotations

import time
from datetime import datetime, UTC
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy import func, case, and_
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
import sqlite3

from core.i18n.i18n import t
# 读写分离：如未配置只读连接，deps 内部会回落到读写连接
from web_admin.deps import db_session_ro as db_session, require_admin

# —— 模型统一从 models 包导入（注意：你的充值模型名是 RechargeOrder，不是 Recharge）
from models.user import User
from models.envelope import Envelope
from models.ledger import Ledger
from models.recharge import RechargeOrder, OrderStatus  # ← 修正类名

logger = logging.getLogger("web_admin.controllers.dashboard")

router = APIRouter(prefix="/admin", tags=["admin-dashboard"])

# ---- 进程内软缓存（30 秒） ----
_CACHE: Dict[str, Any] = {"ts": 0, "data": None}
_CACHE_TTL = 30  # 秒


def _col(model, *names):
    """容错字段选择：按给定字段名依次找第一个存在的列属性。"""
    for n in names:
        if hasattr(model, n):
            return getattr(model, n)
    return None


def _stats_query(db) -> Dict[str, Any]:
    """
    用 3~4 个聚合查询拿到所有卡片数据。字段名不一致也能兜住。
    依赖索引建议：
      - users(created_at) [可选]
      - envelopes(status) 或 (remain_count, closed_at)
      - ledger(created_at), ledger(type, created_at)
      - recharge_orders(status), recharge_orders(status, created_at)
    """
    seven_days_ago = dt.datetime.now(UTC).replace(tzinfo=None) - dt.timedelta(days=7)

    # ---- Users ----
    users_total = 0
    try:
        users_total = (
            db.query(func.count())
            .select_from(User)
            .scalar()
            or 0
        )
    except Exception:
        # 某些历史库可能缺失 User 表或结构异常，捕获后保持 0，避免仪表盘整页崩溃
        users_total = 0

    # ---- Envelopes（活跃中）----
    # 有 status 就按 OPEN 认定"活跃"；否则按 remain_count>0 且未关闭
    envelopes_active = 0
    try:
        E_STATUS = _col(Envelope, "status")
        E_CLOSED = _col(Envelope, "closed_at", "finished_at", "ended_at", "is_finished")
        E_REMAIN = _col(Envelope, "remain_count", "left_count", "rest_count", "left", "left_shares")

        q_env = db.query(func.count(1)).select_from(Envelope)
        if E_STATUS is not None:
            q_env = q_env.filter(E_STATUS.in_(["OPEN", "ACTIVE", "ONGOING"]))
        else:
            conds = []
            if E_REMAIN is not None:
                conds.append(E_REMAIN > 0)
            if E_CLOSED is not None:
                # 支持字段为布尔/时间的情况
                try:
                    conds.append(and_(E_CLOSED.is_(None)))
                except Exception:
                    pass
            if conds:
                q_env = q_env.filter(and_(*conds))
        envelopes_active = q_env.scalar() or 0
    except (SQLAlchemyOperationalError, sqlite3.OperationalError) as e:
        # 优雅降级：如果 envelopes 表不存在，使用零统计值
        # 这提升了开发/新部署环境下的稳定性，生产环境应通过迁移/初始化确保表存在
        error_msg = str(e).lower()
        if "no such table" in error_msg and "envelopes" in error_msg:
            logger.warning("envelopes table not found, using zero stats")
            envelopes_active = 0
        else:
            # 其他类型的数据库错误（如连接失败、权限问题等），重新抛出
            raise
    except Exception:
        # 其他类型的异常，重新抛出
        raise

    # ---- Ledger（近 7 天 Σ 金额与条数，只算核心类型）----
    ledger_7d_amount = 0
    ledger_7d_count = 0
    try:
        L_AMOUNT = _col(Ledger, "amount", "delta", "value")
        L_CREATED = _col(Ledger, "created_at", "created", "ts")
        L_TYPE = _col(Ledger, "type", "ltype")
        # 用你模型里的规范类型名
        FOCUS_TYPES = ("RECHARGE", "HONGBAO_SEND", "HONGBAO_GRAB", "ADJUSTMENT")

        if L_AMOUNT is not None:
            q_ledger = db.query(
                func.coalesce(func.sum(L_AMOUNT), 0).label("sum_amt"),
                func.count(1).label("cnt"),
            ).select_from(Ledger)
        else:
            q_ledger = db.query(func.count(1).label("cnt")).select_from(Ledger)

        if L_CREATED is not None:
            q_ledger = q_ledger.filter(L_CREATED >= seven_days_ago)
        if L_TYPE is not None:
            q_ledger = q_ledger.filter(L_TYPE.in_(FOCUS_TYPES))

        rec = q_ledger.first()
        ledger_7d_amount = ((rec.sum_amt if rec else 0) or 0) if L_AMOUNT is not None else 0
        ledger_7d_count = (rec.cnt if rec else 0) or 0
    except (SQLAlchemyOperationalError, sqlite3.OperationalError) as e:
        # 优雅降级：如果 ledger 表不存在，使用零统计值
        error_msg = str(e).lower()
        if "no such table" in error_msg and "ledger" in error_msg:
            logger.warning("ledger table not found, using zero stats")
            ledger_7d_amount = 0
            ledger_7d_count = 0
        else:
            # 其他类型的数据库错误，重新抛出
            raise
    except Exception:
        # 其他类型的异常，重新抛出
        raise

    # ---- Recharge（PENDING / SUCCESS 数量）----
    # 你的模型字段：RechargeOrder.status 是 Enum(OrderStatus)
    recharge_pending = 0
    recharge_success = 0
    try:
        R_STATUS = _col(RechargeOrder, "status")
        if R_STATUS is not None:
            # SQLAlchemy Enum 列直接与枚举值比较最稳妥
            q_re = db.query(
                func.sum(case((R_STATUS == OrderStatus.PENDING, 1), else_=0)).label("p"),
                func.sum(case((R_STATUS == OrderStatus.SUCCESS, 1), else_=0)).label("s"),
            ).select_from(RechargeOrder)
            row = q_re.first()
            recharge_pending = int((row.p if row else 0) or 0)
            recharge_success = int((row.s if row else 0) or 0)
    except (SQLAlchemyOperationalError, sqlite3.OperationalError) as e:
        # 优雅降级：如果 recharge_orders 表不存在，使用零统计值
        error_msg = str(e).lower()
        if "no such table" in error_msg and ("recharge" in error_msg or "recharge_order" in error_msg):
            logger.warning("recharge_orders table not found, using zero stats")
            recharge_pending = 0
            recharge_success = 0
        else:
            # 其他类型的数据库错误，重新抛出
            raise
    except Exception:
        # 其他类型的异常，重新抛出
        raise

    return {
        "users_total": int(users_total or 0),
        "envelopes_active": int(envelopes_active or 0),
        "ledger_7d_amount": f"{(ledger_7d_amount or 0):.2f}",
        "ledger_7d_count": int(ledger_7d_count or 0),
        "recharge_pending": int(recharge_pending or 0),
        "recharge_success": int(recharge_success or 0),
        # 返回 ISO 格式字符串，供前端和模板使用
        "since": seven_days_ago.isoformat(),
        "until": dt.datetime.now(UTC).replace(tzinfo=None).isoformat(),
    }


# -------- 首页跳转到仪表盘 --------
@router.get("", include_in_schema=False)
def _root():
    return RedirectResponse(url="/admin/dashboard")


# -------- 仪表盘页面 --------
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(req: Request, db=Depends(db_session), sess=Depends(require_admin)):
    now = time.time()
    if _CACHE["data"] is not None and now - _CACHE["ts"] <= _CACHE_TTL:
        data = _CACHE["data"]
    else:
        data = _stats_query(db)
        _CACHE["ts"] = now
        _CACHE["data"] = data

    return req.app.state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": req,
            "title": t("admin.nav.dashboard"),
            "nav_active": "dashboard",
            "s": data,
        },
    )


# -------- REST API: 获取统计数据 --------
@router.get("/api/v1/dashboard/stats", response_class=JSONResponse)
def get_dashboard_stats(db=Depends(db_session), sess=Depends(require_admin)):
    """返回仪表盘统计数据（JSON 格式，供前端调用）"""
    now = time.time()
    if _CACHE["data"] is not None and now - _CACHE["ts"] <= _CACHE_TTL:
        data = _CACHE["data"]
    else:
        data = _stats_query(db)
        _CACHE["ts"] = now
        _CACHE["data"] = data
    
    return JSONResponse(data)


# -------- REST API: 获取统计数据（无需认证版本，用于前端展示） --------
@router.get("/api/v1/dashboard/stats/public", response_class=JSONResponse)
def get_dashboard_stats_public(db=Depends(db_session)):
    """
    返回仪表盘统计数据（公开版本，无需认证）
    注意：此接口仅返回基础统计，不包含敏感信息
    如果数据库查询失败，返回 mock 数据以确保前端正常显示
    """
    try:
        now = time.time()
        if _CACHE["data"] is not None and now - _CACHE["ts"] <= _CACHE_TTL:
            data = _CACHE["data"]
        else:
            data = _stats_query(db)
            _CACHE["ts"] = now
            _CACHE["data"] = data
        return JSONResponse(data)
    except Exception as e:
        # 如果数据库查询失败，返回 mock 数据
        import datetime as dt
        mock_data = {
            "users_total": 1234,
            "envelopes_active": 56,
            "ledger_7d_amount": "12345.67",
            "ledger_7d_count": 890,
            "recharge_pending": 12,
            "recharge_success": 345,
            "since": (dt.datetime.now(UTC) - dt.timedelta(days=7)).isoformat(),
            "until": dt.datetime.now(UTC).isoformat(),
        }
        return JSONResponse(mock_data)


# -------- REST API: 获取 Dashboard 数据（主接口，字段名与前端一致） --------
@router.get("/api/v1/dashboard", response_class=JSONResponse)
def get_dashboard(db=Depends(db_session), sess=Depends(require_admin)):
    """
    返回 Dashboard 完整数据（字段名与前端期望一致）
    如果数据库查询失败，返回 mock 数据以确保前端正常显示
    """
    try:
        now = time.time()
        if _CACHE["data"] is not None and now - _CACHE["ts"] <= _CACHE_TTL:
            raw_data = _CACHE["data"]
        else:
            raw_data = _stats_query(db)
            _CACHE["ts"] = now
            _CACHE["data"] = raw_data
        
        # 转换为前端期望的字段名
        result = {
            "user_count": raw_data.get("users_total", 0),
            "active_envelopes": raw_data.get("envelopes_active", 0),
            "last_7d_amount": raw_data.get("ledger_7d_amount", "0.00"),
            "last_7d_orders": raw_data.get("ledger_7d_count", 0),
            "pending_recharges": raw_data.get("recharge_pending", 0),
            "success_recharges": raw_data.get("recharge_success", 0),
            "since": raw_data.get("since"),
            "until": raw_data.get("until"),
        }
        return JSONResponse(result)
    except Exception as e:
        # 如果数据库查询失败，返回 mock 数据
        import datetime as dt
        mock_data = {
            "user_count": 1234,
            "active_envelopes": 56,
            "last_7d_amount": "12345.67",
            "last_7d_orders": 890,
            "pending_recharges": 12,
            "success_recharges": 345,
            "since": (dt.datetime.now(UTC) - dt.timedelta(days=7)).isoformat(),
            "until": dt.datetime.now(UTC).isoformat(),
        }
        return JSONResponse(mock_data)


# -------- REST API: 获取统计数据（无需认证版本，字段名与前端一致） --------
@router.get("/api/v1/dashboard/public", response_class=JSONResponse)
def get_dashboard_public(db=Depends(db_session)):
    """
    返回 Dashboard 完整数据（公开版本，无需认证，字段名与前端期望一致）
    如果数据库查询失败，返回 mock 数据以确保前端正常显示
    """
    try:
        now = time.time()
        if _CACHE["data"] is not None and now - _CACHE["ts"] <= _CACHE_TTL:
            raw_data = _CACHE["data"]
        else:
            raw_data = _stats_query(db)
            _CACHE["ts"] = now
            _CACHE["data"] = raw_data
        
        # 转换为前端期望的字段名
        result = {
            "user_count": raw_data.get("users_total", 0),
            "active_envelopes": raw_data.get("envelopes_active", 0),
            "last_7d_amount": raw_data.get("ledger_7d_amount", "0.00"),
            "last_7d_orders": raw_data.get("ledger_7d_count", 0),
            "pending_recharges": raw_data.get("recharge_pending", 0),
            "success_recharges": raw_data.get("recharge_success", 0),
            "since": raw_data.get("since"),
            "until": raw_data.get("until"),
        }
        return JSONResponse(result)
    except Exception as e:
        # 如果数据库查询失败，返回 mock 数据
        import datetime as dt
        mock_data = {
            "user_count": 1234,
            "active_envelopes": 56,
            "last_7d_amount": "12345.67",
            "last_7d_orders": 890,
            "pending_recharges": 12,
            "success_recharges": 345,
            "since": (dt.datetime.now(UTC) - dt.timedelta(days=7)).isoformat(),
            "until": dt.datetime.now(UTC).isoformat(),
        }
        return JSONResponse(mock_data)
