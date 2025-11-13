#!/usr/bin/env python
"""
Seed sample public groups and automation activities for testing.

Usage (from project root):
    python scripts/seed_public_groups.py --groups 3 --activities 3 --creator 900001

The script uses service layers so validations remain consistent with production.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from typing import List

from models.db import get_session
from services.public_group_service import create_group
from services.public_group_activity import create_activity


def _generate_groups(prefix: str, count: int) -> List[dict]:
    today = datetime.utcnow().strftime("%Y%m%d")
    groups: List[dict] = []
    for idx in range(1, count + 1):
        name = f"{prefix}{today} #{idx:02d}"
        invite_slug = f"test{today}{idx:02d}"
        groups.append(
            {
                "name": name,
                "invite_link": f"https://t.me/+{invite_slug}",
                "description": (
                    f"自動產生的測試交友群 {idx}，建立於 {today}。"
                    " 用於驗證公開群流程與 MiniApp 資料同步。"
                ),
                "language": "zh",
                "tags": ["test", "dating", f"day{today[-2:]}"],
            }
        )
    return groups


def _generate_activities(prefix: str, count: int) -> List[dict]:
    base_start = datetime.utcnow()
    activities: List[dict] = []
    for idx in range(1, count + 1):
        name = f"{prefix}星星加碼 #{idx:02d}"
        start_at = base_start
        end_at = base_start + timedelta(days=idx)
        front_card = {
            "title": f"{name}",
            "subtitle": f"加入即可領取 {10 + idx * 2} 星，另加早鳥加碼。",
            "cta_label": "立即加入",
            "cta_link": "https://t.me/placeholder",
            "badge": "限時活動",
            "priority": 50 + idx,
        }
        activities.append(
            {
                "name": name,
                "description": f"這是為自動化測試準備的活動 {idx}，請勿在正式環境使用。",
                "reward_points": 10 + idx * 2,
                "bonus_points": 5,
                "daily_cap": 50,
                "total_cap": 200,
                "start_at": start_at,
                "end_at": end_at,
                "is_highlight_enabled": idx % 2 == 1,
                "highlight_slots": 5 if idx % 2 == 1 else 0,
                "front_card": front_card,
            }
        )
    return activities


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed public groups and activities for testing.")
    parser.add_argument("--groups", type=int, default=3, help="Number of public groups to create.")
    parser.add_argument("--activities", type=int, default=3, help="Number of activities to create.")
    parser.add_argument(
        "--creator",
        type=int,
        default=900000,
        help="Telegram ID used as the creator for seeded groups.",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="測試交友 ",
        help="Prefix used for seeded group names.",
    )
    args = parser.parse_args()

    group_defs = _generate_groups(args.prefix, max(args.groups, 0))
    activity_defs = _generate_activities("MiniApp ", max(args.activities, 0))

    created_group_ids: List[int] = []
    created_activity_ids: List[int] = []

    with get_session() as session:
        for definition in group_defs:
            group, risk = create_group(
                session,
                creator_tg_id=args.creator,
                name=definition["name"],
                invite_link=definition["invite_link"],
                description=definition["description"],
                tags=definition["tags"],
                language=definition["language"],
                entry_reward_enabled=True,
                entry_reward_points=10,
                entry_reward_pool_max=500,
            )
            created_group_ids.append(group.id)
            print(
                f"[seed] group id={group.id} name='{group.name}' "
                f"status={group.status.value} risk={risk.score} flags={risk.flags}"
            )

        for definition in activity_defs:
            activity = create_activity(
                session,
                name=definition["name"],
                description=definition["description"],
                reward_points=definition["reward_points"],
                bonus_points=definition["bonus_points"],
                daily_cap=definition["daily_cap"],
                total_cap=definition["total_cap"],
                start_at=definition["start_at"],
                end_at=definition["end_at"],
                is_highlight_enabled=definition["is_highlight_enabled"],
                highlight_slots=definition["highlight_slots"],
                front_card=definition["front_card"],
            )
            created_activity_ids.append(activity.id)
            print(f"[seed] activity id={activity.id} name='{activity.name}'")

    print("\nSeed completed.")
    if created_group_ids:
        print("Groups created:", ", ".join(map(str, created_group_ids)))
    if created_activity_ids:
        print("Activities created:", ", ".join(map(str, created_activity_ids)))


if __name__ == "__main__":
    main()

