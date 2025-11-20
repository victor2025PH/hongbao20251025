"""
增强的 public_group_service.py 测试
覆盖更多服务层函数，提升测试覆盖率
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, UTC
from pathlib import Path

import pytest
from sqlalchemy import text

from models.user import User, get_or_create_user  # noqa: E402

# 运行测试前强制使用独立的 SQLite 数据库
os.environ["DATABASE_URL"] = "sqlite:///./test_public_group_service_enhanced.sqlite"
_prev_public_group_flag = os.environ.get("FLAG_ENABLE_PUBLIC_GROUPS")
os.environ["FLAG_ENABLE_PUBLIC_GROUPS"] = "1"

from models.db import engine, get_session, init_db  # noqa: E402
from models.public_group import (  # noqa: E402
    PublicGroup,
    PublicGroupBookmark,
    PublicGroupStatus,
)
from services.public_group_service import (  # noqa: E402
    PublicGroupError,
    add_bookmark,
    get_user_bookmark_ids,
    list_bookmarked_groups,
    remove_bookmark,
    serialize_group,
    unpin_group,
    update_group,
    create_group,
    pin_group,
    join_group,
)


def setup_module() -> None:
    Path("test_public_group_service_enhanced.sqlite").unlink(missing_ok=True)
    init_db()


def teardown_module() -> None:
    if _prev_public_group_flag is None:
        os.environ.pop("FLAG_ENABLE_PUBLIC_GROUPS", None)
    else:
        os.environ["FLAG_ENABLE_PUBLIC_GROUPS"] = _prev_public_group_flag


@pytest.fixture(autouse=True)
def _clean_group_tables():
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM public_group_activity_logs"))
        conn.execute(text("DELETE FROM public_group_activities"))
        conn.execute(text("DELETE FROM public_group_reward_claims"))
        conn.execute(text("DELETE FROM public_group_members"))
        conn.execute(text("DELETE FROM public_group_bookmarks"))
        conn.execute(text("DELETE FROM public_groups"))
        conn.execute(text("DELETE FROM users"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM public_group_activity_logs"))
        conn.execute(text("DELETE FROM public_group_activities"))
        conn.execute(text("DELETE FROM public_group_reward_claims"))
        conn.execute(text("DELETE FROM public_group_members"))
        conn.execute(text("DELETE FROM public_group_bookmarks"))
        conn.execute(text("DELETE FROM public_groups"))
        conn.execute(text("DELETE FROM users"))


def test_unpin_group() -> None:
    """测试取消置顶群组"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=1001,
            name="Pinned Group",
            invite_link="https://t.me/+pinned_group",
        )
        # 先置顶
        pin_group(session, group_id=group.id, operator_tg_id=9999)
        session.commit()
        
        # 验证已置顶
        refreshed = session.get(PublicGroup, group.id)
        assert refreshed.is_pinned is True
        
        # 取消置顶
        unpinned = unpin_group(session, group_id=group.id)
        session.commit()
        
        assert unpinned.is_pinned is False
        assert unpinned.pinned_until is None
        
        # 验证数据库中的状态
        refreshed = session.get(PublicGroup, group.id)
        assert refreshed.is_pinned is False


def test_unpin_group_not_found() -> None:
    """测试取消置顶不存在的群组"""
    with get_session() as session:
        with pytest.raises(PublicGroupError, match="group_not_found"):
            unpin_group(session, group_id=99999)


def test_update_group_basic() -> None:
    """测试更新群组基本信息"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=2001,
            name="Original Name",
            invite_link="https://t.me/+original",
            description="Original description",
            tags=["tag1", "tag2"],
        )
        session.commit()
        
        # 更新描述和标签
        updated = update_group(
            session,
            group_id=group.id,
            updater_tg_id=2001,
            description="Updated description",
            tags=["tag3", "tag4"],
        )
        session.commit()
        
        assert updated.description == "Updated description"
        assert updated.tags == ["tag3", "tag4"]
        
        # 验证数据库中的状态
        refreshed = session.get(PublicGroup, group.id)
        assert refreshed.description == "Updated description"
        assert refreshed.tags == ["tag3", "tag4"]


def test_update_group_not_owner() -> None:
    """测试非所有者更新群组（应该失败）"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=3001,
            name="Owner Group",
            invite_link="https://t.me/+owner_group",
        )
        session.commit()
        
        # 非所有者尝试更新
        with pytest.raises(PublicGroupError, match="forbidden"):
            update_group(
                session,
                group_id=group.id,
                updater_tg_id=3002,  # 不同的用户
                description="Hacked description",
            )


def test_update_group_as_admin() -> None:
    """测试管理员更新群组（应该成功）"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=4001,
            name="Admin Update Group",
            invite_link="https://t.me/+admin_update",
        )
        session.commit()
        
        # 管理员更新
        updated = update_group(
            session,
            group_id=group.id,
            updater_tg_id=9999,  # 管理员
            description="Admin updated description",
            is_admin=True,
        )
        session.commit()
        
        assert updated.description == "Admin updated description"


def test_update_group_entry_reward() -> None:
    """测试更新群组入口奖励设置"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=5001,
            name="Reward Group",
            invite_link="https://t.me/+reward_group",
            entry_reward_points=5,
            entry_reward_pool_max=100,
        )
        session.commit()
        
        # 更新奖励设置
        updated = update_group(
            session,
            group_id=group.id,
            updater_tg_id=5001,
            entry_reward_points=10,
            entry_reward_pool_max=200,
            entry_reward_pool=150,
        )
        session.commit()
        
        assert updated.entry_reward_points == 10
        assert updated.entry_reward_pool_max == 200
        assert updated.entry_reward_pool == 150


def test_update_group_invalid_reward_points() -> None:
    """测试更新无效的奖励点数"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=6001,
            name="Invalid Reward Group",
            invite_link="https://t.me/+invalid_reward",
        )
        session.commit()
        
        # 尝试设置无效的奖励点数
        with pytest.raises(PublicGroupError, match="entry_reward_points_invalid"):
            update_group(
                session,
                group_id=group.id,
                updater_tg_id=6001,
                entry_reward_points=100,  # 超过最大值
            )


def test_add_bookmark() -> None:
    """测试添加书签"""
    with get_session() as session:
        # 创建用户和群组
        user = get_or_create_user(session, tg_id=7001)
        group, _ = create_group(
            session,
            creator_tg_id=7002,
            name="Bookmark Group",
            invite_link="https://t.me/+bookmark_group",
        )
        session.commit()
        
        # 添加书签
        bookmark, created = add_bookmark(session, group_id=group.id, user_tg_id=7001)
        session.commit()
        
        assert bookmark.group_id == group.id
        assert bookmark.user_tg_id == 7001
        assert created is True
        
        # 验证数据库中的书签
        refreshed = session.get(PublicGroupBookmark, bookmark.id)
        assert refreshed is not None


def test_add_bookmark_duplicate() -> None:
    """测试重复添加书签（应该返回现有书签）"""
    with get_session() as session:
        user = get_or_create_user(session, tg_id=8001)
        group, _ = create_group(
            session,
            creator_tg_id=8002,
            name="Duplicate Bookmark Group",
            invite_link="https://t.me/+duplicate_bookmark",
        )
        session.commit()
        
        # 第一次添加
        bookmark1, created1 = add_bookmark(session, group_id=group.id, user_tg_id=8001)
        session.commit()
        
        # 第二次添加（应该返回同一个书签）
        bookmark2, created2 = add_bookmark(session, group_id=group.id, user_tg_id=8001)
        session.commit()
        
        assert bookmark1.id == bookmark2.id
        assert created1 is True
        assert created2 is False  # 第二次不应该创建新书签


def test_remove_bookmark() -> None:
    """测试删除书签"""
    with get_session() as session:
        user = get_or_create_user(session, tg_id=9001)
        group, _ = create_group(
            session,
            creator_tg_id=9002,
            name="Remove Bookmark Group",
            invite_link="https://t.me/+remove_bookmark",
        )
        session.commit()
        
        # 添加书签
        bookmark, _ = add_bookmark(session, group_id=group.id, user_tg_id=9001)
        session.commit()
        bookmark_id = bookmark.id
        
        # 删除书签
        removed = remove_bookmark(session, group_id=group.id, user_tg_id=9001)
        session.commit()
        
        assert removed is True
        
        # 验证书签已删除
        refreshed = session.get(PublicGroupBookmark, bookmark_id)
        assert refreshed is None


def test_remove_bookmark_not_exists() -> None:
    """测试删除不存在的书签"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=10001,
            name="No Bookmark Group",
            invite_link="https://t.me/+no_bookmark",
        )
        session.commit()
        
        # 尝试删除不存在的书签
        removed = remove_bookmark(session, group_id=group.id, user_tg_id=99999)
        assert removed is False


def test_list_bookmarked_groups() -> None:
    """测试列出用户的书签群组"""
    with get_session() as session:
        user = get_or_create_user(session, tg_id=11001)
        
        # 创建多个群组
        groups = []
        for i in range(3):
            group, _ = create_group(
                session,
                creator_tg_id=11002 + i,
                name=f"Bookmarked Group {i}",
                invite_link=f"https://t.me/+bookmarked_{i}",
            )
            groups.append(group)
            # 添加书签
            add_bookmark(session, group_id=group.id, user_tg_id=11001)
        session.commit()
        
        # 列出书签群组
        bookmarked = list_bookmarked_groups(session, user_tg_id=11001)
        
        assert len(bookmarked) == 3
        group_ids = [g.id for g in bookmarked]
        assert all(g.id in group_ids for g in groups)


def test_get_user_bookmark_ids() -> None:
    """测试获取用户的书签ID列表"""
    with get_session() as session:
        user = get_or_create_user(session, tg_id=12001)
        
        # 创建群组并添加书签
        group1, _ = create_group(
            session,
            creator_tg_id=12002,
            name="Bookmark ID Group 1",
            invite_link="https://t.me/+bookmark_id_1",
        )
        group2, _ = create_group(
            session,
            creator_tg_id=12003,
            name="Bookmark ID Group 2",
            invite_link="https://t.me/+bookmark_id_2",
        )
        add_bookmark(session, group_id=group1.id, user_tg_id=12001)
        add_bookmark(session, group_id=group2.id, user_tg_id=12001)
        session.commit()
        
        # 获取书签ID列表
        bookmark_ids = get_user_bookmark_ids(session, user_tg_id=12001)
        
        assert len(bookmark_ids) == 2
        assert group1.id in bookmark_ids
        assert group2.id in bookmark_ids


def test_serialize_group() -> None:
    """测试序列化群组"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=13001,
            name="Serialize Group",
            invite_link="https://t.me/+serialize_group",
            description="Test description",
            tags=["tag1", "tag2"],
        )
        session.commit()
        
        # 序列化群组
        serialized = serialize_group(group, is_bookmarked=False)
        
        assert serialized["id"] == group.id
        assert serialized["name"] == "Serialize Group"
        assert serialized["description"] == "Test description"
        assert serialized["tags"] == ["tag1", "tag2"]
        assert serialized["is_bookmarked"] is False
        
        # 序列化带书签的群组
        serialized_bookmarked = serialize_group(group, is_bookmarked=True)
        assert serialized_bookmarked["is_bookmarked"] is True


def test_update_group_language() -> None:
    """测试更新群组语言"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=14001,
            name="Language Group",
            invite_link="https://t.me/+language_group",
            language="zh",
        )
        session.commit()
        
        # 更新语言
        updated = update_group(
            session,
            group_id=group.id,
            updater_tg_id=14001,
            language="en",
        )
        session.commit()
        
        assert updated.language == "en"


def test_update_group_cover_template() -> None:
    """测试更新群组封面模板"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=15001,
            name="Cover Template Group",
            invite_link="https://t.me/+cover_template",
        )
        session.commit()
        
        # 更新封面模板
        updated = update_group(
            session,
            group_id=group.id,
            updater_tg_id=15001,
            cover_template="template_v2",
        )
        session.commit()
        
        assert updated.cover_template == "template_v2"


def test_update_group_description_too_long() -> None:
    """测试更新过长的描述"""
    with get_session() as session:
        group, _ = create_group(
            session,
            creator_tg_id=16001,
            name="Long Desc Group",
            invite_link="https://t.me/+long_desc",
        )
        session.commit()
        
        # 尝试设置过长的描述
        long_desc = "x" * 500  # 超过 MAX_DESC_LENGTH (400)
        with pytest.raises(PublicGroupError, match="group_description_too_long"):
            update_group(
                session,
                group_id=group.id,
                updater_tg_id=16001,
                description=long_desc,
            )

