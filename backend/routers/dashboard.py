"""
仪表盘路由
"""
from fastapi import APIRouter
from datetime import datetime, timedelta
from database import get_db
import random

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard():
    """获取仪表盘数据"""
    with get_db() as conn:
        # 获取Agent统计
        agents = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active
            FROM agents
        """).fetchone()
        
        # 今日任务统计
        today = datetime.now().date()
        tasks_today = conn.execute("""
            SELECT 
                COUNT(*) as total,
                ROUND(AVG(CASE WHEN success = 1 THEN 100.0 ELSE 0.0 END), 1) as success_rate,
                ROUND(AVG(response_time), 0) as avg_response_time,
                SUM(cost) as total_cost
            FROM tasks
            WHERE date(created_at) = ?
        """, (today,)).fetchone()
        
        # 本月成本
        first_day_of_month = today.replace(day=1)
        month_cost = conn.execute("""
            SELECT COALESCE(SUM(cost), 0) as total FROM tasks
            WHERE date(created_at) >= ?
        """, (first_day_of_month,)).fetchone()
        
        # 今日告警
        alerts = conn.execute("""
            SELECT COUNT(*) FROM audit_logs
            WHERE date(created_at) = ? AND blocked = 1
        """, (today,)).fetchone()
        
        # 任务趋势 (7天)
        task_trend = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            row = conn.execute("""
                SELECT 
                    COUNT(*) as tasks,
                    ROUND(AVG(CASE WHEN success = 1 THEN 100.0 ELSE 0.0 END), 0) as rate
                FROM tasks
                WHERE date(created_at) = ?
            """, (date,)).fetchone()
            task_trend.append({
                "date": date.strftime("%m-%d"),
                "tasks": row[0] or 0,
                "success_rate": row[1] or 0
            })
        
        # 成本趋势 (7天)
        cost_trend = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            row = conn.execute("""
                SELECT COALESCE(SUM(cost), 0) FROM tasks
                WHERE date(created_at) = ?
            """, (date,)).fetchone()
            cost_trend.append({
                "date": date.strftime("%m-%d"),
                "cost": round(row[0], 1)
            })
        
        return {
            "total_agents": agents[0] or 0,
            "active_agents": agents[1] or 0,
            "total_tasks_today": tasks_today[0] or 0,
            "success_rate_today": tasks_today[1] or 0,
            "avg_response_time": tasks_today[2] or 0,
            "today_cost": round(tasks_today[3] or 0, 1),
            "month_cost": round(month_cost[0], 1),
            "budget_used_percent": 42.5,
            "total_alerts": alerts[0] or 0,
            "blocked_operations_today": alerts[0] or 0,
            "task_trend": task_trend,
            "cost_trend": cost_trend
        }
