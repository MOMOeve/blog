/** API 基址：开发走 Vite 代理到 Django，生产可改为完整域名 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

const VISITOR_KEY = 'hoshino-visitor-id'
const TOKEN_KEY = 'hoshino-token'
const REFRESH_KEY = 'hoshino-refresh'
let refreshPromise: Promise<string | null> | null = null

function getVisitorId(): string {
  let id = localStorage.getItem(VISITOR_KEY)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(VISITOR_KEY, id)
  }
  return id
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status = 400) {
    super(message)
    this.status = status
  }
}

function extractErrorMessage(data: unknown, fallback: string): string {
  if (!data || typeof data !== 'object') return fallback
  const obj = data as Record<string, unknown>
  if (typeof obj.detail === 'string') return obj.detail
  if (Array.isArray(obj.detail) && obj.detail.length) {
    const first = obj.detail[0]
    if (typeof first === 'string') return first
    if (first && typeof first === 'object' && 'msg' in first) {
      return String((first as { msg: unknown }).msg)
    }
  }
  if (typeof obj.message === 'string') return obj.message
  for (const value of Object.values(obj)) {
    if (Array.isArray(value) && typeof value[0] === 'string') return value[0]
    if (typeof value === 'string') return value
  }
  return fallback
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY)
  const headers = new Headers(init?.headers)
  if (!headers.has('Content-Type') && init?.body && !(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  if (token) headers.set('Authorization', `Bearer ${token}`)
  headers.set('X-Visitor-Id', getVisitorId())

  const requestInit: RequestInit = {
    ...init,
    headers,
  }
  let res = await fetch(`${API_BASE_URL}${path}`, requestInit)

  if (res.status === 401 && !path.includes('/auth/refresh/') && localStorage.getItem(REFRESH_KEY)) {
    const nextToken = await refreshAccessToken()
    if (nextToken) {
      const retryHeaders = new Headers(requestInit.headers)
      retryHeaders.set('Authorization', `Bearer ${nextToken}`)
      res = await fetch(`${API_BASE_URL}${path}`, { ...requestInit, headers: retryHeaders })
    }
  }

  if (!res.ok) {
    let message = `请求失败 (${res.status})`
    try {
      message = extractErrorMessage(await res.json(), message)
    } catch {
      /* ignore */
    }
    throw new ApiError(message, res.status)
  }

  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise
  const refresh = localStorage.getItem(REFRESH_KEY)
  if (!refresh) return null

  refreshPromise = fetch(`${API_BASE_URL}/auth/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
    .then(async (res) => {
      if (!res.ok) throw new Error('refresh failed')
      return (await res.json()) as { access?: string; refresh?: string }
    })
    .then((data) => {
      if (!data.access) return null
      localStorage.setItem(TOKEN_KEY, data.access)
      if (data.refresh) localStorage.setItem(REFRESH_KEY, data.refresh)
      return data.access
    })
    .catch(() => {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_KEY)
      localStorage.removeItem('hoshino-auth')
      return null
    })
    .finally(() => {
      refreshPromise = null
    })
  return refreshPromise
}
