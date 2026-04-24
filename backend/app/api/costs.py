"""
AI运维平台 - 成本管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.database import Agent, CostRecord
from app.schemas import CostRecordCreate, CostRecordResponse, CostSummary

router = APIRouter(prefix="/costs", tags=["成本管理"])


# === 成本记录 ===
@router.post("/", response_model=CostRecordResponse)
async def create_cost_record(cost: CostRecordCreate, db: AsyncSession = Depends(get_db)):
    """创建成本记录"""
    # 检查 Agent 是否存在
    result = await db.execute(select(Agent).where(Agent.id == cost.agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")
    
    db_cost = CostRecord(**cost.model_dump())
    db.add(db_cost)
    
    # 检查是否超过预算
    today = datetime.utcnow().strftime("%Y-%m-%d")
    today_cost_result = await db.execute(
        select(func.sum(CostRecord.cost_amount)).where(
            and_(
                CostRecord.agent_id == cost.agent_id,
                CostRecord.date == today
            )
        )
    )
    today_cost = today_cost_result.scalar() or 0.0
    
    if today_cost + cost.cost_amount > agent.daily_budget:
        # 超过预算，触发告警
        return {
            "warning": "超过每日预算",
            "current_cost": today_cost + cost.cost_amount,
            "budget": agent.daily_budget
        }
    
    await db.flush()
    await db.refresh(db_cost)
    return db_cost


@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(db: AsyncSession = Depends(get_db)):
    """获取成本汇总"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    current_month = datetime.utcnow().strftime("%Y-%m")
    
    # 今日成本
    today_result = await db.execute(
        select(func.sum(CostRecord.cost_amount)).where(CostRecord.date == today)
    )
    today_cost = today_result.scalar() or 0.0
    
    # 本月成本
    month_result = await db.execute(
        select(func.sum(CostRecord.cost_amount)).where(
            CostRecord.date.like(f"{current_month}%")
        )
    )
    month_cost = month_result.scalar() or 0.0
    
    # 总成本
    total_result = await db.execute(
        select(func.sum(CostRecord.cost_amount))
    )
    total_cost = total_result.scalar() or 0.0
    
    # 按 Agent 汇总
    agent_costs_result = await db.execute(
        select(
            Agent.id,
            Agent.name,
            func.sum(CostRecord.cost_amount).label("total")
        )
        .join(CostRecord, Agent.id == CostRecord.agent_id)
        .group_by(Agent.id, Agent.name)
    )
    agent_costs = [
        {"agent_id": row[0], "agent_name": row[1], "total_cost": row[2] or 0.0}
        for row in agent_costs_result.all()
    ]
    
    return CostSummary(
        total_cost=total_cost,
        today_cost=today_cost,
        month_cost=month_cost,
        agent_costs=agent_costs
    )


@router.get("/agent/{agent_id}", response_model=List[CostRecordResponse])
async def get_agent_costs(
    agent_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """获取 Agent 的成本记录"""
    start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    result = await db.execute(
        select(CostRecord)
        .where(
            and_(
                CostRecord.agent_id == agent_id,
                CostRecord.date >= start_date
            )
        )
        .order_by(CostRecord.date.desc())
    )
    return result.scalars().all()


@router.get("/trend")
async def get_cost_trend(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """获取成本趋势"""
    trends = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        result = await db.execute(
            select(func.sum(CostRecord.cost_amount)).where(CostRecord.date == date)
        )
        cost = result.scalar() or 0.0
        trends.append({"date": date, "cost": round(cost, 2)})
    
    return list(reversed(trends))


@router.get("/budget-status")
async def get_budget_status(db: AsyncSession = Depends(get_db)):
    """获取预算状态"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    # 获取所有 Agent 的预算使用情况
    result = await db.execute(select(Agent))
    agents = result.scalars().all()
    
    budget_status = []
    for agent in agents:
        # 今日成本
        cost_result = await db.execute(
            select(func.sum(CostRecord.cost_amount)).where(
                and_(
                    CostRecord.agent_id == agent.id,
                    CostRecord.date == today
                )
            )
        )
        today_cost = cost_result.scalar() or 0.0
        
        used_percent = (today_cost / agent.daily_budget * 100) if agent.daily_budget > 0 else 0
        
        budget_status.append({
            "agent_id": agent.id,
            "agent_name": agent.name,
            "daily_budget": agent.daily_budget,
            "today_cost": round(today_cost, 2),
            "used_percent": round(used_percent, 1),
            "is_exceeded": today_cost > agent.daily_budget,
            "status": "danger" if used_percent >= 100 else "warning" if used_percent >= 80 else "normal"
        })
    
    return budget_status
