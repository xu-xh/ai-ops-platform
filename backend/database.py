"""
数据库模块
"""
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
import random

DATABASE = "ai_ops.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """初始化数据库表"""
    with get_db() as conn:
        # Agents表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                department TEXT,
                daily_budget REAL DEFAULT 10.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tasks表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER,
                task_type TEXT,
                success BOOLEAN,
                cost REAL,
                response_time INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        """)
        
        # Audit日志表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER,
                action TEXT,
                risk_level TEXT,
                blocked BOOLEAN,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        """)
        
        # Reports表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                total_tasks INTEGER,
                success_rate REAL,
                total_cost REAL,
                alert_count INTEGER,
                blocked_count INTEGER,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        
        # 初始化示例数据
        init_sample_data(conn)

def init_sample_data(conn):
    """初始化示例数据"""
    # 检查是否已有数据
    cursor = conn.execute("SELECT COUNT(*) FROM agents")
    if cursor.fetchone()[0] > 0:
        return
    
    # 添加Agent
    agents = [
        ("客服Agent-01", "active", "客服部", 15.0),
        ("数据Agent-02", "active", "数据部", 10.0),
        ("运维Agent-03", "active", "运维部", 20.0),
        ("营销Agent-04", "inactive", "营销部", 10.0),
        ("测试Agent-05", "error", "测试部", 5.0),
    ]
    conn.executemany(
        "INSERT INTO agents (name, status, department, daily_budget) VALUES (?, ?, ?, ?)",
        agents
    )
    
    # 生成7天的任务数据
    today = datetime.now().date()
    for i in range(7):
        date = today - timedelta(days=i)
        for agent_id in range(1, 6):
            task_count = random.randint(80, 150)
            success_rate = random.uniform(88, 98)
            cost = random.uniform(5, 20)
            
            conn.execute("""
                INSERT INTO tasks (agent_id, task_type, success, cost, response_time, created_at)
                SELECT ?, 'auto', ?, ?, ?, datetime(?)
            """, (agent_id, random.random() < success_rate/100, cost, random.randint(500, 2000), f"{date} {random.randint(0,23):02d}:{random.randint(0,59):02d}:00"))
    
    # 添加审计日志
    audit_actions = [
        (3, "delete_database", "critical", 1),
        (1, "query_users", "low", 0),
        (2, "export_data", "medium", 0),
        (3, "execute_script", "high", 1),
        (4, "send_notification", "medium", 0),
    ]
    conn.executemany(
        "INSERT INTO audit_logs (agent_id, action, risk_level, blocked) VALUES (?, ?, ?, ?)",
        audit_actions
    )
    
    # 添加报告
    reports = [
        (today - timedelta(days=2), 128, 94.5, 45.8, 3, 2, "系统运行正常"),
        (today - timedelta(days=1), 120, 93.2, 48.3, 5, 1, "运维Agent出现异常"),
        (today, 98, 90.1, 39.5, 2, 0, "成本优化建议"),
    ]
    conn.executemany(
        "INSERT INTO reports (date, total_tasks, success_rate, total_cost, alert_count, blocked_count, summary) VALUES (?, ?, ?, ?, ?, ?, ?)",
        reports
    )
    
    conn.commit()
