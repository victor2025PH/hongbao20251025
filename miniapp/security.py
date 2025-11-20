# -*- coding: utf-8 -*-
"""JWT 工具：簽發 / 驗證 / 黑名單管理。"""

from __future__ import annotations

from datetime import datetime, timedelta, UTC
import time
from threading import RLock
from typing import Any, Dict, Iterable, Optional, Tuple
from uuid import uuid4

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from config.settings import settings

_ALGORITHM = "HS256"
_BLACKLIST: Dict[str, datetime] = {}
_LOCK = RLock()


def _purge_blacklist() -> None:
    now = datetime.now(UTC)
    expired = [key for key, value in _BLACKLIST.items() if value <= now]
    for key in expired:
        _BLACKLIST.pop(key, None)


def blacklist_jti(jti: str, expires_at: datetime) -> None:
    with _LOCK:
        _purge_blacklist()
        _BLACKLIST[jti] = expires_at


def is_token_blacklisted(jti: Optional[str]) -> bool:
    if not jti:
        return False
    with _LOCK:
        _purge_blacklist()
        expiry = _BLACKLIST.get(jti)
        return bool(expiry and expiry > datetime.now(UTC))


def create_access_token(
    *,
    subject: str,
    tg_id: int,
    scopes: Iterable[str] = (),
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_seconds: Optional[int] = None,
) -> Tuple[str, datetime]:
    ttl = expires_seconds or settings.MINIAPP_JWT_EXPIRE_SECONDS
    now_ts = int(time.time())
    expire_ts = now_ts + max(1, ttl)
    now = datetime.fromtimestamp(now_ts, UTC)
    expire_at = datetime.fromtimestamp(expire_ts, UTC)
    jti = str(uuid4())
    payload: Dict[str, Any] = {
        "iss": settings.MINIAPP_JWT_ISSUER,
        "sub": subject,
        "iat": now_ts,
        "exp": expire_ts,
        "jti": jti,
        "scope": " ".join(scopes),
        "tg_id": tg_id,
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, settings.MINIAPP_JWT_SECRET, algorithm=_ALGORITHM)
    return token, expire_at


def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(  # type: ignore[no-any-return]
        token,
        settings.MINIAPP_JWT_SECRET,
        algorithms=[_ALGORITHM],
        issuer=settings.MINIAPP_JWT_ISSUER,
        options={"verify_aud": False},
    )


def get_expires_in(expire_at: datetime) -> int:
    remaining = int((expire_at - datetime.now(UTC)).total_seconds())
    return remaining if remaining > 0 else 0


__all__ = [
    "create_access_token",
    "decode_access_token",
    "blacklist_jti",
    "is_token_blacklisted",
    "get_expires_in",
    "ExpiredSignatureError",
    "InvalidTokenError",
]
