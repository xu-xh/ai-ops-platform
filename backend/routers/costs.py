"""
成本管理路由
"""
from fastapi import APIRouter
from datetime import datetime
from database import get_db

router = APIRouter()

@router.get("/costs")
async def get_costs(start_date: str = None, end_date: str = None):
    """获取成本数据"""
    with get_db() as conn:
        today = datetime.now().date()
        
        # 获取每个Agent的预算使用情况
        budget_usage = conn.execute("""
            SELECT 
                a.id,
                a.name,
                a.daily_budget,
                COALESCE(SUM(t.cost), 0) as today_cost
            FROM agents a
            LEFT JOIN tasks t ON a.id = t.agent_id AND date(t.created_at) = ?
            GROUP BY a.id
            ORDER BY a.id
        """, (today,)).fetchall()
        
        return [
            {
                "agent_id": row[0],
                "agent_name": row[1],
                "daily_budget": row[2],
                "today_cost": round(row[3], 1),
                "used_percent": min(100, round(row[3] / row[2] * 100, 0)) if row[2] > 0 else 0,
                "status": "warning" if row[3] / row[2] > 0.8 else "normal" if row[2] > 0 else "normal"
            }
            for row in budget_usage
        ]

@router.get("/costs/summary")
async def get_cost_summary():
    """获取成本汇总"""
    with get_db() as conn:
        today = datetime.now().date()
        first_day = today.replace(day=1)
        
        # 今日成本
        today_cost = conn.execute("""
            SELECT COALESCE(SUM(cost), 0) FROM tasks WHERE date(created_at) = ?
        """, (today,)).fetchone()
        
        # 本月成本
        month_cost = conn.execute("""
            SELECT COALESCE(SUM(cost), 0) FROM tasks WHERE date(created_at) >= ?
        """, (first_day,)).fetchone()
        
        return {
            "today_cost": round(today_cost[0], 1),
            "month_cost": round(month_cost[0], 1),
            "budget_used_percent": round(month_cost[0] / 2000 * 100, 1)  # 假设月预算2000
        }
