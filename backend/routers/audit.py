"""
安全审计路由
"""
from fastapi import APIRouter
from database import get_db

router = APIRouter()

@router.get("/audit/logs")
async def get_audit_logs(limit: int = 50):
    """获取审计日志"""
    with get_db() as conn:
        logs = conn.execute("""
            SELECT 
                al.id,
                a.name as agent_name,
                al.action,
                al.risk_level,
                al.blocked,
                al.details,
                al.created_at
            FROM audit_logs al
            LEFT JOIN agents a ON al.agent_id = a.id
            ORDER BY al.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [
            {
                "id": row[0],
                "agent": row[1],
                "action": row[2],
                "risk": row[3],
                "blocked": bool(row[4]),
                "details": row[5],
                "time": row[6].split(" ")[1] if row[6] else ""
            }
            for row in logs
        ]

@router.get("/audit/stats")
async def get_audit_stats():
    """获取审计统计"""
    with get_db() as conn:
        today = conn.execute("SELECT date('now')").fetchone()[0]
        
        # 今日拦截
        blocked = conn.execute("""
            SELECT COUNT(*) FROM audit_logs WHERE date(created_at) = ? AND blocked = 1
        """, (today,)).fetchone()
        
        # 高风险操作
        high_risk = conn.execute("""
            SELECT COUNT(*) FROM audit_logs 
            WHERE date(created_at) = ? AND risk_level IN ('critical', 'high')
        """, (today,)).fetchone()
        
        # 总日志数
        total = conn.execute("""
            SELECT COUNT(*) FROM audit_logs WHERE date(created_at) = ?
        """, (today,)).fetchone()
        
        return {
            "blocked_today": blocked[0] or 0,
            "high_risk_today": high_risk[0] or 0,
            "total_logs_today": total[0] or 0
        }
