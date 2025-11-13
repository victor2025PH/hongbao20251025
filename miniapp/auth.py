# -*- coding: utf-8 -*-
"""MiniApp 登入流程：Telegram code / 密碼模式 -> JWT access_token"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.settings import is_admin, settings
from miniapp.security import create_access_token, get_expires_in
from models.db import get_db
from models.user import User, UserRole, get_or_create_user

try:  # pragma: no cover - 可选 bcrypt
    import bcrypt  # type: ignore

    _BCRYPT_AVAILABLE = True
except Exception:  # pragma: no cover
    _BCRYPT_AVAILABLE = False

router = APIRouter(tags=["auth"])

_ALLOWED_SKEW_SECONDS = 300  # Telegram code 时间戳允许的误差


class LoginProvider(str):
    TELEGRAM = "telegram"
    PASSWORD = "password"


class LoginRequest(BaseModel):
    provider: str = Field(..., pattern="^(telegram|password)$")
    telegram_code: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    tg_id: Optional[int] = None
    language: Optional[str] = None


class UserPayload(BaseModel):
    id: int
    tg_id: int
    username: Optional[str] = None
    roles: List[str]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPayload


def _build_user_payload(user: User) -> UserPayload:
    return UserPayload(
        id=user.id,
        tg_id=int(user.tg_id),
        username=user.username,
        roles=[user.role.value],
    )


def _verify_password_secret(stored: str, candidate: str) -> bool:
    if stored.lower().startswith("sha256:"):
        expected = stored.split(":", 1)[1].strip().lower()
        calc = hashlib.sha256(candidate.encode("utf-8")).hexdigest().lower()
        return hmac.compare_digest(calc, expected)
    if stored.lower().startswith("bcrypt:"):
        if not _BCRYPT_AVAILABLE:
            return False
        hashed = stored.split(":", 1)[1].strip().encode("utf-8")
        try:
            return bcrypt.checkpw(candidate.encode("utf-8"), hashed)  # type: ignore[arg-type]
        except Exception:
            return False
    return hmac.compare_digest(stored, candidate)


def _password_user_map() -> Dict[str, str]:
    raw = os.getenv("MINIAPP_PASSWORD_USERS", "").strip()
    result: Dict[str, str] = {}
    if not raw:
        return result
    for chunk in raw.split(","):
        part = chunk.strip()
        if not part or ":" not in part:
            continue
        user, secret = part.split(":", 1)
        user = user.strip()
        if not user:
            continue
        result[user] = secret.strip()
    return result


def _verify_password_account(username: str, password: str) -> bool:
    store = _password_user_map()
    secret = store.get(username)
    if secret is None:
        return False
    return _verify_password_secret(secret, password)


def _verify_telegram_code(code: str) -> Dict[str, Optional[str]]:
    try:
        tg_id_s, username, ts_s, signature = code.split(".", 3)
    except ValueError:  # pragma: no cover - 输入格式不对
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_telegram_code")

    secret = getattr(settings, "TELEGRAM_BOT_TOKEN", None) or settings.BOT_TOKEN
    message = f"{tg_id_s}.{username}.{ts_s}"
    expected = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="telegram_verification_failed")

    try:
        tg_id = int(tg_id_s)
        ts = int(ts_s)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_telegram_code")

    if abs(int(time.time()) - ts) > _ALLOWED_SKEW_SECONDS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="telegram_code_expired")

    normalized_username = username or None
    if normalized_username:
        normalized_username = normalized_username.strip() or None

    return {"tg_id": tg_id, "username": normalized_username}


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    provider = body.provider.lower()

    if provider == LoginProvider.TELEGRAM:
        if not body.telegram_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="telegram_code_required")
        payload = _verify_telegram_code(body.telegram_code)
        tg_id = int(payload["tg_id"])
        username = payload.get("username")
    elif provider == LoginProvider.PASSWORD:
        if not all([body.username, body.password, body.tg_id is not None]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username_password_required")
        if not _verify_password_account(body.username, body.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")
        tg_id = int(body.tg_id)
        username = body.username
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported_provider")

    try:
        user = get_or_create_user(
            db,
            tg_id=tg_id,
            username=username,
            lang=body.language,
            role=UserRole.USER,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="user_persist_failed")

    scopes: List[str] = ["miniapp"]
    admin_flag = is_admin(tg_id) or user.role == UserRole.ADMIN
    if admin_flag:
        scopes.append("miniapp:admin")

    token, expire_at = create_access_token(
        subject=str(user.id),
        tg_id=tg_id,
        scopes=scopes,
        extra_claims={
            "username": user.username,
            "is_admin": admin_flag,
        },
    )

    return LoginResponse(
        access_token=token,
        expires_in=get_expires_in(expire_at),
        user=_build_user_payload(user),
    )
