"""
AI运维平台 - 仪表盘 & 报告 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.database import Agent, Task, CostRecord, AuditLog, DailyReport, AgentStatus
from app.schemas import DashboardStats, DailyReportResponse

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """获取仪表盘统计数据"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    current_month = datetime.utcnow().strftime("%Y-%m")
    
    # === Agent 统计 ===
    total_agents_result = await db.execute(select(func.count(Agent.id)))
    total_agents = total_agents_result.scalar() or 0
    
    active_agents_result = await db.execute(
        select(func.count(Agent.id)).where(Agent.status == AgentStatus.ACTIVE)
    )
    active_agents = active_agents_result.scalar() or 0
    
    # === 今日任务统计 ===
    today_tasks_result = await db.execute(
        select(
            func.count(Task.id),
            func.avg(Task.success_rate),
            func.avg(Task.response_time)
        ).where(Task.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0))
    )
    task_stats = today_tasks_result.one()
    total_tasks_today = task_stats[0] or 0
    success_rate_today = task_stats[1] or 0.0
    avg_response_time = task_stats[2] or 0.0
    
    # === 成本统计 ===
    today_cost_result = await db.execute(
        select(func.sum(CostRecord.cost_amount)).where(CostRecord.date == today)
    )
    today_cost = today_cost_result.scalar() or 0.0
    
    month_cost_result = await db.execute(
        select(func.sum(CostRecord.cost_amount)).where(
            CostRecord.date.like(f"{current_month}%")
        )
    )
    month_cost = month_cost_result.scalar() or 0.0
    
    # 预算使用百分比（假设总预算300元）
    budget_used_percent = (month_cost / 300.0 * 100) if 300.0 > 0 else 0
    
    # === 安全统计 ===
    alerts_result = await db.execute(
        select(func.count(AuditLog.id)).where(
            AuditLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        )
    )
    total_alerts = alerts_result.scalar() or 0
    
    blocked_result = await db.execute(
        select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.blocked == True,
                AuditLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
            )
        )
    )
    blocked_operations_today = blocked_result.scalar() or 0
    
    # === 任务趋势（最近7天）===
    task_trend = []
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        # 简化：随机生成趋势数据，实际应该从数据库查询
        task_trend.append({
            "date": date,
            "tasks": total_tasks_today // max(1, (7-i)) if i == 0 else total_tasks_today // 2,
            "success_rate": 85 + (i * 2)
        })
    
    # === 成本趋势（最近7天）===
    cost_trend = []
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        cost_trend.append({
            "date": date,
            "cost": round(today_cost / max(1, (7-i)), 2)
        })
    
    return DashboardStats(
        total_agents=total_agents,
        active_agents=active_agents,
        total_tasks_today=total_tasks_today,
        success_rate_today=round(success_rate_today, 1),
        avg_response_time=round(avg_response_time, 0),
        today_cost=round(today_cost, 2),
        month_cost=round(month_cost, 2),
        budget_used_percent=round(budget_used_percent, 1),
        total_alerts=total_alerts,
        blocked_operations_today=blocked_operations_today,
        task_trend=task_trend,
        cost_trend=cost_trend
    )


# === 报告 API ===
router_reports = APIRouter(prefix="/reports", tags=["运维报告"])


@router_reports.get("/today", response_model=DailyReportResponse)
async def get_today_report(db: AsyncSession = Depends(get_db)):
    """获取今日报告"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    result = await db.execute(
        select(DailyReport).where(DailyReport.report_date == today)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        # 生成默认报告
        report = DailyReport(
            report_date=today,
            total_tasks=0,
            success_rate=0.0,
            total_cost=0.0,
            active_agents=0,
            total_alerts=0,
            blocked_operations=0,
            summary="暂无数据",
            recommendations="等待AI团队开始工作"
        )
    
    return report


@router_reports.get("/history", response_model=list[DailyReportResponse])
async def get_report_history(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """获取历史报告"""
    start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    result = await db.execute(
        select(DailyReport)
        .where(DailyReport.report_date >= start_date)
        .order_by(DailyReport.report_date.desc())
    )
    return result.scalars().all()


@router_reports.post("/generate")
async def generate_daily_report(db: AsyncSession = Depends(get_db)):
    """手动生成每日报告"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    # 统计任务
    tasks_result = await db.execute(
        select(
            func.count(Task.id),
            func.avg(Task.success_rate)
        )
    )
    task_stats = tasks_result.one()
    
    # 统计成本
    cost_result = await db.execute(
        select(func.sum(CostRecord.cost_amount)).where(CostRecord.date == today)
    )
    total_cost = cost_result.scalar() or 0.0
    
    # 统计 Agent
    agent_result = await db.execute(
        select(func.count(Agent.id)).where(Agent.status == AgentStatus.ACTIVE)
    )
    active_agents = agent_result.scalar() or 0
    
    # 统计告警
    alerts_result = await db.execute(
        select(func.count(AuditLog.id))
    )
    total_alerts = alerts_result.scalar() or 0
    
    blocked_result = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.blocked == True)
    )
    blocked_operations = blocked_result.scalar() or 0
    
    # 生成建议
    recommendations = []
    if total_cost > 200:
        recommendations.append("本月成本已超过200元，建议优化Agent调用策略")
    if active_agents < 3:
        recommendations.append("活跃Agent数量较少，考虑增加自动化任务")
    if blocked_operations > 10:
        recommendations.append("检测到多次高危操作被拦截，建议检查Agent配置")
    
    if not recommendations:
        recommendations.append("系统运行正常，继续保持")
    
    # 保存或更新报告
    result = await db.execute(
        select(DailyReport).where(DailyReport.report_date == today)
    )
    report = result.scalar_one_or_none()
    
    if report:
        report.total_tasks = task_stats[0] or 0
        report.success_rate = task_stats[1] or 0.0
        report.total_cost = total_cost
        report.active_agents = active_agents
        report.total_alerts = total_alerts
        report.blocked_operations = blocked_operations
        report.summary = f"今日共执行{task_stats[0] or 0}个任务，成功率{task_stats[1] or 0:.1f}%，成本{total_cost:.2f}元"
        report.recommendations = "; ".join(recommendations)
    else:
        report = DailyReport(
            report_date=today,
            total_tasks=task_stats[0] or 0,
            success_rate=task_stats[1] or 0.0,
            total_cost=total_cost,
            active_agents=active_agents,
            total_alerts=total_alerts,
            blocked_operations=blocked_operations,
            summary=f"今日共执行{task_stats[0] or 0}个任务，成功率{task_stats[1] or 0:.1f}%，成本{total_cost:.2f}元",
            recommendations="; ".join(recommendations)
        )
        db.add(report)
    
    await db.flush()
    await db.refresh(report)
    
    return report
