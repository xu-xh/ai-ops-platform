"""
AI运维平台 - 安全审计 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.database import Agent, AuditLog, RiskLevel
from app.schemas import AuditLogCreate, AuditLogResponse, AuditStats

router = APIRouter(prefix="/audit", tags=["安全审计"])

# 高危操作列表
HIGH_RISK_ACTIONS = [
    "delete_database",
    "drop_table",
    "truncate_table",
    "send_bulk_email",
    "delete_user",
    "modify_permissions",
    "execute_raw_sql",
    "access_sensitive_data"
]

# 高危操作拦截
@router.post("/log", response_model=AuditLogResponse)
async def create_audit_log(log: AuditLogCreate, db: AsyncSession = Depends(get_db)):
    """创建审计日志（同时进行高危操作检测）"""
    is_blocked = False
    
    # 检测高危操作
    if log.action in HIGH_RISK_ACTIONS or log.risk_level == RiskLevel.HIGH:
        is_blocked = True
        log.blocked = True
    
    db_log = AuditLog(**log.model_dump())
    db.add(db_log)
    await db.flush()
    await db.refresh(db_log)
    
    result = {
        "log": db_log,
        "blocked": is_blocked,
        "message": "操作已被拦截" if is_blocked else "操作已记录"
    }
    
    return result


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    risk_level: RiskLevel = None,
    blocked: bool = None,
    agent_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """获取审计日志列表"""
    query = select(AuditLog)
    
    if risk_level:
        query = query.where(AuditLog.risk_level == risk_level)
    if blocked is not None:
        query = query.where(AuditLog.blocked == blocked)
    if agent_id:
        query = query.where(AuditLog.agent_id == agent_id)
    
    query = query.offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats", response_model=AuditStats)
async def get_audit_stats(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """获取审计统计"""
    start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # 总数
    total_result = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= start_date)
    )
    total_logs = total_result.scalar() or 0
    
    # 拦截数
    blocked_result = await db.execute(
        select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.blocked == True,
                AuditLog.created_at >= start_date
            )
        )
    )
    blocked_count = blocked_result.scalar() or 0
    
    # 高风险数
    high_risk_result = await db.execute(
        select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.risk_level == RiskLevel.HIGH,
                AuditLog.created_at >= start_date
            )
        )
    )
    high_risk_count = high_risk_result.scalar() or 0
    
    # 最近拦截
    recent_result = await db.execute(
        select(AuditLog)
        .where(AuditLog.blocked == True)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
    )
    recent_blocks = recent_result.scalars().all()
    
    return AuditStats(
        total_logs=total_logs,
        blocked_count=blocked_count,
        high_risk_count=high_risk_count,
        recent_blocks=recent_blocks
    )


@router.get("/high-risk-actions")
async def get_high_risk_actions():
    """获取高危操作列表"""
    return {
        "actions": HIGH_RISK_ACTIONS,
        "description": "这些操作将被监管智能体实时监控和拦截"
    }


@router.post("/test-block")
async def test_block_operation(
    action: str,
    resource: str,
    agent_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """测试高危操作拦截"""
    is_blocked = action in HIGH_RISK_ACTIONS
    
    log = AuditLog(
        agent_id=agent_id,
        action=action,
        resource=resource,
        risk_level=RiskLevel.HIGH if is_blocked else RiskLevel.LOW,
        details=f"测试操作: {action}",
        blocked=is_blocked,
        ip_address="127.0.0.1"
    )
    db.add(log)
    await db.flush()
    
    return {
        "action": action,
        "resource": resource,
        "blocked": is_blocked,
        "message": "高危操作已被拦截" if is_blocked else "操作允许执行"
    }
