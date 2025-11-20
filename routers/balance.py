# routers/balance.py
# -*- coding: utf-8 -*-
"""
我的资产（余额）与账单：
- balance:main / bal:main            → 资产总览
- balance:USDT / balance:TON / balance:POINT → 分币种明细（余额 + 最近流水）
- balance:history / bal:history      → 最近流水（全部币种），默认近10条，可扩展分页

说明：
1) 兼容你项目里的不同回调前缀：同时支持 bal:* 与 balance:*
2) 只依赖 models.user 与 models.ledger 的基础字段：Ledger(user_tg_id, type, token, amount/value, created_at, note)
3) i18n 文案全部走 t()；若词条缺失，也有合理兜底
4) 新增 ledger 类型的通用 i18n 逻辑：优先 t('types.<NAME>')，同时兼容 SEND/GRAB → HONGBAO_SEND/HONGBAO_GRAB 的别名
"""

from __future__ import annotations
import logging
import re
from typing import List, Dict, Tuple, Any, Sequence, Optional
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from core.i18n.i18n import t
from core.utils.keyboards import asset_menu, back_home_kb
from models.db import get_session
from models.user import User, get_balance_summary
from models.ledger import Ledger, LedgerType

# ==== 新增：服务实现所需 ====
from datetime import datetime, UTC
from time import perf_counter
from decimal import Decimal, InvalidOperation
from sqlalchemy import func, and_

router = Router()
log = logging.getLogger("balance")


# ---------- 工具 ----------
def _canon_lang(code: str | None) -> str:
    if not code:
        return "zh"
    c = str(code).strip().lower()
    if c.startswith("zh"):
        return "zh"
    if c.startswith("en"):
        return "en"
    return "zh"


def _db_lang(user_id: int, fallback_user) -> str:
    with get_session() as s:
        u = s.query(User).filter_by(tg_id=user_id).first()
        if u and getattr(u, "language", None):
            return _canon_lang(u.language)
    return _canon_lang(getattr(fallback_user, "language_code", None))


def _amt_attr() -> str:
    # 兼容有的库叫 amount、有的叫 value
    if hasattr(Ledger, "amount"):
        return "amount"
    if hasattr(Ledger, "value"):
        return "value"
    return "amount"


def _fmt6(v: float) -> str:
    """金额展示统一使用 2 位小数（不影响数据库内部 6 位精度）。"""
    try:
        return f"{float(v):.2f}"
    except Exception:
        return str(v)


def _fmt_token_amount(token: str, v) -> str:
    up = (token or "").upper()
    if up in ("POINT", "POINTS"):
        try:
            return str(int(v))
        except Exception:
            return str(v)
    return _fmt6(v)


def _token_i18n(tok: str, lang: str) -> str:
    u = (tok or "").upper()
    if u == "USDT":
        return t("asset.usdt", lang) or "USDT"
    if u == "TON":
        return t("asset.ton", lang) or "TON"
    if u in ("POINT", "POINTS"):
        return t("asset.points", lang) or "Points"
    return u or "—"


def _ledger_type_i18n(ltype: LedgerType, lang: str) -> str:
    """
    优先从 yml 的 types.* 取翻译（与项目现有包一致）；
    同时兼容一些历史/别名：
      SEND → HONGBAO_SEND
      GRAB → HONGBAO_GRAB
      ENVELOPE_GRAB → HONGBAO_GRAB
      ENVELOPE_SEND → HONGBAO_SEND
    若仍无匹配，则回退为枚举名本身。
    """
    name = (getattr(ltype, "name", None) or str(ltype) or "").strip()
    if not name:
        return ""

    # 1) 直接按 types.NAME
    key = f"types.{name}"
    val = t(key, lang)
    if val:
        return val

    # 2) 常见别名 → 规范枚举名
    alias = {
        "SEND": "HONGBAO_SEND",
        "GRAB": "HONGBAO_GRAB",
        "ENVELOPE_GRAB": "HONGBAO_GRAB",
        "ENVELOPE_SEND": "HONGBAO_SEND",
    }
    if name in alias:
        v2 = t(f"types.{alias[name]}", lang)
        if v2:
            return v2

    # 3) 早期键位（极少数遗留）：record.type.*
    legacy_map = {
        "SEND": "record.type.send",
        "GRAB": "record.type.grab",
        "RECHARGE": "record.type.recharge",
        "WITHDRAW": "record.type.withdraw",
        "ADJUSTMENT": "record.type.adjust",
        "ENVELOPE_GRAB": "record.type.grab",
    }
    if name in legacy_map:
        v3 = t(legacy_map[name], lang)
        if v3:
            return v3

    # 4) 最终兜底：原枚举名
    return name


def _sign_amount(token_or_label: str, v: float) -> str:
    # 显示有符号金额（+/-）；积分以整数展示
    up = (token_or_label or "").upper()
    if up in ("POINT", "POINTS", "⭐ POINTS", "⭐ 积分"):
        try:
            return f"{int(v):+d}"
        except Exception:
            return f"{v:+}"
    try:
        return f"{float(v):+,.2f}"
    except Exception:
        return f"{v:+}"


# ---------- 资产总览 ----------
@router.callback_query(F.data.in_({"balance:main", "bal:main"}))
async def balance_main(cb: CallbackQuery):
    lang = _db_lang(cb.from_user.id, cb.from_user)

    # 余额摘要
    summary = get_balance_summary(cb.from_user.id)
    usdt = float(summary.get("usdt", 0.0) or 0.0)
    ton = float(summary.get("ton", 0.0) or 0.0)
    pts = int(summary.get("point", 0) or 0)
    energy = int(summary.get("energy", 0) or 0)

    title = t("asset.title", lang) or "💼 My Assets"
    # 统一标签：优先 asset.energy → 其次 labels.energy → 再兜底
    energy_label = t("asset.energy", lang) or t("labels.energy", lang) or "⚡ Energy"
    points_label = t("asset.points", lang) or "⭐ Points"

    lines = [
        f"{title}",
        "────────────────",
        f"💵 USDT: {_fmt6(usdt)}",
        f"🔷 TON:  {_fmt6(ton)}",
        f"{points_label}: {pts}",
        f"{energy_label}: {energy}",
        "",
        t("asset.tip", lang) or "Use the buttons below to view details or recharge.",
    ]
    text = "\n".join(lines)

    kb = asset_menu(lang)
    try:
        await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except TelegramBadRequest:
        await cb.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await cb.answer()


# ---------- 分币种明细（余额 + 最近10条流水） ----------
@router.callback_query(F.data.regexp(r"^(?:balance|bal):(USDT|TON|POINT|POINTS)$"))
async def balance_token_detail(cb: CallbackQuery):
    lang = _db_lang(cb.from_user.id, cb.from_user)
    m = re.match(r"^(?:balance|bal):(USDT|TON|POINT|POINTS)$", cb.data or "")
    token = (m.group(1) if m else "USDT").upper()
    if token == "POINTS":
        token = "POINT"

    # 余额
    summary = get_balance_summary(cb.from_user.id)
    bal_map = {
        "USDT": float(summary.get("usdt", 0.0) or 0.0),
        "TON": float(summary.get("ton", 0.0) or 0.0),
        "POINT": int(summary.get("point", 0) or 0),
    }
    bal = bal_map.get(token, 0)

    # 流水（最近10条，按时间倒序）
    amt_field = _amt_attr()
    with get_session() as s:
        q = (
            s.query(Ledger)
            .filter(Ledger.user_tg_id == cb.from_user.id)
            .filter((Ledger.token == token) | (Ledger.token == token.capitalize()))
            .order_by(getattr(Ledger, "created_at").desc())
            .limit(10)
        )
        rows: List[Ledger] = q.all()

    title = (
        t("asset.detail.title", lang, token=_token_i18n(token, lang))
        or f"📄 {_token_i18n(token, lang)} Details"
    )
    header = [
        title,
        "────────────────",
        (
            t(
                "asset.balance",
                lang,
                amount=_fmt_token_amount(token, bal),
                token=_token_i18n(token, lang),
            )
            or f"Balance: {_fmt_token_amount(token, bal)} {_token_i18n(token, lang)}"
        ),
        "",
        t("record.recent10", lang) or "Recent 10 records:",
    ]
    body = []
    if not rows:
        body.append(t("record.none", lang) or "📭 No transactions yet")
    else:
        for r in rows:
            kind = _ledger_type_i18n(getattr(r, "type"), lang)
            val = float(getattr(r, amt_field) or 0.0)
            ts = getattr(r, "created_at", None)
            ts_s = ts.strftime("%Y-%m-%d %H:%M") if ts else ""
            note = getattr(r, "note", "") or ""
            body.append(f"• {ts_s} {kind} {_sign_amount(token, val)}  {note}")

    text = "\n".join(header + [""] + body)
    kb = back_home_kb(lang)
    try:
        await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except TelegramBadRequest:
        await cb.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await cb.answer()


# ---------- 最近流水（全部币种） ----------
@router.callback_query(F.data.in_({"balance:history", "bal:history"}))
async def balance_history(cb: CallbackQuery):
    lang = _db_lang(cb.from_user.id, cb.from_user)
    amt_field = _amt_attr()

    with get_session() as s:
        rows: List[Ledger] = (
            s.query(Ledger)
            .filter(Ledger.user_tg_id == cb.from_user.id)
            .order_by(getattr(Ledger, "created_at").desc())
            .limit(10)
            .all()
        )

    title = t("record.title", lang) or "📜 Records"
    sub = t("record.recent10", lang) or "Recent 10 records:"
    header = [title, "────────────────", sub]
    body = []
    if not rows:
        body.append(t("record.none", lang) or "📭 No transactions yet")
    else:
        for r in rows:
            kind = _ledger_type_i18n(getattr(r, "type"), lang)
            tok_label = _token_i18n(getattr(r, "token", ""), lang)
            # tok_label 用于判断积分格式，也兼容 Points/积分
            val = float(getattr(r, amt_field) or 0.0)
            ts = getattr(r, "created_at", None)
            ts_s = ts.strftime("%Y-%m-%d %H:%M") if ts else ""
            note = getattr(r, "note", "") or ""
            body.append(f"• {ts_s} {kind} {_sign_amount(tok_label, val)} {tok_label}  {note}")

    text = "\n".join(header + [""] + body)
    kb = back_home_kb(lang)
    try:
        await cb.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except TelegramBadRequest:
        await cb.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await cb.answer()


# ===================================================================
#                新增：批量清零服务（供路由调用）
# ===================================================================

def _user_balance_fields() -> Tuple[str, str, str]:
    """
    兼容不同项目里的用户余额字段命名：
      - 常见：usdt_balance / ton_balance / point_balance
      - 也见过：usdt / ton / point
    """
    candidates = [
        ("usdt_balance", "ton_balance", "point_balance"),
        ("usdt", "ton", "point"),
    ]
    for a, b, c in candidates:
        if hasattr(User, a) and hasattr(User, b) and hasattr(User, c):
            return a, b, c
    # 最后兜底仍给常用名，失败就让异常暴露出来，方便你修字段
    return ("usdt_balance", "ton_balance", "point_balance")


def _ledger_type_reset() -> LedgerType:
    # 优先使用 LedgerType.RESET，没有则回落为 ADJUSTMENT
    try:
        return getattr(LedgerType, "RESET")
    except Exception:
        return LedgerType.ADJUSTMENT


def _mk_batch_id(prefix: str, operator_id: int) -> str:
    now = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}#{now}-{operator_id}"


def _decimalize(val: Any) -> Decimal:
    try:
        return Decimal(str(val or "0"))
    except (InvalidOperation, Exception):
        return Decimal(0)


def _totals_zero() -> Dict[str, Decimal]:
    return {"USDT": Decimal(0), "TON": Decimal(0), "POINT": Decimal(0)}


def reset_all_balances(note: str = "", operator_id: int = 0) -> Dict[str, Any]:
    """
    将所有用户的 USDT/TON/POINT 余额归零：
      1) 为每个非零余额写入一条负向流水（type=RESET 或 ADJUSTMENT）
      2) 将用户表余额字段置 0
    单事务；返回受影响用户数、各资产总扣减量、批次号与耗时。
    """
    t0 = perf_counter()
    amt_field = _amt_attr()
    reset_type = _ledger_type_reset()
    usdt_f, ton_f, pt_f = _user_balance_fields()
    batch_id = _mk_batch_id("RESET_ALL", operator_id)
    base_note = (note or "").strip()
    final_note = f"{batch_id} op={operator_id}" + (f" | {base_note}" if base_note else "")

    affected_users = 0
    totals = _totals_zero()

    with get_session() as s:
        # 查出所有有余额的用户
        users: List[User] = (
            s.query(User)
            .filter(
                (getattr(User, usdt_f) != 0) |
                (getattr(User, ton_f) != 0) |
                (getattr(User, pt_f) != 0)
            )
            .all()
        )

        if not users:
            elapsed = f"{perf_counter() - t0:.2f}s"
            return {
                "affected_users": 0,
                "usdt_total": "0",
                "ton_total": "0",
                "point_total": "0",
                "batch_id": batch_id,
                "elapsed": elapsed,
            }

        affected_users = len(users)

        # 批量写流水、置零
        for u in users:
            uid = int(getattr(u, "tg_id"))
            usdt = _decimalize(getattr(u, usdt_f))
            ton  = _decimalize(getattr(u, ton_f))
            pts  = _decimalize(getattr(u, pt_f))

            # 为每个非零资产写一条负向流水
            if usdt != 0:
                entry = Ledger(
                    user_tg_id=uid,
                    token="USDT",
                    type=reset_type,
                    note=final_note,
                )
                setattr(entry, amt_field, -usdt)
                s.add(entry)
                totals["USDT"] += usdt

            if ton != 0:
                entry = Ledger(
                    user_tg_id=uid,
                    token="TON",
                    type=reset_type,
                    note=final_note,
                )
                setattr(entry, amt_field, -ton)
                s.add(entry)
                totals["TON"] += ton

            if pts != 0:
                entry = Ledger(
                    user_tg_id=uid,
                    token="POINT",
                    type=reset_type,
                    note=final_note,
                )
                # 积分也按 Decimal 走，但展示会转 int
                setattr(entry, amt_field, -pts)
                s.add(entry)
                totals["POINT"] += pts

            # 将余额置 0
            setattr(u, usdt_f, Decimal(0))
            setattr(u, ton_f,  Decimal(0))
            setattr(u, pt_f,   Decimal(0))

        s.commit()

    elapsed = f"{perf_counter() - t0:.2f}s"
    return {
        "affected_users": affected_users,
        "usdt_total": str(totals["USDT"].quantize(Decimal("0.000000"))),
        "ton_total":  str(totals["TON"].quantize(Decimal("0.000000"))),
        "point_total": str(int(totals["POINT"])),
        "batch_id": batch_id,
        "elapsed": elapsed,
    }


def reset_selected_balances(user_ids: Sequence[int], note: str = "", operator_id: int = 0) -> Dict[str, Any]:
    """
    将“指定用户”的 USDT/TON/POINT 余额清零：
      1) 每个用户每种非零资产写入负向流水（type=RESET 或 ADJUSTMENT）
      2) 将用户表余额字段置 0
    每个用户在一个 try 块内，局部失败不影响其他人。返回成功/失败统计与总扣减。
    """
    t0 = perf_counter()
    amt_field = _amt_attr()
    reset_type = _ledger_type_reset()
    usdt_f, ton_f, pt_f = _user_balance_fields()
    batch_id = _mk_batch_id("RESET_SELECTED", operator_id)
    base_note = (note or "").strip()
    final_note = f"{batch_id} op={operator_id}" + (f" | {base_note}" if base_note else "")

    ids = [int(x) for x in list(dict.fromkeys(user_ids or [])) if str(x).isdigit()]
    if not ids:
        return {
            "success_count": 0,
            "fail_count": 0,
            "errors_by_user": {},
            "batch_id": batch_id,
            "totals": {"USDT": "0", "TON": "0", "POINT": "0"},
        }

    success = 0
    fail = 0
    errors: Dict[int, str] = {}
    totals = _totals_zero()

    with get_session() as s:
        # 一次性查出所有目标
        rows: List[User] = (
            s.query(User)
            .filter(User.tg_id.in_(ids))
            .all()
        )
        by_id = {int(getattr(u, "tg_id")): u for u in rows}

        for uid in ids:
            u = by_id.get(uid)
            if not u:
                fail += 1
                errors[uid] = "NOT_FOUND"
                continue

            try:
                usdt = _decimalize(getattr(u, usdt_f))
                ton  = _decimalize(getattr(u, ton_f))
                pts  = _decimalize(getattr(u, pt_f))

                # 若三项均为 0，当作成功但不写流水
                wrote = False

                if usdt != 0:
                    entry = Ledger(
                        user_tg_id=uid,
                        token="USDT",
                        type=reset_type,
                        note=final_note,
                    )
                    setattr(entry, amt_field, -usdt)
                    s.add(entry)
                    totals["USDT"] += usdt
                    wrote = True

                if ton != 0:
                    entry = Ledger(
                        user_tg_id=uid,
                        token="TON",
                        type=reset_type,
                        note=final_note,
                    )
                    setattr(entry, amt_field, -ton)
                    s.add(entry)
                    totals["TON"] += ton
                    wrote = True

                if pts != 0:
                    entry = Ledger(
                        user_tg_id=uid,
                        token="POINT",
                        type=reset_type,
                        note=final_note,
                    )
                    setattr(entry, amt_field, -pts)
                    s.add(entry)
                    totals["POINT"] += pts
                    wrote = True

                # 将余额置 0
                setattr(u, usdt_f, Decimal(0))
                setattr(u, ton_f,  Decimal(0))
                setattr(u, pt_f,   Decimal(0))

                success += 1
            except Exception as e:
                fail += 1
                errors[uid] = e.__class__.__name__

        s.commit()

    return {
        "success_count": success,
        "fail_count": fail,
        "errors_by_user": errors,
        "batch_id": batch_id,
        "totals": {
            "USDT": str(totals["USDT"].quantize(Decimal("0.000000"))),
            "TON":  str(totals["TON"].quantize(Decimal("0.000000"))),
            "POINT": str(int(totals["POINT"])),
        },
    }
