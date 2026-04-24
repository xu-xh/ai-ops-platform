"""
AI运维平台 - Agent API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.database import Agent, Task, CostRecord, AgentStatus, TaskStatus
from app.schemas import (
    AgentCreate, AgentUpdate, AgentResponse, AgentStats,
    TaskCreate, TaskResponse
)

router = APIRouter(prefix="/agents", tags=["Agent管理"])


# === Agent CRUD ===
@router.post("/", response_model=AgentResponse)
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db)):
    """创建 Agent"""
    db_agent = Agent(**agent.model_dump())
    db.add(db_agent)
    await db.flush()
    await db.refresh(db_agent)
    return db_agent


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    status: AgentStatus = None,
    db: AsyncSession = Depends(get_db)
):
    """获取 Agent 列表"""
    query = select(Agent)
    if status:
        query = query.where(Agent.status == status)
    query = query.offset(skip).limit(limit).order_by(Agent.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个 Agent"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新 Agent"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")
    
    update_data = agent_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    agent.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(agent)
    return agent


@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """删除 Agent"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")
    
    await db.delete(agent)
    return {"message": "删除成功"}


@router.get("/{agent_id}/stats", response_model=AgentStats)
async def get_agent_stats(agent_id: int, db: AsyncSession = Depends(get_db)):
    """获取 Agent 统计数据"""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")
    
    # 统计任务
    task_result = await db.execute(
        select(
            func.count(Task.id),
            func.avg(Task.success_rate),
            func.avg(Task.response_time),
            func.sum(Task.token_count)
        ).where(Task.agent_id == agent_id)
    )
    task_stats = task_result.one()
    
    # 统计成本
    today = datetime.utcnow().strftime("%Y-%m-%d")
    cost_result = await db.execute(
        select(
            func.sum(CostRecord.cost_amount)
        ).where(
            and_(
                CostRecord.agent_id == agent_id,
                CostRecord.date == today
            )
        )
    )
    today_cost = cost_result.scalar() or 0.0
    
    total_cost_result = await db.execute(
        select(func.sum(CostRecord.cost_amount)).where(CostRecord.agent_id == agent_id)
    )
    total_cost = total_cost_result.scalar() or 0.0
    
    return AgentStats(
        total_tasks=task_stats[0] or 0,
        success_rate=task_stats[1] or 0.0,
        avg_response_time=task_stats[2] or 0.0,
        total_cost=total_cost,
        today_cost=today_cost,
        token_count=task_stats[3] or 0
    )


# === Task API ===
@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """创建任务记录"""
    db_task = Task(
        **task.model_dump(),
        status=TaskStatus.RUNNING,
        started_at=datetime.utcnow()
    )
    db.add(db_task)
    await db.flush()
    await db.refresh(db_task)
    return db_task


@router.get("/{agent_id}/tasks", response_model=List[TaskResponse])
async def list_agent_tasks(
    agent_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取 Agent 的任务列表"""
    result = await db.execute(
        select(Task)
        .where(Task.agent_id == agent_id)
        .offset(skip)
        .limit(limit)
        .order_by(Task.created_at.desc())
    )
    return result.scalars().all()


@router.put("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    status: TaskStatus,
    success_rate: float = 100.0,
    error_message: str = None,
    db: AsyncSession = Depends(get_db)
):
    """完成任务"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task.status = status
    task.success_rate = success_rate
    task.error_message = error_message
    task.completed_at = datetime.utcnow()
    
    await db.flush()
    return {"message": "任务更新成功"}
