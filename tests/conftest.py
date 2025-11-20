"""
统一的测试 fixtures 和工具函数
用于所有测试文件的共享配置
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# 设置测试环境变量（在导入其他模块之前）
os.environ.setdefault("FLAG_ENABLE_PUBLIC_GROUPS", "1")
os.environ.setdefault("ADMIN_WEB_USER", "admin")
os.environ.setdefault("RECHARGE_PROVIDER", "mock")  # 避免网络请求

# 清理模块缓存（如果需要）
_MODULES_TO_CLEAR = (
    "models.db",
    "models.user",
    "models.envelope",
    "models.ledger",
    "models.public_group",
)


def _clear_module_cache():
    """清理模块缓存，确保使用新的环境变量"""
    for mod in _MODULES_TO_CLEAR:
        sys.modules.pop(mod, None)


# 延迟导入，避免循环依赖
def _get_models():
    """延迟导入模型"""
    from models.db import get_session, init_db, engine  # noqa: E402
    from models.user import User  # noqa: E402
    from models.envelope import Envelope  # noqa: E402
    from models.ledger import Ledger  # noqa: E402
    from models.public_group import (  # noqa: E402
        PublicGroup,
        PublicGroupStatus,
    )
    return {
        "get_session": get_session,
        "init_db": init_db,
        "engine": engine,
        "User": User,
        "Envelope": Envelope,
        "Ledger": Ledger,
        "PublicGroup": PublicGroup,
        "PublicGroupStatus": PublicGroupStatus,
    }


# ==================== 数据库 Fixtures ====================


@pytest.fixture(scope="function")
def test_db_path(tmp_path: Path, request) -> Path:
    """返回临时测试数据库路径，每个测试文件使用独立的数据库"""
    # 使用测试文件名和测试函数名作为数据库文件名的一部分，确保每个测试使用独立的数据库
    test_file_name = Path(request.node.fspath).stem if hasattr(request.node, 'fspath') else "test"
    test_function_name = request.node.name if hasattr(request.node, 'name') else "test"
    # 使用哈希确保唯一性，避免文件名过长
    import hashlib
    import time
    # 添加时间戳确保唯一性
    unique_id = hashlib.md5(f"{test_file_name}_{test_function_name}_{time.time()}".encode()).hexdigest()[:12]
    db_path = tmp_path / f"{test_file_name}_{unique_id}.sqlite"
    # 确保数据库文件不存在（如果存在则删除）
    if db_path.exists():
        try:
            db_path.unlink(missing_ok=True)
        except (FileNotFoundError, PermissionError):
            pass
    return db_path


@pytest.fixture(scope="function", autouse=True)
def setup_test_db(test_db_path: Path, request) -> Generator[None, None, None]:
    """
    设置测试数据库（自动使用，确保所有测试都有独立的数据库）
    
    注意：如果测试文件已经设置了 DATABASE_URL（如 test_services.py），
    这个 fixture 会尊重已有的设置，但会确保使用独立的数据库文件。
    """
    # 检查是否已经有数据库 URL 设置（某些测试文件可能已经设置）
    test_file_path = Path(request.node.fspath) if hasattr(request.node, 'fspath') else None
    if test_file_path:
        test_file_name = test_file_path.name
        # 这些测试文件使用自己的数据库设置，但我们仍然确保使用独立的数据库文件
        custom_db_files = [
            "test_services.py",
            "test_regression_features.py",
        ]
        if test_file_name in custom_db_files:
            # 对于这些文件，我们仍然使用独立的数据库路径，但使用它们自己的命名规则
            # 这样可以避免冲突，同时保持它们的特殊设置
            original_db_url = os.environ.get("DATABASE_URL")
            # 如果它们已经设置了 DATABASE_URL，我们提取路径并修改为使用独立的文件
            if original_db_url and "sqlite" in original_db_url:
                # 提取原始路径
                import re
                match = re.search(r'sqlite:///(.+)', original_db_url)
                if match:
                    original_path = Path(match.group(1))
                    # 使用测试函数名创建唯一的数据库文件
                    test_function_name = request.node.name if hasattr(request.node, 'name') else "test"
                    unique_db_path = original_path.parent / f"{original_path.stem}_{test_function_name}_{id(request.node)}.sqlite"
                    os.environ["DATABASE_URL"] = f"sqlite:///{unique_db_path.absolute()}"
                    # 清理模块缓存
                    extended_modules = _MODULES_TO_CLEAR + (
                        "models.invite",
                        "models.recharge",
                        "services.invite_service",
                        "services.recharge_service",
                        "services.hongbao_service",
                    )
                    for mod in extended_modules:
                        sys.modules.pop(mod, None)
            yield
            # 清理
            try:
                models = _get_models()
                models["engine"].dispose()
                import time
                time.sleep(0.1)
                if "unique_db_path" in locals() and unique_db_path.exists():
                    unique_db_path.unlink(missing_ok=True)
            except Exception:
                pass
            finally:
                if original_db_url:
                    os.environ["DATABASE_URL"] = original_db_url
            return
    
    # 保存原始数据库 URL（如果存在）
    original_db_url = os.environ.get("DATABASE_URL")
    
    # 设置数据库 URL
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path.absolute()}"
    
    # 清理模块缓存（包括更多模块）
    extended_modules = _MODULES_TO_CLEAR + (
        "models.invite",
        "models.recharge",
        "services.invite_service",
        "services.recharge_service",
        "services.hongbao_service",
    )
    for mod in extended_modules:
        sys.modules.pop(mod, None)
    
    # 初始化数据库
    models = _get_models()
    try:
        models["init_db"]()
    except Exception:
        # 如果初始化失败（可能表已存在），忽略
        pass
    
    yield
    
    # 清理
    try:
        # 关闭所有连接
        models["engine"].dispose()
        # 等待一小段时间，确保文件句柄已关闭
        import time
        time.sleep(0.1)
        # 删除数据库文件
        if test_db_path.exists():
            test_db_path.unlink(missing_ok=True)
    except (FileNotFoundError, PermissionError, Exception) as e:
        # 如果删除失败，记录但不抛出异常
        pass
    finally:
        # 恢复原始数据库 URL
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url
        elif "DATABASE_URL" in os.environ and not any(
            Path(request.node.fspath).name == f for f in ["test_services.py", "test_regression_features.py"]
            if hasattr(request.node, 'fspath')
        ):
            del os.environ["DATABASE_URL"]


@pytest.fixture
def db_session(setup_test_db) -> Generator[Session, None, None]:
    """提供数据库会话"""
    models = _get_models()
    with models["get_session"]() as session:
        yield session


# ==================== FastAPI 应用 Fixtures ====================


@pytest.fixture
def fastapi_app():
    """创建 FastAPI 应用实例"""
    _clear_module_cache()
    from web_admin.main import create_app  # noqa: E402
    
    app = create_app()
    yield app
    
    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def client(fastapi_app) -> TestClient:
    """创建测试客户端"""
    return TestClient(fastapi_app)


# ==================== 认证 Fixtures ====================


@pytest.fixture
def admin_user() -> dict:
    """返回管理员用户信息"""
    return {"username": "admin", "tg_id": 99999}


@pytest.fixture
def mock_admin_auth(admin_user: dict):
    """模拟管理员认证"""
    def override_admin(req: Request):
        return admin_user
    return override_admin


@pytest.fixture
def authenticated_client(client: TestClient, fastapi_app, mock_admin_auth):
    """已认证的测试客户端"""
    from web_admin.deps import require_admin  # noqa: E402
    
    fastapi_app.dependency_overrides[require_admin] = mock_admin_auth
    yield client
    fastapi_app.dependency_overrides.clear()


# ==================== 数据库会话 Fixtures ====================


@pytest.fixture
def mock_db_session(db_session: Session):
    """模拟数据库会话依赖"""
    def override_db():
        yield db_session
    
    return override_db


@pytest.fixture
def client_with_db(client: TestClient, fastapi_app, mock_db_session, mock_admin_auth):
    """带数据库和认证的测试客户端"""
    from web_admin.deps import db_session, db_session_ro, require_admin  # noqa: E402
    
    fastapi_app.dependency_overrides[db_session] = mock_db_session
    fastapi_app.dependency_overrides[db_session_ro] = mock_db_session
    fastapi_app.dependency_overrides[require_admin] = mock_admin_auth
    
    yield client
    
    fastapi_app.dependency_overrides.clear()


# ==================== 测试数据 Fixtures ====================


@pytest.fixture
def sample_user(db_session: Session):
    """创建示例用户"""
    models = _get_models()
    user = models["User"](
        tg_id=10001,
        username="test_user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_group(db_session: Session):
    """创建示例公开群组"""
    from services.public_group_service import create_group  # noqa: E402
    
    group, _ = create_group(
        db_session,
        creator_tg_id=20001,
        name="Test Group",
        invite_link="https://t.me/+test_group",
        description="Test description",
        tags=["test"],
    )
    db_session.commit()
    db_session.refresh(group)
    return group


@pytest.fixture
def sample_envelope(db_session: Session, sample_user):
    """创建示例红包"""
    models = _get_models()
    envelope = models["Envelope"](
        tg_id=30001,
        chat_id=-1000000000,
        message_id=1001,
        amount=100.0,
        count=5,
    )
    db_session.add(envelope)
    db_session.commit()
    db_session.refresh(envelope)
    return envelope


# ==================== 工具函数 ====================


def create_test_user(
    session: Session,
    tg_id: int = 10001,
    username: str = "test_user",
) -> object:
    """创建测试用户"""
    models = _get_models()
    user = models["User"](
        tg_id=tg_id,
        username=username,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_test_group(
    session: Session,
    creator_tg_id: int = 20001,
    name: str = "Test Group",
    invite_link: str = "https://t.me/+test_group",
    **kwargs
) -> tuple:
    """创建测试群组"""
    from services.public_group_service import create_group  # noqa: E402
    
    group, risk = create_group(
        session,
        creator_tg_id=creator_tg_id,
        name=name,
        invite_link=invite_link,
        **kwargs
    )
    session.commit()
    session.refresh(group)
    return group, risk


def create_test_envelope(
    session: Session,
    tg_id: int = 30001,
    chat_id: int = -1000000000,
    message_id: int = 1001,
    amount: float = 100.0,
    count: int = 5,
) -> object:
    """创建测试红包"""
    models = _get_models()
    envelope = models["Envelope"](
        tg_id=tg_id,
        chat_id=chat_id,
        message_id=message_id,
        amount=amount,
        count=count,
    )
    session.add(envelope)
    session.commit()
    session.refresh(envelope)
    return envelope


# ==================== 清理 Fixtures ====================


@pytest.fixture(autouse=True)
def cleanup_after_test(db_session: Session):
    """每个测试后清理数据"""
    yield
    # 测试后清理（如果需要）
    # 注意：使用临时数据库时，数据库文件会在测试后自动删除
    pass

