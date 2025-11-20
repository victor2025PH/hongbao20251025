# services/hongbao_service.py
# -*- coding: utf-8 -*-
"""
红包业务服务层：
- create_envelope(user_id, token, total_amount, total_count)
- grab_envelope(user_id, envelope_id) -> (成功?, 文案, 剩余数量)
- close_envelope_if_finished(envelope_id) -> 排行榜文案
"""

from __future__ import annotations
from decimal import Decimal
from typing import Tuple, Optional, List

from sqlalchemy.orm import Session

from models.db import get_session
from models.user import User, update_balance, get_balance
from models.ledger import add_ledger_entry, LedgerType
from models.envelope import Envelope, EnvelopeShare

# 兼容旧命名
GrabRecord = EnvelopeShare

# EnvelopeStatus 不存在，使用字符串常量
class EnvelopeStatus:
    OPEN = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"
from core.i18n.i18n import t


# ========== 发红包 ==========

def create_envelope(user_id: int, token: str, total_amount: Decimal, total_count: int,
                    lang: str = "zh") -> Tuple[bool, str, Optional[int]]:
    """
    发红包：扣款并生成 Envelope
    返回 (成功?, 文案, envelope_id)
    """
    with get_session() as s:
        # 检查余额
        u = s.query(User).filter_by(tg_id=user_id).first()
        if not u:
            return False, t("hongbao.no_user", lang), None

        bal = get_balance(s, u, token)
        if bal < total_amount:
            return False, t("hongbao.not_enough", lang, token=token), None

        # 扣款
        update_balance(s, u, token, -total_amount)
        add_ledger_entry(
            s, user_tg_id=user_id, ltype=LedgerType.SEND,
            token=token, amount=-total_amount, ref_type="ENVELOPE", ref_id="NEW",
            note=f"发红包 {total_amount} {token}"
        )

        # 新建红包（使用正确的字段名）
        from models.envelope import HBMode
        mode = HBMode.POINT if token == "POINT" else (HBMode.USDT if token == "USDT" else HBMode.TON)
        env = Envelope(
            sender_tg_id=user_id,
            chat_id=-1000000000,  # 默认聊天 ID
            mode=mode,
            total_amount=Decimal(total_amount),
            shares=total_count,
            status=EnvelopeStatus.OPEN,
        )
        s.add(env)
        s.flush()
        return True, t("hongbao.created", lang, amount=total_amount, count=total_count, token=token), env.id


# ========== 抢红包 ==========

def grab_envelope(user_id: int, envelope_id: int, lang: str = "zh") -> Tuple[bool, str, int]:
    """
    抢红包逻辑：
    - 检查是否已抢过
    - 随机金额分配（或均分）
    - 更新 Envelope / GrabRecord
    - 返回 (成功?, 文案, 剩余数量)
    """
    import random
    from sqlalchemy import func
    with get_session() as s:
        env = s.query(Envelope).get(envelope_id)
        if not env or env.status != EnvelopeStatus.OPEN:
            return False, t("hongbao.finished", lang), 0

        # 计算已领取数量和金额
        grabbed_count = s.query(func.count(GrabRecord.id)).filter(
            GrabRecord.envelope_id == env.id
        ).scalar() or 0
        grabbed_amount = s.query(func.coalesce(func.sum(GrabRecord.amount), 0)).filter(
            GrabRecord.envelope_id == env.id
        ).scalar() or Decimal("0")
        
        # 计算剩余数量和金额
        remain_count = int(env.shares) - int(grabbed_count)
        remain_amount = Decimal(str(env.total_amount)) - Decimal(str(grabbed_amount))
        token = env.mode.value if hasattr(env.mode, 'value') else str(env.mode)

        # 检查是否抢过
        grabbed = s.query(GrabRecord).filter_by(envelope_id=env.id, user_tg_id=user_id).first()
        if grabbed:
            return False, t("hongbao.already", lang), remain_count

        # 分配金额
        if remain_count == 1:
            amt = remain_amount
        else:
            max_amt = float(remain_amount) / remain_count * 2
            amt = Decimal(str(round(random.uniform(0.01, max_amt), 2)))
            if amt > remain_amount:
                amt = remain_amount

        # 记录领取
        rec = GrabRecord(envelope_id=env.id, user_tg_id=user_id, amount=amt)
        s.add(rec)

        # 如果已领完，更新状态
        if remain_count <= 1 or remain_amount <= amt:
            env.status = EnvelopeStatus.CLOSED
            s.add(env)

        # 更新余额
        u = s.query(User).filter_by(tg_id=user_id).first() or User(tg_id=user_id)
        s.add(u)
        update_balance(s, u, token, amt)
        add_ledger_entry(
            s, user_tg_id=user_id, ltype=LedgerType.GRAB,
            token=token, amount=amt, ref_type="ENVELOPE", ref_id=str(env.id),
            note="抢红包"
        )
        s.commit()

        # 计算新的剩余数量
        new_remain_count = remain_count - 1
        return True, t("hongbao.grabbed", lang, amount=amt, token=token), new_remain_count


# ========== 完结 & 排行榜 ==========

def close_envelope_if_finished(envelope_id: int, lang: str = "zh") -> Optional[str]:
    """
    如果红包已领完 → 返回排行榜文案
    """
    with get_session() as s:
        env = s.query(Envelope).get(envelope_id)
        if not env or env.status != EnvelopeStatus.CLOSED:
            return None

        # 抓取所有记录
        recs: List[GrabRecord] = (
            s.query(GrabRecord).filter_by(envelope_id=envelope_id).order_by(GrabRecord.amount.desc()).all()
        )
        if not recs:
            return None

        token = env.mode.value if hasattr(env.mode, 'value') else str(env.mode)
        lines = [t("rank.title", lang)]
        for r in recs:
            user_line = t("rank.item", lang, user=r.user_tg_id, amount=float(r.amount), token=token)
            lines.append(user_line)

        lucky = recs[0]
        lines.append("")
        lines.append(t("rank.lucky", lang, user=lucky.user_tg_id, amount=float(lucky.amount), token=token))

        return "\n".join(lines)
