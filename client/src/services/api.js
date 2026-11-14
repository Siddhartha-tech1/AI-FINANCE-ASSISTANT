const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:5000/api/v1'

export function getToken() { return localStorage.getItem('finance_access_token') }
export function setToken(token) { localStorage.setItem('finance_access_token', token) }
export function clearToken() { localStorage.removeItem('finance_access_token') }

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}), ...options.headers },
  })
  if (response.status === 204) return null
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(body.message ?? body.error ?? 'Request failed')
  return body
}

export const api = {
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request('/auth/me'),
  logout: () => request('/auth/logout', { method: 'POST' }),
  summary: (month) => request(`/dashboard/summary${month ? `?month=${month}` : ''}`),
  transactions: (filters = {}) => {
    const query = new URLSearchParams(Object.entries(filters).filter(([, value]) => value !== '' && value !== undefined && value !== null)).toString()
    return request(`/transactions${query ? `?${query}` : ''}`)
  },
  createTransaction: (data) => request('/transactions', { method: 'POST', body: JSON.stringify(data) }),
  updateTransaction: (id, data) => request(`/transactions/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTransaction: (id) => request(`/transactions/${id}`, { method: 'DELETE' }),
  budgets: () => request('/budgets'),
  createBudget: (data) => request('/budgets', { method: 'POST', body: JSON.stringify(data) }),
  updateBudget: (id, data) => request(`/budgets/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteBudget: (id) => request(`/budgets/${id}`, { method: 'DELETE' }),
  budgetStatus: (month) => request(`/budgets/status${month ? `?month=${month}` : ''}`),
  categories: (month) => request(`/analytics/category-breakdown${month ? `?month=${month}` : ''}`),
  trends: () => request('/analytics/monthly-trends'),
  insights: () => request('/insights'),
  predictCategory: (description) => request('/ml/predict-category', { method: 'POST', body: JSON.stringify({ description }) }),
  forecast: () => request('/ml/forecast'),
  chat: (message) => request('/chat', { method: 'POST', body: JSON.stringify({ message }) }),
}
