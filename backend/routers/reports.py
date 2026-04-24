"""
运维报告路由
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from database import get_db
import random

router = APIRouter()

@router.get("/reports")
async def get_reports(limit: int = 30):
    """获取运维报告列表"""
    with get_db() as conn:
        reports = conn.execute("""
            SELECT 
                date, total_tasks, success_rate, total_cost,
                alert_count, blocked_count, summary
            FROM reports
            ORDER BY date DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [
            {
                "date": row[0],
                "tasks": row[1],
                "success_rate": row[2],
                "cost": row[3],
                "alerts": row[4],
                "blocked": row[5],
                "summary": row[6]
            }
            for row in reports
        ]

@router.post("/reports/generate")
async def generate_report(date: str = None):
    """生成指定日期的报告"""
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    
    with get_db() as conn:
        # 检查报告是否已存在
        existing = conn.execute(
            "SELECT id FROM reports WHERE date = ?",
            (target_date,)
        ).fetchone()
        
        if existing:
            raise HTTPException(status_code=400, detail="Report already exists for this date")
        
        # 统计数据
        stats = conn.execute("""
            SELECT 
                COUNT(*) as tasks,
                ROUND(AVG(CASE WHEN success = 1 THEN 100.0 ELSE 0.0 END), 1) as rate,
                SUM(cost) as cost
            FROM tasks
            WHERE date(created_at) = ?
        """, (target_date,)).fetchone()
        
        alert_count = conn.execute("""
            SELECT COUNT(*) FROM audit_logs WHERE date(created_at) = ?
        """, (target_date,)).fetchone()
        
        blocked_count = conn.execute("""
            SELECT COUNT(*) FROM audit_logs WHERE date(created_at) = ? AND blocked = 1
        """, (target_date,)).fetchone()
        
        # 生成摘要
        summary = "系统运行正常"
        if stats[1] and stats[1] < 90:
            summary = "成功率偏低，建议检查Agent状态"
        if blocked_count[0] and blocked_count[0] > 5:
            summary = "高危操作拦截较多，建议审查权限配置"
        
        # 保存报告
        conn.execute("""
            INSERT INTO reports (date, total_tasks, success_rate, total_cost, alert_count, blocked_count, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (target_date, stats[0] or 0, stats[1] or 0, round(stats[2] or 0, 1), alert_count[0] or 0, blocked_count[0] or 0, summary))
        
        conn.commit()
        
        return {
            "message": "Report generated successfully",
            "date": str(target_date),
            "summary": summary
        }

@router.get("/reports/{date}")
async def get_report(date: str):
    """获取指定日期的报告"""
    with get_db() as conn:
        report = conn.execute("""
            SELECT * FROM reports WHERE date = ?
        """, (date,)).fetchone()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "date": report[1],
            "tasks": report[2],
            "success_rate": report[3],
            "cost": report[4],
            "alerts": report[5],
            "blocked": report[6],
            "summary": report[7]
        }
