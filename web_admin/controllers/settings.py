# web_admin/controllers/settings.py
from __future__ import annotations

import os
from typing import Any, List, Tuple

from fastapi import APIRouter, Depends, Request, HTTPException, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from core.i18n.i18n import t
from web_admin.deps import require_admin
from web_admin.constants import TWOFA_PASSED_KEY  # ← 改为从 constants 读取，避免循环

router = APIRouter(prefix="/admin/settings", tags=["admin-settings"])
api_router = APIRouter(prefix="/admin/api/v1", tags=["admin-api"])

# 尝试优雅地接入你工程里的 feature flags
# 支持三种形态（按优先级从高到低）：
# 1) feature_flags.flags   -> dict
# 2) feature_flags         -> 模块内的 UPPERCASE bool 变量
# 3) 环境变量 FLAG_*       -> 兜底，只读
try:
    import feature_flags as ff   # 你的项目若叫 config.feature_flags，请自己加个转发模块
except Exception:
    ff = None  # 没有模块就用环境兜底


def _collect_flags() -> List[Tuple[str, Any, str]]:
    """
    汇总功能开关，返回 [(key, value, source)]，source in {"dict","module","env"}
    """
    items: List[Tuple[str, Any, str]] = []
    # 1) dict flags
    if ff is not None and hasattr(ff, "flags") and isinstance(ff.flags, dict):
        for k, v in ff.flags.items():
            items.append((str(k), v, "dict"))
    # 2) 模块内 UPPERCASE
    if ff is not None and not items:
        for k in dir(ff):
            if not k.isupper():
                continue
            v = getattr(ff, k)
            if isinstance(v, (bool, int, str)):
                items.append((k, v, "module"))
    # 3) 环境变量 FLAG_*
    if not items:
        for k, v in os.environ.items():
            if not k.startswith("FLAG_"):
                continue
            vv: Any = v
            if v.lower() in {"1", "true", "yes"}:
                vv = True
            elif v.lower() in {"0", "false", "no"}:
                vv = False
            items.append((k, vv, "env"))
    # 排序稳定
    items.sort(key=lambda x: x[0])
    return items


def _toggle_first_available() -> str:
    """
    尝试切换第一个可切的布尔开关。
    仅支持 module 或 dict。环境变量不在此列（除非你自己写落盘逻辑）。
    返回被切的键名；如果啥也切不了，抛错。
    """
    # dict 优先
    if ff is not None and hasattr(ff, "flags") and isinstance(ff.flags, dict):
        for k, v in ff.flags.items():
            if isinstance(v, bool):
                ff.flags[k] = not v
                return k
    # 模块 UPPERCASE
    if ff is not None:
        for k in dir(ff):
            if not k.isupper():
                continue
            v = getattr(ff, k)
            if isinstance(v, bool):
                setattr(ff, k, not v)
                return k
    raise RuntimeError("No toggleable flag found")


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def settings_page(req: Request, sess=Depends(require_admin)):
    flags = _collect_flags()
    allow_reset = os.getenv("ALLOW_RESET", "0") in {"1", "true", "True", "yes", "YES"}
    twofa_ok = bool(req.session.get(TWOFA_PASSED_KEY))
    return req.app.state.templates.TemplateResponse(
        "settings.html",
        {
            "request": req,
            "title": t("admin.settings.title"),
            "nav_active": "settings",
            "flags": flags,
            "allow_reset": allow_reset,
            "twofa_ok": twofa_ok,
        },
    )


@router.post("/toggle", response_class=RedirectResponse)
def settings_toggle(req: Request, sess=Depends(require_admin)):
    try:
        changed = _toggle_first_available()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # 回到设置页，给个 query 提示
    return RedirectResponse(url=f"/admin/settings?toggled={changed}", status_code=303)


# ---------- REST API: 获取系统设置 ----------
@api_router.get("/settings", response_class=JSONResponse)
def get_settings_api(sess=Depends(require_admin)):
    """
    获取系统设置（JSON API）
    """
    try:
        flags = _collect_flags()
        
        # 从环境变量或配置读取系统参数
        settings = {
            "amount_limits": {
                "max_single": float(os.getenv("MAX_SINGLE_AMOUNT", "1000.0")),
                "min_single": float(os.getenv("MIN_SINGLE_AMOUNT", "0.01")),
                "daily_total": float(os.getenv("DAILY_TOTAL_LIMIT", "10000.0")),
            },
            "risk_control": {
                "enable_rate_limit": os.getenv("ENABLE_RATE_LIMIT", "true").lower() in {"1", "true", "yes"},
                "enable_blacklist": os.getenv("ENABLE_BLACKLIST", "true").lower() in {"1", "true", "yes"},
                "max_per_user_per_day": int(os.getenv("MAX_PER_USER_PER_DAY", "10")),
            },
            "notifications": {
                "notify_on_failure": os.getenv("NOTIFY_ON_FAILURE", "true").lower() in {"1", "true", "yes"},
                "notify_on_critical": os.getenv("NOTIFY_ON_CRITICAL", "true").lower() in {"1", "true", "yes"},
            },
            "feature_flags": {k: v for k, v, _ in flags},
        }
        
        return JSONResponse(settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置失败: {str(e)}")


# ---------- REST API: 更新系统设置 ----------
class SettingsUpdate(BaseModel):
    amount_limits: Optional[Dict[str, float]] = None
    risk_control: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, bool]] = None


@api_router.put("/settings", response_class=JSONResponse)
def update_settings_api(
    settings: SettingsUpdate = Body(...),
    sess=Depends(require_admin),
):
    """
    更新系统设置（JSON API）
    注意：这里只是示例，实际应该持久化到数据库或配置文件
    """
    try:
        # 这里应该将设置保存到数据库或配置文件
        # 目前只是返回成功，实际实现需要根据项目架构调整
        
        # 示例：更新环境变量（仅用于演示，生产环境应该使用数据库）
        if settings.amount_limits:
            if "max_single" in settings.amount_limits:
                os.environ["MAX_SINGLE_AMOUNT"] = str(settings.amount_limits["max_single"])
            if "min_single" in settings.amount_limits:
                os.environ["MIN_SINGLE_AMOUNT"] = str(settings.amount_limits["min_single"])
            if "daily_total" in settings.amount_limits:
                os.environ["DAILY_TOTAL_LIMIT"] = str(settings.amount_limits["daily_total"])
        
        if settings.risk_control:
            if "enable_rate_limit" in settings.risk_control:
                os.environ["ENABLE_RATE_LIMIT"] = str(settings.risk_control["enable_rate_limit"]).lower()
            if "enable_blacklist" in settings.risk_control:
                os.environ["ENABLE_BLACKLIST"] = str(settings.risk_control["enable_blacklist"]).lower()
            if "max_per_user_per_day" in settings.risk_control:
                os.environ["MAX_PER_USER_PER_DAY"] = str(settings.risk_control["max_per_user_per_day"])
        
        if settings.notifications:
            if "notify_on_failure" in settings.notifications:
                os.environ["NOTIFY_ON_FAILURE"] = str(settings.notifications["notify_on_failure"]).lower()
            if "notify_on_critical" in settings.notifications:
                os.environ["NOTIFY_ON_CRITICAL"] = str(settings.notifications["notify_on_critical"]).lower()
        
        return JSONResponse({"success": True, "message": "设置已保存"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存设置失败: {str(e)}")
