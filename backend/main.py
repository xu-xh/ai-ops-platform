"""
AI运维平台后端主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import dashboard, agents, costs, audit, reports
from database import init_db

app = FastAPI(title="AI运维平台", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(agents.router, prefix="/api", tags=["Agents"])
app.include_router(costs.router, prefix="/api", tags=["Costs"])
app.include_router(audit.router, prefix="/api", tags=["Audit"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])

# 初始化数据库
@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
async def root():
    return {"message": "AI运维平台 API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}
