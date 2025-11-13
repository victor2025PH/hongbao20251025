from __future__ import annotations

import json

import pytest

from models.db import get_session, init_db
from models.public_group import PublicGroupActivityAIHistory
from services import ai_activity_generator as ai_gen


def setup_module() -> None:
    init_db()


def test_generate_activity_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "name": "AI 全民拉新",
        "description": "新用戶加入社群即可獲得 12 星，邀請好友再加碼。",
        "reward_points": 12,
        "bonus_points": 6,
        "daily_cap": 80,
        "total_cap": 400,
        "duration_hours": 72,
        "front_card": {
            "title": "AI 活動卡片",
            "subtitle": "限時 3 天，立即領取星星獎勵！",
            "cta_label": "立即參加",
            "cta_link": "https://t.me/placeholder-ai",
            "badge": "限時活動",
            "priority": 42,
            "highlight_slots": 4,
        },
    }

    monkeypatch.setattr(
        ai_gen,
        "_call_openai",
        lambda brief: json.dumps(payload),
    )

    with get_session() as session:
        result = ai_gen.generate_activity_draft(
            session,
            operator_tg_id=987654321,
            brief="拉新活動，3 天內發放 12 星獎勵。",
        )
        session.commit()

    draft = result["draft"]
    assert draft["name"] == "AI 全民拉新"
    assert draft["reward_points"] == 12
    assert draft["bonus_points"] == 6
    assert draft["highlight_enabled"] is True
    assert draft["highlight_slots"] == 4
    assert "start_at" in draft and "end_at" in draft
    assert draft["front_card"]["title"] == "AI 活動卡片"

    with get_session() as session:
        history = session.query(PublicGroupActivityAIHistory).order_by(
            PublicGroupActivityAIHistory.id.desc()
        ).first()
        assert history is not None
        assert history.operator_tg_id == 987654321
        assert history.payload.get("name") == "AI 全民拉新"


def test_generate_activity_draft_requires_brief(monkeypatch: pytest.MonkeyPatch) -> None:
    with get_session() as session:
        with pytest.raises(ValueError):
            ai_gen.generate_activity_draft(
                session,
                operator_tg_id=1,
                brief=" ",
            )

