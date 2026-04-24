import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { api } from './services/api'
import './App.css'

interface DashboardStats {
  total_agents: number
  active_agents: number
  total_tasks_today: number
  success_rate_today: number
  avg_response_time: number
  today_cost: number
  month_cost: number
  budget_used_percent: number
  total_alerts: number
  blocked_operations_today: number
  task_trend: { date: string; tasks: number; success_rate: number }[]
  cost_trend: { date: string; cost: number }[]
}

function App() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('dashboard')

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const data = await api.getDashboard()
      setStats(data)
    } catch (error) {
      console.error('Failed to load dashboard:', error)
      // 使用模拟数据
      setStats({
        total_agents: 8,
        active_agents: 6,
        total_tasks_today: 128,
        success_rate_today: 94.5,
        avg_response_time: 1250,
        today_cost: 45.8,
        month_cost: 892.3,
        budget_used_percent: 42.5,
        total_alerts: 3,
        blocked_operations_today: 2,
        task_trend: [
          { date: '04-18', tasks: 95, success_rate: 88 },
          { date: '04-19', tasks: 108, success_rate: 91 },
          { date: '04-20', tasks: 102, success_rate: 89 },
          { date: '04-21', tasks: 115, success_rate: 92 },
          { date: '04-22', tasks: 98, success_rate: 90 },
          { date: '04-23', tasks: 120, success_rate: 93 },
          { date: '04-24', tasks: 128, success_rate: 94 },
        ],
        cost_trend: [
          { date: '04-18', cost: 32.5 },
          { date: '04-19', cost: 38.2 },
          { date: '04-20', cost: 35.8 },
          { date: '04-21', cost: 42.1 },
          { date: '04-22', cost: 39.5 },
          { date: '04-23', cost: 48.3 },
          { date: '04-24', cost: 45.8 },
        ]
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      {/* 左侧导航 */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon">🤖</div>
          <span>AI运维</span>
        </div>
        <nav className="nav">
          <a 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 仪表盘
          </a>
          <a 
            className={`nav-item ${activeTab === 'agents' ? 'active' : ''}`}
            onClick={() => setActiveTab('agents')}
          >
            👥 Agent管理
          </a>
          <a 
            className={`nav-item ${activeTab === 'costs' ? 'active' : ''}`}
            onClick={() => setActiveTab('costs')}
          >
            💰 成本管理
          </a>
          <a 
            className={`nav-item ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            🛡️ 安全审计
          </a>
          <a 
            className={`nav-item ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            📝 运维报告
          </a>
        </nav>
      </aside>

      {/* 右侧内容 */}
      <main className="main-content">
        {/* 顶部 Header */}
        <header className="header">
          <h1>
            {activeTab === 'dashboard' && '业务KPI大屏'}
            {activeTab === 'agents' && 'Agent管理'}
            {activeTab === 'costs' && '成本透视'}
            {activeTab === 'security' && '安全审计'}
            {activeTab === 'reports' && '运维报告'}
          </h1>
          <div className="header-right">
            <span className="time">{new Date().toLocaleString('zh-CN')}</span>
          </div>
        </header>

        {/* 内容区域 */}
        <div className="content">
          {loading ? (
            <div className="loading">加载中...</div>
          ) : activeTab === 'dashboard' ? (
            <Dashboard stats={stats} />
          ) : activeTab === 'agents' ? (
            <AgentsPage />
          ) : activeTab === 'costs' ? (
            <CostsPage stats={stats} />
          ) : activeTab === 'security' ? (
            <SecurityPage />
          ) : (
            <ReportsPage />
          )}
        </div>
      </main>

      {/* 右侧告警栏 */}
      <aside className="alert-sidebar">
        <h3>🔔 实时告警</h3>
        <div className="alert-list">
          <div className="alert-item warning">
            <span className="alert-time">14:32</span>
            <p>Agent-03 接近日预算上限</p>
          </div>
          <div className="alert-item danger">
            <span className="alert-time">13:15</span>
            <p>高危操作已被拦截: delete_database</p>
          </div>
          <div className="alert-item info">
            <span className="alert-time">10:00</span>
            <p>每日运维报告已生成</p>
          </div>
        </div>
      </aside>
    </div>
  )
}

// 仪表盘组件
function Dashboard({ stats }: { stats: DashboardStats | null }) {
  if (!stats) return <div>暂无数据</div>

  return (
    <div className="dashboard">
      {/* KPI 卡片 */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">活跃Agent</div>
          <div className="kpi-value">{stats.active_agents}<span className="kpi-total">/{stats.total_agents}</span></div>
          <div className="kpi-trend up">↑ 2</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">今日任务</div>
          <div className="kpi-value">{stats.total_tasks_today}</div>
          <div className="kpi-trend up">↑ 8%</div>
        </div>
        <div className="kpi-card success">
          <div className="kpi-label">成功率</div>
          <div className="kpi-value">{stats.success_rate_today}%</div>
          <div className="kpi-trend up">↑ 1.2%</div>
        </div>
        <div className="kpi-card warning">
          <div className="kpi-label">今日成本</div>
          <div className="kpi-value">¥{stats.today_cost}</div>
          <div className="kpi-trend down">↓ 3%</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">本月成本</div>
          <div className="kpi-value">¥{stats.month_cost}</div>
          <div className="kpi-progress">
            <div className="progress-bar" style={{ width: `${stats.budget_used_percent}%` }}></div>
          </div>
          <span className="kpi-hint">预算使用 {stats.budget_used_percent}%</span>
        </div>
        <div className="kpi-card danger">
          <div className="kpi-label">今日拦截</div>
          <div className="kpi-value">{stats.blocked_operations_today}</div>
          <div className="kpi-hint">高危操作已拦截</div>
        </div>
      </div>

      {/* 图表区域 */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>📈 任务趋势 (7天)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={stats.task_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="date" stroke="#666" fontSize={12} />
              <YAxis stroke="#666" fontSize={12} />
              <Tooltip />
              <Line type="monotone" dataKey="tasks" stroke="#8B5CF6" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="success_rate" stroke="#10B981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>💰 成本趋势 (7天)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={stats.cost_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="date" stroke="#666" fontSize={12} />
              <YAxis stroke="#666" fontSize={12} />
              <Tooltip />
              <Bar dataKey="cost" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

// Agent管理页面
function AgentsPage() {
  const agents = [
    { id: 1, name: '客服Agent-01', status: 'active', department: '客服部', tasks: 156, success_rate: 96.5, today_cost: 12.3 },
    { id: 2, name: '数据Agent-02', status: 'active', department: '数据部', tasks: 89, success_rate: 94.2, today_cost: 8.5 },
    { id: 3, name: '运维Agent-03', status: 'active', department: '运维部', tasks: 234, success_rate: 98.1, today_cost: 15.2 },
    { id: 4, name: '营销Agent-04', status: 'inactive', department: '营销部', tasks: 45, success_rate: 91.3, today_cost: 5.8 },
    { id: 5, name: '测试Agent-05', status: 'error', department: '测试部', tasks: 12, success_rate: 75.0, today_cost: 2.1 },
  ]

  return (
    <div className="page">
      <div className="page-header">
        <button className="btn-primary">+ 新建Agent</button>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Agent名称</th>
            <th>状态</th>
            <th>部门</th>
            <th>今日任务</th>
            <th>成功率</th>
            <th>今日成本</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {agents.map(agent => (
            <tr key={agent.id}>
              <td>{agent.name}</td>
              <td>
                <span className={`status-badge ${agent.status}`}>
                  {agent.status === 'active' ? '● 活跃' : agent.status === 'inactive' ? '○ 停用' : '⚠ 异常'}
                </span>
              </td>
              <td>{agent.department}</td>
              <td>{agent.tasks}</td>
              <td>{agent.success_rate}%</td>
              <td>¥{agent.today_cost}</td>
              <td>
                <button className="btn-text">编辑</button>
                <button className="btn-text">详情</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// 成本管理页面
function CostsPage({ stats }: { stats: DashboardStats | null }) {
  const budgetStatus = [
    { agent_name: '客服Agent-01', daily_budget: 15, today_cost: 12.3, used_percent: 82, status: 'warning' },
    { agent_name: '数据Agent-02', daily_budget: 10, today_cost: 8.5, used_percent: 85, status: 'warning' },
    { agent_name: '运维Agent-03', daily_budget: 20, today_cost: 15.2, used_percent: 76, status: 'normal' },
    { agent_name: '营销Agent-04', daily_budget: 10, today_cost: 5.8, used_percent: 58, status: 'normal' },
    { agent_name: '测试Agent-05', daily_budget: 5, today_cost: 2.1, used_percent: 42, status: 'normal' },
  ]

  return (
    <div className="page">
      <div className="cost-summary">
        <div className="cost-card">
          <span className="cost-label">今日成本</span>
          <span className="cost-value">¥{stats?.today_cost || 0}</span>
        </div>
        <div className="cost-card">
          <span className="cost-label">本月成本</span>
          <span className="cost-value">¥{stats?.month_cost || 0}</span>
        </div>
        <div className="cost-card">
          <span className="cost-label">预算使用</span>
          <span className="cost-value">{stats?.budget_used_percent || 0}%</span>
        </div>
      </div>

      <h3>预算状态</h3>
      <div className="budget-list">
        {budgetStatus.map((item, idx) => (
          <div key={idx} className="budget-item">
            <div className="budget-info">
              <span className="budget-name">{item.agent_name}</span>
              <span className="budget-amount">¥{item.today_cost} / ¥{item.daily_budget}</span>
            </div>
            <div className="budget-bar">
              <div className="budget-progress" style={{ width: `${item.used_percent}%`, background: item.status === 'warning' ? '#F59E0B' : '#10B981' }}></div>
            </div>
            <span className={`budget-status ${item.status}`}>{item.used_percent}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// 安全审计页面
function SecurityPage() {
  const logs = [
    { time: '14:32:15', agent: '运维Agent-03', action: 'delete_database', risk: 'critical', blocked: true },
    { time: '14:28:33', agent: '客服Agent-01', action: 'query_users', risk: 'low', blocked: false },
    { time: '14:15:42', agent: '数据Agent-02', action: 'export_data', risk: 'medium', blocked: false },
    { time: '13:45:21', agent: '运维Agent-03', action: 'execute_script', risk: 'high', blocked: true },
    { time: '13:22:08', agent: '营销Agent-04', action: 'send_notification', risk: 'medium', blocked: false },
  ]

  return (
    <div className="page">
      <div className="security-stats">
        <div className="stat-card">
          <span className="stat-label">今日拦截</span>
          <span className="stat-value danger">2</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">高风险操作</span>
          <span className="stat-value warning">5</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">审计日志</span>
          <span className="stat-value">1,234</span>
        </div>
      </div>

      <h3>最近操作记录</h3>
      <table className="data-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>Agent</th>
            <th>操作</th>
            <th>风险等级</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, idx) => (
            <tr key={idx}>
              <td>{log.time}</td>
              <td>{log.agent}</td>
              <td>{log.action}</td>
              <td>
                <span className={`risk-badge ${log.risk}`}>
                  {log.risk === 'critical' ? '🔴 严重' : log.risk === 'high' ? '🟠 高' : log.risk === 'medium' ? '🟡 中' : '🟢 低'}
                </span>
              </td>
              <td>
                {log.blocked ? <span className="status-blocked">🚫 已拦截</span> : <span className="status-allowed">✅ 允许</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// 运维报告页面
function ReportsPage() {
  const reports = [
    { date: '2026-04-24', tasks: 128, success_rate: 94.5, cost: 45.8, alerts: 3, blocked: 2, summary: '系统运行正常' },
    { date: '2026-04-23', tasks: 120, success_rate: 93.2, cost: 48.3, alerts: 5, blocked: 1, summary: '运维Agent出现异常' },
    { date: '2026-04-22', tasks: 98, success_rate: 90.1, cost: 39.5, alerts: 2, blocked: 0, summary: '成本优化建议' },
  ]

  return (
    <div className="page">
      <div className="page-header">
        <button className="btn-primary">生成今日报告</button>
      </div>

      <div className="report-list">
        {reports.map((report, idx) => (
          <div key={idx} className="report-card">
            <div className="report-header">
              <h4>{report.date}</h4>
              <span className="report-summary">{report.summary}</span>
            </div>
            <div className="report-stats">
              <div className="report-stat">
                <span>任务数</span>
                <strong>{report.tasks}</strong>
              </div>
              <div className="report-stat">
                <span>成功率</span>
                <strong>{report.success_rate}%</strong>
              </div>
              <div className="report-stat">
                <span>成本</span>
                <strong>¥{report.cost}</strong>
              </div>
              <div className="report-stat">
                <span>告警</span>
                <strong>{report.alerts}</strong>
              </div>
              <div className="report-stat">
                <span>拦截</span>
                <strong>{report.blocked}</strong>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
