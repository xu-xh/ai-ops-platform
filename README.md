# AI Operations Platform

"一人公司"AI运维平台 - AI数字员工的HR系统

## 项目结构

```
ai-ops-platform/
├── backend/           # Python FastAPI 后端
│   ├── app/
│   │   ├── api/       # API 路由
│   │   ├── core/      # 核心配置
│   │   ├── models/    # 数据库模型
│   │   ├── schemas/   # Pydantic 模型
│   │   └── services/  # 业务逻辑
│   └── tests/         # 测试
└── frontend/          # React 前端
    ├── src/
    │   ├── components/# 公共组件
    │   ├── pages/     # 页面
    │   ├── hooks/     # 自定义 Hooks
    │   ├── services/  # API 调用
    │   ├── types/     # TypeScript 类型
    │   └── utils/     # 工具函数
    └── public/
```

## 快速开始

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 核心功能

1. **业务KPI大屏** - 任务成功率、响应时间、活跃Agent数
2. **成本透视** - Token消耗统计、预算熔断
3. **安全审计** - 监管智能体、高危操作拦截
4. **运维报告** - 每日AI团队日报
