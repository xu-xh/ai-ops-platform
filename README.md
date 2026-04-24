# AI运维平台

"一人公司"AI数字员工的HR系统

## 项目结构

```
ai-ops-platform/
├── backend/                 # Python FastAPI 后端
│   ├── main.py             # 应用入口
│   ├── database.py        # SQLite数据库
│   ├── requirements.txt   # Python依赖
│   ├── Dockerfile         # 后端容器配置
│   └── routers/           # API路由
│       ├── dashboard.py   # 仪表盘API
│       ├── agents.py      # Agent管理API
│       ├── costs.py       # 成本管理API
│       ├── audit.py       # 安全审计API
│       └── reports.py     # 运维报告API
├── frontend/               # React 前端
│   ├── src/
│   │   ├── App.tsx        # 主应用
│   │   ├── App.css        # 样式
│   │   ├── services/api.ts # API调用
│   │   └── main.tsx       # 入口文件
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml       # Docker编排
└── README.md
```

## 功能模块

| 模块 | 说明 |
|------|------|
| 📊 仪表盘 | KPI卡片、任务趋势图、成本趋势图 |
| 👥 Agent管理 | 查看/创建/编辑/删除AI Agent |
| 💰 成本管理 | 每日/每月成本、Agent预算使用 |
| 🛡️ 安全审计 | 高危操作拦截记录、审计日志 |
| 📝 运维报告 | 每日运维报告生成与查看 |

## 快速开始

### 使用Docker（推荐）

```bash
# 克隆项目
git clone https://github.com/xu-xh/ai-ops-platform.git
cd ai-ops-platform

# 启动服务
docker-compose up
```

访问地址：
- 前端：http://localhost:3000
- 后端：http://localhost:8000
- API文档：http://localhost:8000/docs

### 手动运行

#### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

## 技术栈

- **前端**: React + TypeScript + Vite + Recharts
- **后端**: FastAPI + SQLite + Pydantic
- **部署**: Docker + Nginx

## License

MIT
