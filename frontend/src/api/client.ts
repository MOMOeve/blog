/** API 基址：开发走 Vite 代理到 Django，生产可改为完整域名 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

const VISITOR_KEY = 'hoshino-visitor-id'

/** HTTP 公网 IP 非 Secure Context，crypto.randomUUID 不可用，需回退 */
function createId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
    const bytes = new Uint8Array(16)
    crypto.getRandomValues(bytes)
    bytes[6] = (bytes[6]! & 0x0f) | 0x40
    bytes[8] = (bytes[8]! & 0x3f) | 0x80
    const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('')
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`
  }
  return `v-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`
}

function getVisitorId(): string {
  let id = localStorage.getItem(VISITOR_KEY)
  if (!id) {
    id = createId()
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
  const token = localStorage.getItem('hoshino-token')
  const headers = new Headers(init?.headers)
  if (!headers.has('Content-Type') && init?.body && !(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  if (token) headers.set('Authorization', `Bearer ${token}`)
  headers.set('X-Visitor-Id', getVisitorId())

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  })

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
