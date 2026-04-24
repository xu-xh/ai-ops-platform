"""
AI运维平台 - Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# === Enums ===
class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


class TaskStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# === Agent Schemas ===
class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    department: Optional[str] = Field(None, max_length=50)
    daily_budget: float = 10.0
    monthly_budget: float = 300.0
    is_monitoring: bool = True


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    department: Optional[str] = None
    daily_budget: Optional[float] = None
    monthly_budget: Optional[float] = None
    is_monitoring: Optional[bool] = None


class AgentResponse(AgentBase):
    id: int
    status: AgentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentStats(BaseModel):
    """Agent 统计数据"""
    total_tasks: int
    success_rate: float
    avg_response_time: float
    total_cost: float
    today_cost: float
    token_count: int


# === Task Schemas ===
class TaskBase(BaseModel):
    agent_id: int
    task_type: str
    description: Optional[str] = None
    token_count: int = 0
    response_time: float = 0.0


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    success_rate: Optional[float] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# === Cost Schemas ===
class CostRecordBase(BaseModel):
    agent_id: int
    token_count: int = 0
    cost_amount: float = 0.0
    model_name: str = "gpt-4"
    date: str


class CostRecordCreate(CostRecordBase):
    pass


class CostRecordResponse(CostRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CostSummary(BaseModel):
    """成本汇总"""
    total_cost: float
    today_cost: float
    month_cost: float
    agent_costs: List[dict]  # 按Agent汇总


# === Audit Schemas ===
class AuditLogBase(BaseModel):
    agent_id: Optional[int] = None
    action: str
    resource: str
    risk_level: RiskLevel = RiskLevel.LOW
    details: Optional[str] = None
    blocked: bool = False
    ip_address: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogResponse(AuditLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AuditStats(BaseModel):
    """审计统计"""
    total_logs: int
    blocked_count: int
    high_risk_count: int
    recent_blocks: List[AuditLogResponse]


# === Alert Schemas ===
class AlertConfigBase(BaseModel):
    name: str
    alert_type: str
    threshold: float
    enabled: bool = True
    notification_channels: str = "email"


class AlertConfigCreate(AlertConfigBase):
    pass


class AlertConfigResponse(AlertConfigBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# === Report Schemas ===
class DailyReportResponse(BaseModel):
    id: int
    report_date: str
    total_tasks: int
    success_rate: float
    total_cost: float
    active_agents: int
    total_alerts: int
    blocked_operations: int
    summary: Optional[str]
    recommendations: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# === Dashboard Schemas ===
class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    # KPI
    total_agents: int
    active_agents: int
    total_tasks_today: int
    success_rate_today: float
    avg_response_time: float
    
    # 成本
    today_cost: float
    month_cost: float
    budget_used_percent: float
    
    # 安全
    total_alerts: int
    blocked_operations_today: int
    
    # 趋势数据
    task_trend: List[dict]  # 最近7天任务趋势
    cost_trend: List[dict]  # 最近7天成本趋势
