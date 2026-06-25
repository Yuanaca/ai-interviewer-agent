import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 响应拦截器
api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.detail || err.message || '请求失败'
    console.error('[API Error]', msg)
    return Promise.reject(new Error(msg))
  }
)

// ===================== 面试 =====================
export const interviewAPI = {
  /** 创建面试会话 */
  create(data) {
    return api.post('/interview/create', data)
  },
  /** 提交回答 */
  submitAnswer(data) {
    return api.post('/interview/answer', data)
  },
  /** 获取会话状态 */
  getState(sessionId) {
    return api.get(`/interview/state/${sessionId}`)
  },
  /** 列出所有会话 */
  listSessions() {
    return api.get('/interview/sessions')
  },
  /** 获取报告 */
  getReport(sessionId) {
    return api.get(`/interview/report/${sessionId}`)
  },
  /** 列出所有报告 */
  listReports() {
    return api.get('/interview/reports')
  },
  /** 单独分析简历 */
  analyzeResume(resumeText, llmConfig) {
    return api.post('/interview/resume/analyze', { resume_text: resumeText, llm_config: llmConfig })
  },
}

// ===================== 职位 =====================
export const jobsAPI = {
  list() {
    return api.get('/jobs')
  },
  get(id) {
    return api.get(`/jobs/${id}`)
  },
  create(data) {
    return api.post('/jobs', data)
  },
  update(id, data) {
    return api.put(`/jobs/${id}`, data)
  },
  delete(id) {
    return api.delete(`/jobs/${id}`)
  },
}

// ===================== 知识库 =====================
export const knowledgeAPI = {
  list(category) {
    return api.get('/knowledge', { params: { category } })
  },
  get(id) {
    return api.get(`/knowledge/${id}`)
  },
  create(data) {
    return api.post('/knowledge', data)
  },
  update(id, data) {
    return api.put(`/knowledge/${id}`, data)
  },
  delete(id) {
    return api.delete(`/knowledge/${id}`)
  },
  search(query, topK = 5) {
    return api.post('/knowledge/search', { query, top_k: topK })
  },
  rebuildIndex() {
    return api.post('/knowledge/rebuild-index')
  },
}

// ===================== 健康检查 =====================
export const healthAPI = {
  check() {
    return api.get('/health')
  },
}

export default api
