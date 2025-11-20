# web_admin/controllers/adjust.py
from __future__ import annotations

import re
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from typing import List, Tuple, Dict

from fastapi import APIRouter, Depends, Form, Query, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func

# i18n: 先尝试根级 i18n.py，失败再走 core.i18n.i18n
try:
    from i18n import t  # 优先根级
except Exception:
    from core.i18n.i18n import t  # 兜底路径

from web_admin.deps import (
    db_session,
    require_admin,
    GuardDangerOp,
    csrf_protect,     # ✅ 新增：POST 路由 CSRF 守卫
    issue_csrf,       # ✅ 新增：GET/预览页签发 CSRF
)
from models.user import User, get_balance, can_spend, update_balance
from models.ledger import LedgerType

router = APIRouter(prefix="/admin/adjust", tags=["admin-adjust"])

ALLOWED_ASSETS = {"USDT", "TON", "POINT", "ENERGY"}
DEC_PLACES = Decimal("0.000001")


# ---------- helpers ----------
def _split_users(raw: str) -> List[str]:
    """支持 ID / @username，逗号/空格/换行/分号/中文逗号 等分隔"""
    if not raw:
        return []
    raw = (
        raw.replace("，", ",")
           .replace("\r", ",")
           .replace("\n", ",")
           .replace("\t", ",")
           .replace(";", ",")
           .replace(" ", ",")
    )
    out = []
    for tok in raw.split(","):
        tok = tok.strip()
        if tok:
            out.append(tok)
    return out


def _resolve_single(db, token: str) -> User | None:
    """
    解析单个用户标识符（支持 tg_id 或 @username）
    - 纯数字（至少4位）：当作 tg_id 查找
    - 其他：当作 username 查找（不区分大小写，支持 @ 前缀）
    """
    token = token.strip()
    if not token:
        return None
    
    # 纯数字当作 tg_id
    if re.fullmatch(r"\d{4,}", token):
        try:
            tg_id = int(token)
            user = db.query(User).filter(User.tg_id == tg_id).first()
            return user
        except (ValueError, TypeError) as e:
            # 如果转换失败，继续尝试作为用户名查找
            pass
    
    # 去掉前缀 @，统一小写做不区分大小写匹配
    uname = token.lstrip("@").strip().lower()
    if not uname:
        return None
    
    # 注意：如果 username 为 None，func.lower() 会返回 None，需要处理 NULL 值
    # 使用 func.lower() 并确保 username IS NOT NULL
    from sqlalchemy import and_
    user = db.query(User).filter(
        and_(
            User.username.isnot(None),  # 确保 username 不为 NULL
            func.lower(User.username) == uname
        )
    ).first()
    return user


def _resolve_users(db, tokens: List[str]) -> Tuple[List[User], List[str]]:
    found, missing = [], []
    for tok in tokens:
        u = _resolve_single(db, tok)
        if u:
            found.append(u)
        else:
            missing.append(tok)
    return found, missing


def _parse_amount(asset: str, raw: str) -> Decimal:
    """POINT/ENERGY 必须为整数；其他币种保留 6 位小数，向下取整"""
    if asset in {"POINT", "ENERGY"}:
        try:
            val = Decimal(raw)
        except InvalidOperation:
            raise ValueError("invalid")
        if val != val.to_integral_value():
            raise ValueError("integer-only")
        return val
    else:
        try:
            val = Decimal(raw).quantize(DEC_PLACES, rounding=ROUND_DOWN)
        except InvalidOperation:
            raise ValueError("invalid")
        return val


# ---------- routes ----------
@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def adjust_form(req: Request, sess=Depends(require_admin)):
    # ✅ 为表单签发 CSRF
    csrf_token = issue_csrf(req)
    return req.app.state.templates.TemplateResponse(
        "adjust_form.html",
        {
            "request": req,
            "title": t("admin.adjust.title"),
            "nav_active": "adjust",
            "csrf_token": csrf_token,  # 模板隐藏字段使用
        },
    )


@router.post("/preview", response_class=HTMLResponse)
def adjust_preview(
    req: Request,
    users: str = Form(...),
    asset: str = Form(...),
    amount: str = Form(...),
    note: str = Form(""),
    _=Depends(csrf_protect),          # ✅ 预览也走 CSRF
    db=Depends(db_session),
    sess=Depends(require_admin),
):
    asset = asset.upper().strip()
    if asset not in ALLOWED_ASSETS:
        raise HTTPException(status_code=400, detail=t("admin.errors.validation"))

    try:
        delta = _parse_amount(asset, amount)
    except ValueError:
        raise HTTPException(status_code=400, detail=t("admin.errors.validation"))

    tokens = _split_users(users)
    resolved, missing = _resolve_users(db, tokens)

    rows: List[Dict] = []
    for u in resolved:
        before = get_balance(db, u.tg_id, asset)
        # 负数表示扣减，正数表示增加
        can = True
        reason = ""
        if delta < 0:
            can = can_spend(db, u.tg_id, asset, -delta)
            if not can:
                reason = t("admin.adjust.insufficient")
        after = before + delta if can else before
        rows.append(
            {
                "user": u,
                "asset": asset,
                "before": before,
                "delta": delta,
                "after": after,
                "can": can,
                "reason": reason,
            }
        )

    # ✅ 预览页继续下发一个新的 CSRF，防止重复提交/回退重提
    csrf_token = issue_csrf(req)
    return req.app.state.templates.TemplateResponse(
        "adjust_confirm.html",
        {
            "request": req,
            "title": t("admin.adjust.title"),
            "nav_active": "adjust",
            "rows": rows,
            "missing": missing,
            "asset": asset,
            "amount": str(delta),
            "note": note,
            "users_raw": users,       # 传给模板，避免 POST 到预览时丢 users 原文
            "csrf_token": csrf_token, # 确认提交按钮使用
        },
    )


@router.post("/do", response_class=HTMLResponse)
def adjust_do(
    req: Request,
    users: str = Form(...),
    asset: str = Form(...),
    amount: str = Form(...),
    note: str = Form(""),
    _=Depends(csrf_protect),          # ✅ 执行提交必须通过 CSRF
    db=Depends(db_session),
    sess=Depends(GuardDangerOp(10)),  # 高危操作：要求最近 10 分钟 2FA
):
    asset = asset.upper().strip()
    if asset not in ALLOWED_ASSETS:
        raise HTTPException(status_code=400, detail=t("admin.errors.validation"))

    try:
        delta = _parse_amount(asset, amount)
    except ValueError:
        raise HTTPException(status_code=400, detail=t("admin.errors.validation"))

    tokens = _split_users(users)
    resolved, missing = _resolve_users(db, tokens)

    ok, fail = 0, 0
    results: List[Dict] = []

    for u in resolved:
        try:
            # 扣减前校验
            if delta < 0 and not can_spend(db, u.tg_id, asset, -delta):
                results.append({"u": u, "ok": False, "msg": t("admin.adjust.insufficient")})
                fail += 1
                continue
            # 记账与更新（写入 ledger）
            # 如果需要记录操作人信息，将其追加到 note 中
            operator_note = note[:120] if note else ""
            if sess.get("tg_id"):
                operator_info = f"操作人: {sess.get('tg_id')}"
                if operator_note:
                    operator_note = f"{operator_note} | {operator_info}"
                else:
                    operator_note = operator_info
            update_balance(
                db,
                u.tg_id,
                asset,
                delta,
                write_ledger=True,
                ltype=LedgerType.ADJUSTMENT,
                note=operator_note if operator_note else None,
            )
            ok += 1
            results.append({"u": u, "ok": True, "msg": t("admin.toast.done") or "OK"})
        except Exception as e:
            fail += 1
            # 将错误信息转换为中文友好提示
            error_msg = str(e)
            if "operator_id" in error_msg.lower():
                error_msg = "系统错误：函数参数配置错误。请联系技术支持。"
            elif "INSUFFICIENT_BALANCE" in error_msg:
                error_msg = "余额不足：无法扣减，用户余额不足以完成此次操作。"
            elif "no such table" in error_msg.lower():
                error_msg = "数据库错误：数据表不存在。请联系系统管理员检查数据库配置。"
            elif "connection" in error_msg.lower() and "refused" in error_msg.lower():
                error_msg = "数据库连接错误：无法连接到数据库。请检查数据库服务状态。"
            elif "UNIQUE constraint failed" in error_msg or "duplicate" in error_msg.lower():
                error_msg = "数据冲突：记录已存在，无法重复创建。"
            else:
                # 保留原始错误信息，但添加中文说明
                error_msg = f"操作失败：{error_msg}"
            results.append({"u": u, "ok": False, "msg": error_msg})

    db.commit()

    # ✅ 执行完毕后，返回页面再签发一个新的 CSRF（避免刷新/回退导致重复提交）
    csrf_token = issue_csrf(req)
    return req.app.state.templates.TemplateResponse(
        "adjust_confirm.html",
        {
            "request": req,
            "title": t("admin.adjust.title"),
            "nav_active": "adjust",
            "executed": True,
            "asset": asset,
            "amount": str(delta),
            "note": note,
            "results": results,
            "missing": missing,
            "success_count": ok,
            "fail_count": fail,
            "csrf_token": csrf_token,
        },
    )
