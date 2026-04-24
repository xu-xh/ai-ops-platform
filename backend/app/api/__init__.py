"""
AI运维平台 - API 路由汇总
"""
from fastapi import APIRouter
from app.api import agents, costs, audit, dashboard

api_router = APIRouter()

# Include routers
api_router.include_router(agents.router)
api_router.include_router(costs.router)
api_router.include_router(audit.router)
api_router.include_router(dashboard.router)
api_router.include_router(dashboard.router_reports)
