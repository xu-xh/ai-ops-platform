"""
AI运维平台 - 数据库模型
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class AgentStatus(str, enum.Enum):
    """Agent 状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


class TaskStatus(str, enum.Enum):
    """任务状态"""
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"


class RiskLevel(str, enum.Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Agent(Base):
    """AI Agent 模型"""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.PENDING)
    department = Column(String(50))  # 部门
    daily_budget = Column(Float, default=10.0)  # 每日预算
    monthly_budget = Column(Float, default=300.0)  # 每月预算
    is_monitoring = Column(Boolean, default=True)  # 是否监控
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    tasks = relationship("Task", back_populates="agent")
    cost_records = relationship("CostRecord", back_populates="agent")
    audit_logs = relationship("AuditLog", back_populates="agent")


class Task(Base):
    """任务记录模型"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    task_type = Column(String(50))  # 任务类型
    description = Column(Text)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    success_rate = Column(Float, default=0.0)  # 成功率
    response_time = Column(Float, default=0.0)  # 响应时间(ms)
    token_count = Column(Integer, default=0)  # Token消耗
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    agent = relationship("Agent", back_populates="tasks")


class CostRecord(Base):
    """成本记录模型"""
    __tablename__ = "cost_records"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    token_count = Column(Integer, default=0)
    cost_amount = Column(Float, default=0.0)  # 成本(元)
    model_name = Column(String(100))  # 模型名称
    date = Column(String(10))  # 日期 YYYY-MM-DD
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    agent = relationship("Agent", back_populates="cost_records")


class AuditLog(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    action = Column(String(100))  # 操作类型
    resource = Column(String(100))  # 资源
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW)
    details = Column(Text)
    blocked = Column(Boolean, default=False)  # 是否被拦截
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    agent = relationship("Agent", back_populates="audit_logs")


class AlertConfig(Base):
    """告警配置模型"""
    __tablename__ = "alert_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    alert_type = Column(String(50))  # 告警类型
    threshold = Column(Float)  # 阈值
    enabled = Column(Boolean, default=True)
    notification_channels = Column(String(200))  # 通知渠道，逗号分隔
    created_at = Column(DateTime, default=datetime.utcnow)


class DailyReport(Base):
    """每日运维报告"""
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(String(10), unique=True)  # 日期 YYYY-MM-DD
    total_tasks = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    active_agents = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)
    blocked_operations = Column(Integer, default=0)
    summary = Column(Text)  # 摘要
    recommendations = Column(Text)  # 建议
    created_at = Column(DateTime, default=datetime.utcnow)


class Settings(Base):
    """系统设置"""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
