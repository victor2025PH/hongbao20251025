# web_admin/controllers/redpacket.py
# -*- coding: utf-8 -*-
"""
红包功能 API 控制器：
- POST /admin/api/v1/redpacket/send - 发送红包到 Telegram 群组
- POST /admin/api/v1/redpacket/{envelope_id}/grab - 抢红包
- GET /admin/api/v1/redpacket/{envelope_id} - 查询红包信息
- GET /admin/api/v1/redpacket/balance - 查询用户余额
- GET /admin/api/v1/redpacket/history - 查询红包历史记录
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from models.db import Session
from models.user import User, get_or_create_user, update_balance
from models.envelope import Envelope, EnvelopeShare, HBMode, create_envelope, get_envelope_summary, HBError, HBNotFound, HBFinished, HBDuplicatedGrab
from models.ledger import add_ledger_entry, LedgerType
from web_admin.deps import require_admin, db_session
from routers.hongbao import send_envelope_card_to_chat

logger = logging.getLogger("web_admin.redpacket")

router = APIRouter(prefix="/admin/api/v1/redpacket", tags=["redpacket"])


# ================= Pydantic 模型 =================

class SendRedPacketRequest(BaseModel):
    chat_id: int = Field(..., description="Telegram 群组 ID（负数）")
    token: str = Field(..., description="币种：USDT / TON / POINT")
    total_amount: float = Field(..., gt=0, description="红包总金额")
    shares: int = Field(..., gt=0, description="红包份数")
    note: Optional[str] = Field(None, max_length=120, description="祝福语（可选）")


class SendRedPacketResponse(BaseModel):
    success: bool
    envelope_id: int
    message: str


class GrabRedPacketResponse(BaseModel):
    success: bool
    amount: str
    token: str
    remain_shares: int
    message: str


class RedPacketInfoResponse(BaseModel):
    id: int
    chat_id: int
    sender_tg_id: int
    token: str
    total_amount: str
    shares: int
    remain_shares: int
    remain_amount: str
    note: Optional[str]
    status: str
    is_finished: bool
    created_at: str
    activated_at: Optional[str]


class UserBalanceResponse(BaseModel):
    tg_id: int
    username: Optional[str]
    balance_usdt: str
    balance_ton: str
    balance_point: str


class RedPacketHistoryItem(BaseModel):
    id: int
    chat_id: int
    sender_tg_id: int
    token: str
    total_amount: str
    shares: int
    remain_shares: int
    note: Optional[str]
    status: str
    created_at: str


class RedPacketHistoryResponse(BaseModel):
    items: List[RedPacketHistoryItem]
    total: int
    page: int
    limit: int


# ================= 工具函数 =================

def _get_bot_instance():
    """
    获取 Telegram Bot 实例（用于发送红包卡片到群组）
    """
    try:
        from aiogram import Bot
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        from config.settings import settings
        
        # 创建新的 Bot 实例（使用相同的 BOT_TOKEN）
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        return bot
    except Exception as e:
        logger.exception("Failed to create bot instance: %s", e)
        raise HTTPException(status_code=500, detail="无法创建 Bot 实例")


def _quant_amt(token: str, value: float) -> Decimal:
    """量化金额"""
    tok = token.upper()
    if tok in ("USDT", "TON"):
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding="ROUND_DOWN")
    return Decimal(int(Decimal(str(value))))


def _format_amount(amount: Decimal, token: str) -> str:
    """格式化金额显示"""
    tok = token.upper()
    if tok in ("USDT", "TON"):
        return f"{float(amount):.2f}"
    return str(int(amount))


# ================= API 路由 =================

@router.post("/send", response_class=JSONResponse)
async def send_red_packet(
    request: SendRedPacketRequest,
    req: Request,
    db: Session = Depends(db_session),
    sess=Depends(require_admin),
):
    """
    发送红包到 Telegram 群组
    
    1. 验证用户身份和余额
    2. 创建红包记录（扣款）
    3. 通过 Bot API 发送红包卡片到群组
    """
    try:
        # 1. 获取当前用户
        tg_id = sess.get("tg_id")
        if not tg_id:
            raise HTTPException(status_code=401, detail="未登录")
        
        user = get_or_create_user(db, tg_id=int(tg_id))
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 2. 验证币种
        token = request.token.upper()
        if token not in ("USDT", "TON", "POINT"):
            raise HTTPException(status_code=400, detail="不支持的币种，仅支持 USDT / TON / POINT")
        
        # 3. 量化金额
        amount_total = _quant_amt(token, request.total_amount)
        if amount_total <= 0:
            raise HTTPException(status_code=400, detail="红包金额必须大于 0")
        
        if request.shares < 1:
            raise HTTPException(status_code=400, detail="红包份数必须大于等于 1")
        
        # 4. 检查余额
        balance = user.get_balance(token)
        if balance < amount_total:
            raise HTTPException(
                status_code=400,
                detail=f"余额不足：当前 {token} 余额为 {_format_amount(Decimal(str(balance)), token)}，需要 {_format_amount(amount_total, token)}"
            )
        
        # 5. 创建红包（在事务中扣款并创建记录）
        try:
            # 扣款
            update_balance(db, user, token, -amount_total)
            
            # 记录流水
            add_ledger_entry(
                db,
                user_tg_id=int(tg_id),
                ltype=LedgerType.SEND if hasattr(LedgerType, "SEND") else LedgerType.ADJUSTMENT,
                token=token,
                amount=-amount_total,
                ref_type="ENVELOPE",
                ref_id="NEW",
                note=f"发红包 {_format_amount(amount_total, token)} {token}",
            )
            
            # 创建红包
            env = create_envelope(
                db,
                chat_id=int(request.chat_id),
                sender_tg_id=int(tg_id),
                mode=token,
                total_amount=amount_total,
                shares=int(request.shares),
                note=request.note or "",
                activate=True,
            )
            db.commit()
            
            logger.info(
                "Red packet created: envelope_id=%s, user=%s, chat_id=%s, token=%s, amount=%s, shares=%s",
                env.id, tg_id, request.chat_id, token, amount_total, request.shares
            )
            
        except Exception as e:
            db.rollback()
            logger.exception("Failed to create red packet: %s", e)
            raise HTTPException(status_code=500, detail=f"创建红包失败: {str(e)}")
        
        # 6. 通过 Bot API 发送红包卡片到群组
        try:
            bot = _get_bot_instance()
            await send_envelope_card_to_chat(bot, int(request.chat_id), env.id, lang="zh")
            logger.info("Red packet card sent to chat: envelope_id=%s, chat_id=%s", env.id, request.chat_id)
        except Exception as e:
            logger.warning(
                "Failed to send red packet card to chat (envelope created): envelope_id=%s, chat_id=%s, error=%s",
                env.id, request.chat_id, e
            )
            # 红包已创建，但发送卡片失败，不影响红包本身
        
        return JSONResponse({
            "success": True,
            "envelope_id": int(env.id),
            "message": f"红包已发送到群组！红包 ID: {env.id}",
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in send_red_packet: %s", e)
        raise HTTPException(status_code=500, detail=f"发送红包失败: {str(e)}")


# 注意：具体路由（/balance、/history）必须在参数化路由（/{envelope_id}）之前定义
# 否则 FastAPI 会将 "balance" 和 "history" 当作 envelope_id 参数

@router.get("/balance", response_class=JSONResponse)
async def get_user_balance(
    req: Request,
    db: Session = Depends(db_session),
    sess=Depends(require_admin),
):
    """
    查询用户余额
    """
    try:
        tg_id = sess.get("tg_id")
        if not tg_id:
            raise HTTPException(status_code=401, detail="未登录")
        
        user = get_or_create_user(db, tg_id=int(tg_id))
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        from models.user import get_balance
        
        balance_usdt = get_balance(db, user, "USDT")
        balance_ton = get_balance(db, user, "TON")
        balance_point = get_balance(db, user, "POINT")
        
        return JSONResponse({
            "tg_id": int(user.tg_id),
            "username": user.username or None,
            "balance_usdt": _format_amount(Decimal(str(balance_usdt)), "USDT"),
            "balance_ton": _format_amount(Decimal(str(balance_ton)), "TON"),
            "balance_point": _format_amount(Decimal(str(balance_point)), "POINT"),
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in get_user_balance: %s", e)
        raise HTTPException(status_code=500, detail=f"查询余额失败: {str(e)}")


@router.get("/history", response_class=JSONResponse)
async def get_red_packet_history(
    req: Request,
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(db_session),
    sess=Depends(require_admin),
):
    """
    查询红包历史记录（当前用户发送或参与的红包）
    """
    try:
        tg_id = sess.get("tg_id")
        if not tg_id:
            raise HTTPException(status_code=401, detail="未登录")
        
        # 查询用户发送的红包
        sent_envelopes = db.query(Envelope).filter(
            Envelope.sender_tg_id == int(tg_id)
        ).order_by(Envelope.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        
        # 查询用户参与的红包（通过 EnvelopeShare）
        participated_ids = [
            share.envelope_id for share in db.query(EnvelopeShare).filter(
                EnvelopeShare.user_tg_id == int(tg_id)
            ).all()
        ]
        
        participated_envelopes = db.query(Envelope).filter(
            Envelope.id.in_(participated_ids) if participated_ids else False
        ).order_by(Envelope.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        
        # 合并并去重
        all_env_ids = set([e.id for e in sent_envelopes] + [e.id for e in participated_envelopes])
        all_envelopes = db.query(Envelope).filter(Envelope.id.in_(list(all_env_ids))).all()
        
        items = []
        for env in all_envelopes:
            grabbed_count = db.query(EnvelopeShare).filter(
                EnvelopeShare.envelope_id == env.id
            ).count()
            
            grabbed_amount = sum(
                Decimal(str(share.amount)) for share in db.query(EnvelopeShare).filter(
                    EnvelopeShare.envelope_id == env.id
                ).all()
            )
            remain_amount = Decimal(str(env.total_amount)) - grabbed_amount
            
            token = env.mode.value if hasattr(env.mode, "value") else str(env.mode)
            
            items.append({
                "id": int(env.id),
                "chat_id": int(env.chat_id),
                "token": token,
                "total_amount": _format_amount(Decimal(str(env.total_amount)), token),
                "remain_shares": int(env.shares - grabbed_count),
                "remain_amount": _format_amount(remain_amount, token),
                "status": env.status,
                "is_finished": bool(env.is_finished),
                "created_at": env.created_at.isoformat() if env.created_at else None,
                "is_sender": env.sender_tg_id == int(tg_id),
            })
        
        items.sort(key=lambda x: x["created_at"] or "", reverse=True)
        
        return JSONResponse({
            "items": items,
            "page": page,
            "limit": limit,
            "total": len(items),
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in get_red_packet_history: %s", e)
        raise HTTPException(status_code=500, detail=f"查询历史记录失败: {str(e)}")


@router.post("/{envelope_id}/grab", response_class=JSONResponse)
async def grab_red_packet(
    envelope_id: int,
    req: Request,
    db: Session = Depends(db_session),
    sess=Depends(require_admin),
):
    """
    抢红包
    
    1. 验证用户身份
    2. 检查红包状态
    3. 随机分配金额
    4. 更新余额和记录
    """
    try:
        # 1. 获取当前用户
        tg_id = sess.get("tg_id")
        if not tg_id:
            raise HTTPException(status_code=401, detail="未登录")
        
        user = get_or_create_user(db, tg_id=int(tg_id))
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 2. 查询红包
        env = db.query(Envelope).filter(Envelope.id == int(envelope_id)).first()
        if not env:
            raise HTTPException(status_code=404, detail="红包不存在")
        
        if env.is_finished or env.status != "active":
            raise HTTPException(status_code=400, detail="红包已结束")
        
        # 3. 检查是否已抢过
        existing = db.query(EnvelopeShare).filter(
            EnvelopeShare.envelope_id == env.id,
            EnvelopeShare.user_tg_id == int(tg_id),
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="您已经抢过这个红包了")
        
        # 4. 检查剩余份数
        grabbed_count = db.query(EnvelopeShare).filter(
            EnvelopeShare.envelope_id == env.id
        ).count()
        
        if grabbed_count >= env.shares:
            raise HTTPException(status_code=400, detail="红包已被抢完")
        
        # 5. 随机分配金额
        import random
        remain_amount = Decimal(str(env.total_amount)) - sum(
            Decimal(str(share.amount)) for share in db.query(EnvelopeShare).filter(
                EnvelopeShare.envelope_id == env.id
            ).all()
        )
        remain_shares = env.shares - grabbed_count
        
        if remain_shares == 1:
            # 最后一份，全部给
            amount = remain_amount
        else:
            # 随机分配（最大值不超过平均值的 2 倍）
            max_amount = float(remain_amount) / remain_shares * 2
            amount = Decimal(str(round(random.uniform(0.01, max_amount), 2)))
            if amount > remain_amount:
                amount = remain_amount
        
        # 6. 创建份额记录并更新余额
        try:
            share = EnvelopeShare(
                envelope_id=env.id,
                user_tg_id=int(tg_id),
                amount=amount,
            )
            db.add(share)
            
            # 更新用户余额
            token = env.mode.value if hasattr(env.mode, "value") else str(env.mode)
            update_balance(db, user, token, amount)
            
            # 记录流水
            add_ledger_entry(
                db,
                user_tg_id=int(tg_id),
                ltype=LedgerType.GRAB if hasattr(LedgerType, "GRAB") else LedgerType.ADJUSTMENT,
                token=token,
                amount=amount,
                ref_type="ENVELOPE",
                ref_id=str(env.id),
                note=f"抢红包 #{env.id}",
            )
            
            # 更新红包状态
            new_grabbed_count = grabbed_count + 1
            if new_grabbed_count >= env.shares:
                env.is_finished = True
                env.status = "closed"
            
            db.commit()
            
            logger.info(
                "Red packet grabbed: envelope_id=%s, user=%s, amount=%s %s",
                env.id, tg_id, amount, token
            )
            
            return JSONResponse({
                "success": True,
                "amount": _format_amount(amount, token),
                "token": token,
                "remain_shares": env.shares - new_grabbed_count,
                "message": f"恭喜！你抢到了 {_format_amount(amount, token)} {token}",
            })
            
        except Exception as e:
            db.rollback()
            logger.exception("Failed to grab red packet: %s", e)
            raise HTTPException(status_code=500, detail=f"抢红包失败: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in grab_red_packet: %s", e)
        raise HTTPException(status_code=500, detail=f"抢红包失败: {str(e)}")


@router.get("/{envelope_id}", response_class=JSONResponse)
async def get_red_packet_info(
    envelope_id: int,
    req: Request,
    db: Session = Depends(db_session),
    sess=Depends(require_admin),
):
    """
    查询红包信息
    """
    try:
        env = db.query(Envelope).filter(Envelope.id == int(envelope_id)).first()
        if not env:
            raise HTTPException(status_code=404, detail="红包不存在")
        
        # 查询已抢份数
        grabbed_count = db.query(EnvelopeShare).filter(
            EnvelopeShare.envelope_id == env.id
        ).count()
        
        # 计算剩余金额
        grabbed_amount = sum(
            Decimal(str(share.amount)) for share in db.query(EnvelopeShare).filter(
                EnvelopeShare.envelope_id == env.id
            ).all()
        )
        remain_amount = Decimal(str(env.total_amount)) - grabbed_amount
        
        token = env.mode.value if hasattr(env.mode, "value") else str(env.mode)
        
        return JSONResponse({
            "id": int(env.id),
            "chat_id": int(env.chat_id),
            "sender_tg_id": int(env.sender_tg_id),
            "token": token,
            "total_amount": _format_amount(Decimal(str(env.total_amount)), token),
            "shares": int(env.shares),
            "remain_shares": int(env.shares - grabbed_count),
            "remain_amount": _format_amount(remain_amount, token),
            "note": env.note or None,
            "status": env.status,
            "is_finished": bool(env.is_finished),
            "created_at": env.created_at.isoformat() if env.created_at else None,
            "activated_at": env.activated_at.isoformat() if env.activated_at else None,
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in get_red_packet_info: %s", e)
        raise HTTPException(status_code=500, detail=f"查询红包信息失败: {str(e)}")


# 注意：/balance 必须在 /{envelope_id} 之前定义，否则 FastAPI 会将 "balance" 当作 envelope_id 参数
@router.get("/balance", response_class=JSONResponse)
async def get_user_balance(
    req: Request,
    db: Session = Depends(db_session),
    sess=Depends(require_admin),
):
    """
    查询用户余额
    """
    try:
        tg_id = sess.get("tg_id")
        if not tg_id:
            raise HTTPException(status_code=401, detail="未登录")
        
        user = get_or_create_user(db, tg_id=int(tg_id))
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        from models.user import get_balance
        
        balance_usdt = get_balance(db, user, "USDT")
        balance_ton = get_balance(db, user, "TON")
        balance_point = get_balance(db, user, "POINT")
        
        return JSONResponse({
            "tg_id": int(user.tg_id),
            "username": user.username or None,
            "balance_usdt": _format_amount(Decimal(str(balance_usdt)), "USDT"),
            "balance_ton": _format_amount(Decimal(str(balance_ton)), "TON"),
            "balance_point": _format_amount(Decimal(str(balance_point)), "POINT"),
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in get_user_balance: %s", e)
        raise HTTPException(status_code=500, detail=f"查询余额失败: {str(e)}")


@router.get("/history", response_class=JSONResponse)
async def get_red_packet_history(
    req: Request,
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(db_session),
    sess=Depends(require_admin),
):
    """
    查询红包历史记录（当前用户发送或参与的红包）
    """
    try:
        tg_id = sess.get("tg_id")
        if not tg_id:
            raise HTTPException(status_code=401, detail="未登录")
        
        # 查询当前用户发送或参与的红包
        # 方法1：查询发送的红包
        sent_envelopes = db.query(Envelope).filter(
            Envelope.sender_tg_id == int(tg_id)
        ).subquery()
        
        # 方法2：查询参与的红包（通过 EnvelopeShare）
        grabbed_envelope_ids = db.query(EnvelopeShare.envelope_id).filter(
            EnvelopeShare.user_tg_id == int(tg_id)
        ).subquery()
        
        # 合并查询
        from sqlalchemy import or_
        all_envelopes = db.query(Envelope).filter(
            or_(
                Envelope.sender_tg_id == int(tg_id),
                Envelope.id.in_(db.query(grabbed_envelope_ids))
            )
        ).order_by(Envelope.created_at.desc())
        
        total = all_envelopes.count()
        
        # 分页
        envelopes = all_envelopes.offset((page - 1) * limit).limit(limit).all()
        
        items = []
        for env in envelopes:
            # 查询已抢份数
            grabbed_count = db.query(EnvelopeShare).filter(
                EnvelopeShare.envelope_id == env.id
            ).count()
            
            token = env.mode.value if hasattr(env.mode, "value") else str(env.mode)
            
            items.append({
                "id": int(env.id),
                "chat_id": int(env.chat_id),
                "sender_tg_id": int(env.sender_tg_id),
                "token": token,
                "total_amount": _format_amount(Decimal(str(env.total_amount)), token),
                "shares": int(env.shares),
                "remain_shares": int(env.shares - grabbed_count),
                "note": env.note or None,
                "status": env.status,
                "created_at": env.created_at.isoformat() if env.created_at else None,
            })
        
        return JSONResponse({
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in get_red_packet_history: %s", e)
        raise HTTPException(status_code=500, detail=f"查询历史记录失败: {str(e)}")

