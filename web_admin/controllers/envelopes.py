# web_admin/controllers/envelopes.py
from __future__ import annotations

import math
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import func, desc, or_

from core.i18n.i18n import t
from web_admin.deps import db_session, require_admin

# 你的模型
from models.envelope import Envelope
from models.user import User
from models.ledger import Ledger

router = APIRouter(prefix="/admin/envelopes", tags=["admin-envelopes"])
api_router = APIRouter(prefix="/admin/api/v1", tags=["admin-api"])

# ---------- 兼容型取列 ----------
def _col(model, *names):
    for n in names:
        if hasattr(model, n):
            return getattr(model, n)
    return None

# ---------- 降级实现：summary ----------
def _summary(db, eid: int) -> Dict[str, Any]:
    # 先拿到红包
    env: Envelope | None = db.query(Envelope).filter(Envelope.id == eid).first()
    if not env:
        raise HTTPException(status_code=404, detail=t("admin.errors.not_found"))

    # 字段猜测与容错
    token_col = _col(Envelope, "token", "asset", "currency")
    total_amount_col = _col(Envelope, "total_amount", "amount", "sum_amount")
    total_count_col = _col(Envelope, "total_count", "count", "pieces")
    remain_amount_col = _col(Envelope, "remain_amount", "left_amount", "rest_amount")
    remain_count_col = _col(Envelope, "remain_count", "left_count", "rest_count")
    created_at_col = _col(Envelope, "created_at", "created", "ts")
    closed_at_col = _col(Envelope, "closed_at", "finished_at", "ended_at")
    creator_id_col = _col(Envelope, "creator_id", "owner_id", "tg_id")

    token = getattr(env, token_col.key) if token_col else "POINT"
    total_amount = getattr(env, total_amount_col.key) if total_amount_col else 0
    total_count = getattr(env, total_count_col.key) if total_count_col else 0
    remain_amount = getattr(env, remain_amount_col.key) if remain_amount_col else None
    remain_count = getattr(env, remain_count_col.key) if remain_count_col else None
    created_at = getattr(env, created_at_col.key) if created_at_col else None
    closed_at = getattr(env, closed_at_col.key) if closed_at_col else None
    creator_id = getattr(env, creator_id_col.key) if creator_id_col else None

    # 领取统计来自 Ledger：类型一般是 CLAIM/ENVELOPE_CLAIM
    ltype_col = _col(Ledger, "type", "ltype")
    amount_col = _col(Ledger, "amount", "delta", "value")
    note_col = _col(Ledger, "note", "memo")
    created_col = _col(Ledger, "created_at", "created", "ts")
    token_l_col = _col(Ledger, "token", "asset", "currency")
    env_id_col = _col(Ledger, "envelope_id", "env_id")

    claimed_amount = 0
    claimed_count = 0
    if all([ltype_col, amount_col, token_l_col, env_id_col]):
        try:
            q = (
                db.query(func.coalesce(func.sum(amount_col), 0), func.count(1))
                .filter(env_id_col == eid)
                .filter(token_l_col == token)
                .filter(ltype_col.in_(["CLAIM", "ENVELOPE_CLAIM"]))
            )
            claimed_amount, claimed_count = q.first()
        except Exception:
            pass

    # 幸运王：按同一 envelope_id 的单笔最大领取额找用户
    lucky: Optional[Dict[str, Any]] = None
    if all([ltype_col, amount_col, env_id_col]):
        try:
            sub = (
                db.query(
                    Ledger.user_id.label("uid"),
                    amount_col.label("amt"),
                )
                .filter(env_id_col == eid)
                .order_by(desc(amount_col))
                .limit(1)
                .subquery()
            )
            row = db.query(sub.c.uid, sub.c.amt).first()
            if row:
                u = db.query(User).filter(User.tg_id == row.uid).first()
                lucky = {
                    "tg_id": row.uid,
                    "username": getattr(u, "username", None) if u else None,
                    "amount": row.amt,
                }
        except Exception:
            pass

    # 创建者
    creator = None
    if creator_id:
        creator = db.query(User).filter(User.tg_id == creator_id).first()

    # 剩余推断
    if remain_amount is None and total_amount is not None:
        remain_amount = total_amount - (claimed_amount or 0)
    if remain_count is None and total_count is not None:
        remain_count = total_count - (claimed_count or 0)

    return {
        "envelope": env,
        "token": token,
        "total_amount": total_amount,
        "total_count": total_count,
        "claimed_amount": claimed_amount,
        "claimed_count": claimed_count,
        "remain_amount": remain_amount,
        "remain_count": remain_count,
        "created_at": created_at,
        "closed_at": closed_at,
        "creator": creator,
        "lucky": lucky,
    }

# ---------- 明细分页 ----------
def _claims_page(db, eid: int, page: int, per_page: int = 20):
    ltype_col = _col(Ledger, "type", "ltype")
    amount_col = _col(Ledger, "amount", "delta", "value")
    created_col = _col(Ledger, "created_at", "created", "ts")
    user_id_col = _col(Ledger, "user_id", "uid", "tg_id")
    env_id_col = _col(Ledger, "envelope_id", "env_id")

    if not all([ltype_col, amount_col, created_col, user_id_col, env_id_col]):
        return [], 0

    base = (
        db.query(Ledger, User)
        .join(User, User.tg_id == user_id_col)
        .filter(env_id_col == eid)
        .filter(ltype_col.in_(["CLAIM", "ENVELOPE_CLAIM"]))
        .order_by(desc(created_col))
    )
    total = base.count()
    rows = base.offset((page - 1) * per_page).limit(per_page).all()
    return rows, total

# ---------- REST API: 红包任务列表 ----------
@api_router.get("/tasks", response_class=JSONResponse)
def get_tasks_list(
    db=Depends(db_session),
    sess=Depends(require_admin),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="状态筛选: active, closed, failed"),
    q: Optional[str] = Query(None, description="搜索关键词（任务ID或群组名称）"),
    group_id: Optional[int] = Query(None, description="群组ID筛选"),
):
    """
    获取红包任务/发送记录列表
    """
    try:
        # 基础查询
        base_query = db.query(Envelope)
        
        # 状态筛选
        status_col = _col(Envelope, "status", "state")
        closed_col = _col(Envelope, "closed_at", "finished_at", "ended_at")
        remain_col = _col(Envelope, "remain_count", "left_count", "rest_count")
        
        if status == "active":
            if status_col:
                base_query = base_query.filter(status_col.in_(["OPEN", "ACTIVE", "ONGOING"]))
            else:
                if remain_col:
                    base_query = base_query.filter(remain_col > 0)
                if closed_col:
                    base_query = base_query.filter(closed_col.is_(None))
        elif status == "closed":
            if status_col:
                base_query = base_query.filter(status_col.in_(["CLOSED", "FINISHED", "ENDED"]))
            elif closed_col:
                base_query = base_query.filter(closed_col.isnot(None))
        elif status == "failed":
            if status_col:
                base_query = base_query.filter(status_col == "FAILED")
        
        # 搜索筛选
        if q:
            # 尝试按 ID 搜索
            try:
                task_id = int(q)
                base_query = base_query.filter(Envelope.id == task_id)
            except ValueError:
                # 按群组名称搜索（需要 join 群组表，这里简化处理）
                # 如果有 group_id 字段，可以按此搜索
                group_id_col = _col(Envelope, "group_id", "chat_id")
                if group_id_col:
                    # 这里简化，实际可能需要 join 群组表
                    pass
        
        # 群组筛选
        if group_id:
            group_id_col = _col(Envelope, "group_id", "chat_id")
            if group_id_col:
                base_query = base_query.filter(group_id_col == group_id)
        
        # 排序
        created_col = _col(Envelope, "created_at", "created", "ts")
        if created_col:
            base_query = base_query.order_by(desc(created_col))
        else:
            base_query = base_query.order_by(desc(Envelope.id))
        
        # 分页
        total = base_query.count()
        envelopes = base_query.offset((page - 1) * per_page).limit(per_page).all()
        
        # 转换为字典
        items = []
        for env in envelopes:
            token_col = _col(Envelope, "token", "asset", "currency")
            total_amount_col = _col(Envelope, "total_amount", "amount", "sum_amount")
            total_count_col = _col(Envelope, "total_count", "count", "pieces")
            remain_count_col = _col(Envelope, "remain_count", "left_count", "rest_count")
            created_at_col = _col(Envelope, "created_at", "created", "ts")
            closed_at_col = _col(Envelope, "closed_at", "finished_at", "ended_at")
            creator_id_col = _col(Envelope, "creator_id", "owner_id", "tg_id")
            group_id_col = _col(Envelope, "group_id", "chat_id")
            
            # 判断任务类型（简化：根据字段推断）
            task_type = "个人红包"  # 默认
            if group_id_col and getattr(env, group_id_col.key, None):
                task_type = "群发红包"
            
            # 判断状态
            env_status = "进行中"
            if status_col:
                status_val = getattr(env, status_col.key, None)
                if status_val in ["CLOSED", "FINISHED", "ENDED"]:
                    env_status = "成功"
                elif status_val == "FAILED":
                    env_status = "失败"
            elif closed_at_col and getattr(env, closed_at_col.key, None):
                env_status = "成功"
            
            item = {
                "id": env.id,
                "type": task_type,
                "group_name": f"群组 {getattr(env, group_id_col.key, 'N/A')}" if group_id_col else "个人",
                "amount": float(getattr(env, total_amount_col.key, 0)) if total_amount_col else 0.0,
                "count": int(getattr(env, total_count_col.key, 0)) if total_count_col else 0,
                "status": env_status,
                "created_at": getattr(env, created_at_col.key, None).isoformat() if created_at_col and getattr(env, created_at_col.key, None) else None,
                "remain_count": int(getattr(env, remain_count_col.key, 0)) if remain_count_col else 0,
            }
            items.append(item)
        
        total_pages = max(1, math.ceil(total / per_page))
        
        return JSONResponse({
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# ---------- REST API: 红包任务详情 ----------
@api_router.get("/tasks/{task_id}", response_class=JSONResponse)
def get_task_detail(
    task_id: int,
    db=Depends(db_session),
    sess=Depends(require_admin),
):
    """
    获取红包任务详情
    """
    try:
        info = _summary(db, task_id)
        
        # 获取领取明细
        rows, total = _claims_page(db, task_id, 1, 100)  # 获取前100条
        
        claims = []
        for ledger, user in rows:
            amount_col = _col(Ledger, "amount", "delta", "value")
            created_col = _col(Ledger, "created_at", "created", "ts")
            note_col = _col(Ledger, "note", "memo")
            
            claims.append({
                "user_id": user.tg_id if user else None,
                "username": getattr(user, "username", None) if user else None,
                "amount": float(getattr(ledger, amount_col.key, 0)) if amount_col else 0.0,
                "created_at": getattr(ledger, created_col.key, None).isoformat() if created_col and getattr(ledger, created_col.key, None) else None,
                "note": getattr(ledger, note_col.key, None) if note_col else None,
            })
        
        return JSONResponse({
            "id": task_id,
            "token": info.get("token"),
            "total_amount": info.get("total_amount"),
            "total_count": info.get("total_count"),
            "claimed_amount": info.get("claimed_amount"),
            "claimed_count": info.get("claimed_count"),
            "remain_amount": info.get("remain_amount"),
            "remain_count": info.get("remain_count"),
            "created_at": info.get("created_at").isoformat() if info.get("created_at") else None,
            "closed_at": info.get("closed_at").isoformat() if info.get("closed_at") else None,
            "creator": {
                "tg_id": info.get("creator").tg_id if info.get("creator") else None,
                "username": getattr(info.get("creator"), "username", None) if info.get("creator") else None,
            } if info.get("creator") else None,
            "lucky": info.get("lucky"),
            "claims": claims,
            "total_claims": total,
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# ---------- 路由 ----------
@router.get("/{eid}", response_class=HTMLResponse)
def envelope_detail(
    req: Request,
    eid: int,
    page: int = 1,
    per_page: int = 20,
    db=Depends(db_session),
    sess=Depends(require_admin),
):
    info = _summary(db, eid)
    rows, total = _claims_page(db, eid, page, per_page)
    total_pages = max(1, math.ceil(total / per_page)) if per_page else 1

    return req.app.state.templates.TemplateResponse(
        "envelopes_view.html",
        {
            "request": req,
            "title": t("admin.envelopes.title"),
            "nav_active": "envelopes",
            "eid": eid,
            "info": info,
            "rows": rows,        # 每条是 (Ledger, User)
            "page": page,
            "total_pages": total_pages,
        },
    )
