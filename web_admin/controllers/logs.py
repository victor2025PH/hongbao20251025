# web_admin/controllers/logs.py
from __future__ import annotations

import math
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from web_admin.deps import db_session_ro as db_session, require_admin

router = APIRouter(prefix="/admin/api/v1", tags=["admin-api"])

# 日志级别枚举
LOG_LEVELS = ["info", "warn", "error"]


@router.get("/logs", response_class=JSONResponse)
def get_logs(
    db=Depends(db_session),
    sess=Depends(require_admin),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    level: Optional[str] = Query(None, description="日志级别: info, warn, error"),
    module: Optional[str] = Query(None, description="模块名称"),
    start: Optional[str] = Query(None, description="开始时间 (ISO 格式)"),
    end: Optional[str] = Query(None, description="结束时间 (ISO 格式)"),
    q: Optional[str] = Query(None, description="搜索关键词"),
):
    """
    获取系统日志列表（JSON 格式，供前端调用）
    注意：这是一个简化实现，实际应该从日志文件或日志数据库读取
    """
    try:
        # TODO: 实际应该从日志文件或日志数据库读取
        # 这里返回空列表，前端会使用 mock 数据
        items: List[Dict[str, Any]] = []
        
        # 模拟分页
        total = 0
        total_pages = 0
        
        return JSONResponse({
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/logs/audit", response_class=JSONResponse)
def get_audit_logs_alt(
    db=Depends(db_session),
    sess=Depends(require_admin),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    level: Optional[str] = Query(None, description="日志级别: info, warn, error"),
    module: Optional[str] = Query(None, description="模块名称"),
    start: Optional[str] = Query(None, description="开始时间 (ISO 格式)"),
    end: Optional[str] = Query(None, description="结束时间 (ISO 格式)"),
    q: Optional[str] = Query(None, description="搜索关键词"),
):
    """
    获取审计日志列表（JSON 格式，供前端调用）
    这是 /admin/api/v1/audit 的别名，保持兼容性
    """
    # 重定向到 audit 接口
    from web_admin.controllers.audit import get_audit_logs
    return get_audit_logs(
        db=db,
        sess=sess,
        page=page,
        per_page=per_page,
        ltype=None,
        types=None,
        token=None,
        user=None,
        operator=None,
        min_amount=None,
        max_amount=None,
        start=start,
        end=end,
        q=q,
    )

