import { apiFetch } from './client'

export interface AuthUser {
  id: number
  username: string
  email: string
  displayName: string
  isStaff?: boolean
}

export interface LoginPayload {
  email: string
  password: string
}

export interface LoginResult {
  user: AuthUser
  token: string
  refresh?: string
}

interface DjangoLoginResponse {
  access: string
  refresh: string
  user: AuthUser
}

/**
 * 登录：默认请求 Django `POST /api/v1/auth/login/`
 * 设置 VITE_USE_AUTH_MOCK=true 可切回本地 mock
 */
export async function loginRequest(payload: LoginPayload): Promise<LoginResult> {
  const useMock = import.meta.env.VITE_USE_AUTH_MOCK === 'true'

  if (useMock) {
    await new Promise((r) => setTimeout(r, 700))
    if (!payload.email || !payload.password) {
      throw new Error('请输入邮箱和密码')
    }
    if (payload.password.length < 4) {
      throw new Error('密码至少 4 位（演示用）')
    }
    return {
      token: `mock-token-${Date.now()}`,
      user: {
        id: 1,
        username: payload.email.split('@')[0] || 'user',
        email: payload.email,
        displayName: payload.email.split('@')[0] || '旅行者',
        isStaff: true,
      },
    }
  }

  const data = await apiFetch<DjangoLoginResponse>('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

  return {
    token: data.access,
    refresh: data.refresh,
    user: data.user,
  }
}

/** GET /api/v1/auth/me/ */
export async function fetchMe(): Promise<AuthUser> {
  return apiFetch<AuthUser>('/auth/me/')
}

/** POST /api/v1/auth/logout/ */
export async function logoutRequest(refresh?: string): Promise<void> {
  if (!refresh) return
  await apiFetch<void>('/auth/logout/', {
    method: 'POST',
    body: JSON.stringify({ refresh }),
  })
}
