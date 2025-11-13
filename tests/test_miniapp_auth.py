import hashlib
import hmac
import time

import jwt
from fastapi.testclient import TestClient

from config.settings import settings
from miniapp.main import app

client = TestClient(app)


def _make_telegram_code(tg_id: int, username: str) -> str:
    ts = str(int(time.time()))
    secret_source = getattr(settings, "TELEGRAM_BOT_TOKEN", None) or settings.BOT_TOKEN
    secret = secret_source.encode("utf-8")
    message = f"{tg_id}.{username}.{ts}".encode("utf-8")
    signature = hmac.new(secret, message, hashlib.sha256).hexdigest()
    return f"{tg_id}.{username}.{ts}.{signature}"


def test_login_with_telegram_code() -> None:
    code = _make_telegram_code(123456789, "tester")
    resp = client.post(
        "/api/auth/login",
        json={"provider": "telegram", "telegram_code": code},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"].lower() == "bearer"
    token = data["access_token"]
    payload = jwt.decode(
        token,
        settings.MINIAPP_JWT_SECRET,
        algorithms=["HS256"],
        issuer=settings.MINIAPP_JWT_ISSUER,
        options={"verify_aud": False},
    )
    assert int(payload["tg_id"]) == 123456789
    assert "miniapp" in payload.get("scope", "")


def test_login_with_password(monkeypatch) -> None:
    username = "tester"
    password = "secret123"
    sha = hashlib.sha256(password.encode("utf-8")).hexdigest()
    monkeypatch.setenv("MINIAPP_PASSWORD_USERS", f"{username}:sha256:{sha}")

    resp = client.post(
        "/api/auth/login",
        json={
            "provider": "password",
            "username": username,
            "password": password,
            "tg_id": 987654321,
        },
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    bookmarks = client.get(
        "/v1/groups/public/bookmarks",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert bookmarks.status_code == 200
    assert isinstance(bookmarks.json(), list)
