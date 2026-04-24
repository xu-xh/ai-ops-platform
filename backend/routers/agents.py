"""
Agent管理路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db

router = APIRouter()

class AgentCreate(BaseModel):
    name: str
    department: str
    daily_budget: float = 10.0

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    department: Optional[str] = None
    daily_budget: Optional[float] = None

@router.get("/agents")
async def get_agents():
    """获取所有Agent"""
    with get_db() as conn:
        today = conn.execute("SELECT date('now')").fetchone()[0]
        
        agents = conn.execute("""
            SELECT 
                a.id, a.name, a.status, a.department, a.daily_budget,
                COUNT(t.id) as task_count,
                ROUND(COALESCE(AVG(CASE WHEN t.success = 1 THEN 100.0 ELSE 0.0 END), 0), 1) as success_rate,
                COALESCE(SUM(t.cost), 0) as today_cost
            FROM agents a
            LEFT JOIN tasks t ON a.id = t.agent_id AND date(t.created_at) = ?
            GROUP BY a.id
            ORDER BY a.id
        """, (today,)).fetchall()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "status": row[2],
                "department": row[3],
                "daily_budget": row[4],
                "tasks": row[5] or 0,
                "success_rate": row[6] or 0,
                "today_cost": round(row[7], 1)
            }
            for row in agents
        ]

@router.post("/agents")
async def create_agent(agent: AgentCreate):
    """创建新Agent"""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO agents (name, department, daily_budget) VALUES (?, ?, ?)",
            (agent.name, agent.department, agent.daily_budget)
        )
        conn.commit()
        return {"id": cursor.lastrowid, "message": "Agent created successfully"}

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: int):
    """获取单个Agent详情"""
    with get_db() as conn:
        agent = conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "id": agent[0],
            "name": agent[1],
            "status": agent[2],
            "department": agent[3],
            "daily_budget": agent[4]
        }

@router.put("/agents/{agent_id}")
async def update_agent(agent_id: int, agent: AgentUpdate):
    """更新Agent"""
    with get_db() as conn:
        agent_exists = conn.execute("SELECT id FROM agents WHERE id = ?", (agent_id,)).fetchone()
        if not agent_exists:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        updates = []
        values = []
        if agent.name:
            updates.append("name = ?")
            values.append(agent.name)
        if agent.status:
            updates.append("status = ?")
            values.append(agent.status)
        if agent.department:
            updates.append("department = ?")
            values.append(agent.department)
        if agent.daily_budget:
            updates.append("daily_budget = ?")
            values.append(agent.daily_budget)
        
        if updates:
            values.append(agent_id)
            conn.execute(f"UPDATE agents SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        
        return {"message": "Agent updated successfully"}

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int):
    """删除Agent"""
    with get_db() as conn:
        agent = conn.execute("SELECT id FROM agents WHERE id = ?", (agent_id,)).fetchone()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        conn.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
        conn.commit()
        
        return {"message": "Agent deleted successfully"}
