"""
AI运维平台 - 核心配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    # 应用基础
    APP_NAME: str = "AI运维平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_ops.db"
    
    # 安全
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 成本设置
    DEFAULT_DAILY_BUDGET: float = 10.0  # 默认每日预算 10 元
    DEFAULT_MONTHLY_BUDGET: float = 300.0  # 默认每月预算 300 元
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
