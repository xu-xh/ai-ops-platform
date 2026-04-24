const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000'

export const api = {
  // 获取仪表盘数据
  async getDashboard() {
    const res = await fetch(`${API_BASE}/api/dashboard`)
    if (!res.ok) throw new Error('Failed to fetch dashboard')
    return res.json()
  },

  // 获取Agent列表
  async getAgents() {
    const res = await fetch(`${API_BASE}/api/agents`)
    if (!res.ok) throw new Error('Failed to fetch agents')
    return res.json()
  },

  // 创建Agent
  async createAgent(data: any) {
    const res = await fetch(`${API_BASE}/api/agents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to create agent')
    return res.json()
  },

  // 获取成本数据
  async getCosts(startDate?: string, endDate?: string) {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const res = await fetch(`${API_BASE}/api/costs?${params}`)
    if (!res.ok) throw new Error('Failed to fetch costs')
    return res.json()
  },

  // 获取审计日志
  async getAuditLogs(limit = 50) {
    const res = await fetch(`${API_BASE}/api/audit/logs?limit=${limit}`)
    if (!res.ok) throw new Error('Failed to fetch audit logs')
    return res.json()
  },

  // 获取报告
  async getReports() {
    const res = await fetch(`${API_BASE}/api/reports`)
    if (!res.ok) throw new Error('Failed to fetch reports')
    return res.json()
  },

  // 生成报告
  async generateReport(date: string) {
    const res = await fetch(`${API_BASE}/api/reports/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date })
    })
    if (!res.ok) throw new Error('Failed to generate report')
    return res.json()
  },

  // 更新Agent配置
  async updateAgent(id: string, data: any) {
    const res = await fetch(`${API_BASE}/api/agents/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to update agent')
    return res.json()
  },

  // 删除Agent
  async deleteAgent(id: string) {
    const res = await fetch(`${API_BASE}/api/agents/${id}`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error('Failed to delete agent')
    return res.json()
  }
}
