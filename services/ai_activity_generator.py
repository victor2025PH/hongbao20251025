from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

try:  # pragma: no cover
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore[assignment]

from config.settings import settings
from models.public_group import PublicGroupActivityAIHistory

log = logging.getLogger("public_group.activity.ai")

_SYSTEM_PROMPT = (
    "You are an operations specialist who designs Telegram community campaigns for MiniApp/Bot surfaces. "
    "Generate a JSON object for one automation campaign. Follow exactly this schema:\n"
    "{\n"
    '  "name": str,\n'
    '  "description": str,\n'
    '  "reward_points": int,\n'
    '  "bonus_points": int,\n'
    '  "daily_cap": int | null,\n'
    '  "total_cap": int | null,\n'
    '  "duration_hours": int,\n'
    '  "highlight_enabled": bool,\n'
    '  "highlight_slots": int,\n'
    '  "tags": [str, ...],\n'
    '  "language": str,\n'
    '  "front_card": {\n'
    '      "title": str,\n'
    '      "subtitle": str,\n'
    '      "cta_label": str,\n'
    '      "cta_link": str,\n'
    '      "badge": str,\n'
    '      "priority": int,\n'
    '      "highlight_enabled": bool,\n'
    '      "highlight_slots": int\n'
    "  }\n"
    "}\n"
    "Rewards must be within 0-100. If no timeframe is specified, choose a duration between 24 and 120 hours. "
    "Use concise wording suitable for multilingual MiniApp cards. Return ONLY the JSON object with no explanations."
)


def _default_client() -> OpenAI:
    if OpenAI is None:
        raise RuntimeError("openai_sdk_missing")
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("openai_api_key_missing")
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _call_openai(prompt: str) -> str:
    client = _default_client()
    response = client.responses.create(
        model=settings.OPENAI_MODEL or "gpt-4o-mini",
        input=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        max_output_tokens=600,
    )
    try:
        return response.output[0].content[0].text  # type: ignore[index]
    except Exception as exc:  # pragma: no cover - defensive
        log.exception("failed to parse OpenAI response: %s", exc)
        raise RuntimeError("openai_response_invalid") from exc


def _sanitize_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    def _as_int(value: Any, default: int = 0, allow_none: bool = False) -> Optional[int]:
        if value is None and allow_none:
            return None
        try:
            return int(value)
        except Exception:
            return default

    front_card = raw.get("front_card") or {}
    duration_hours = _as_int(raw.get("duration_hours"), default=48)
    now = datetime.utcnow()
    end_at = now + timedelta(hours=max(duration_hours or 24, 12))

    highlight_enabled = bool(front_card.get("highlight_enabled", raw.get("highlight_enabled", True)))
    highlight_slots = max(_as_int(front_card.get("highlight_slots"), default=3), 0)

    tags = raw.get("tags") or []
    if not isinstance(tags, list):
        tags = []
    clean_tags: List[str] = []
    for tag in tags:
        text = str(tag or "").strip()
        if text and text not in clean_tags:
            clean_tags.append(text[:24])
        if len(clean_tags) >= 5:
            break

    language = str(raw.get("language") or settings.DEFAULT_LANG).split("-")[0][:8]

    return {
        "name": str(raw.get("name") or "Untitled Campaign")[:80],
        "description": str(raw.get("description") or "").strip()[:600],
        "reward_points": max(_as_int(raw.get("reward_points"), default=5), 0),
        "bonus_points": max(_as_int(raw.get("bonus_points"), default=0), 0),
        "daily_cap": _as_int(raw.get("daily_cap"), default=None, allow_none=True),
        "total_cap": _as_int(raw.get("total_cap"), default=None, allow_none=True),
        "start_at": now.isoformat(),
        "end_at": end_at.isoformat(),
        "highlight_enabled": highlight_enabled,
        "highlight_slots": highlight_slots,
        "tags": clean_tags,
        "language": language,
        "front_card": {
            "title": str(front_card.get("title") or raw.get("name") or "Campaign"),
            "subtitle": str(front_card.get("subtitle") or raw.get("description") or "")[:160],
            "cta_label": str(front_card.get("cta_label") or "參加活動"),
            "cta_link": str(front_card.get("cta_link") or "https://t.me/placeholder"),
            "badge": str(front_card.get("badge") or "AI 推薦"),
            "priority": max(_as_int(front_card.get("priority"), default=80), 0),
            "highlight_enabled": highlight_enabled,
            "highlight_slots": highlight_slots,
        },
    }


def generate_activity_draft(
    session: Session,
    *,
    operator_tg_id: Optional[int],
    brief: str,
) -> Dict[str, Any]:
    brief_clean = (brief or "").strip()
    if not brief_clean:
        raise ValueError("brief_required")

    history = PublicGroupActivityAIHistory(
        operator_tg_id=operator_tg_id,
        prompt=brief_clean,
    )
    session.add(history)
    session.flush()

    try:
        raw_text = _call_openai(brief_clean)
        history.response = raw_text
        data = json.loads(raw_text)
        if not isinstance(data, dict):
            raise ValueError("openai_payload_invalid")
        payload = _sanitize_payload(data)
        history.payload = payload
        history.error = None
        session.add(history)
        log.info(
            "public_group.activity.ai_draft history_id=%s operator=%s",
            history.id,
            operator_tg_id,
        )
        return {
            "history_id": history.id,
            "draft": payload,
        }
    except RuntimeError as exc:
        history.error = exc.args[0] if exc.args else "openai_error"
        session.add(history)
        session.flush()
        raise
    except Exception as exc:
        history.error = getattr(exc, "args", ["parse_error"])[0]
        session.add(history)
        session.flush()
        log.exception("ai_draft failed: %s", exc)
        raise ValueError("ai_generate_failed") from exc


def list_activity_ai_history(session: Session, limit: int = 10) -> List[Dict[str, Any]]:
    stmt = (
        select(PublicGroupActivityAIHistory)
        .order_by(PublicGroupActivityAIHistory.created_at.desc())
        .limit(max(1, limit))
    )
    rows = session.execute(stmt).scalars().all()
    items: List[Dict[str, Any]] = []
    for row in rows:
        payload = row.payload or {}
        items.append(
            {
                "id": row.id,
                "operator_tg_id": row.operator_tg_id,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "error": row.error,
                "applied_activity_id": row.applied_activity_id,
                "applied_at": row.applied_at.isoformat() if row.applied_at else None,
                "name": payload.get("name"),
                "reward_points": payload.get("reward_points"),
                "brief_excerpt": (row.prompt or "")[:120],
            }
        )
    return items


def load_history_draft(
    session: Session,
    *,
    history_id: int,
) -> Dict[str, Any]:
    history = session.get(PublicGroupActivityAIHistory, int(history_id))
    if not history:
        raise ValueError("history_not_found")
    payload = history.payload or {}
    if not payload:
        raise ValueError("history_payload_missing")
    history.applied_at = datetime.utcnow()
    session.add(history)
    return {
        "history_id": history.id,
        "draft": payload,
    }

