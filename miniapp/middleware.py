# -*- coding: utf-8 -*-
"""FastAPI 中間件：解析 Authorization: Bearer token。"""

from __future__ import annotations

from typing import Callable

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from jwt import ExpiredSignatureError, InvalidTokenError

from .security import decode_access_token, is_token_blacklisted


class JWTAuthMiddleware:
    """從 Authorization header 中解析 Bearer token，驗證後寫入 scope['user']。"""

    def __init__(self, app: Callable):
        self.app = app

    async def __call__(self, scope, receive, send):  # type: ignore[override]
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        raw_authorization = headers.get(b"authorization")
        if raw_authorization:
            scheme, token = get_authorization_scheme_param(raw_authorization.decode())
            if scheme.lower() == "bearer" and token:
                try:
                    payload = decode_access_token(token)
                except ExpiredSignatureError:
                    response = JSONResponse({"detail": "token_expired"}, status_code=401)
                    await response(scope, receive, send)
                    return
                except InvalidTokenError:
                    response = JSONResponse({"detail": "invalid_token"}, status_code=401)
                    await response(scope, receive, send)
                    return
                if is_token_blacklisted(payload.get("jti")):
                    response = JSONResponse({"detail": "token_revoked"}, status_code=401)
                    await response(scope, receive, send)
                    return
                scope["user"] = payload
            elif scheme and scheme.lower() == "bearer":
                response = JSONResponse({"detail": "invalid_token_header"}, status_code=401)
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
