import { apiFetch } from './client'

export type UserRole = 'reader' | 'author' | 'staff'

export interface AuthUser {
  id: number
  username: string
  email: string
  displayName: string
  role?: UserRole
  isStaff?: boolean
  isAuthor?: boolean
  bio?: string
  avatar?: string
}

export interface RegisterPayload {
  email: string
  password: string
  displayName?: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface ProfileUpdatePayload {
  displayName?: string
  bio?: string
  avatar?: string
}

export interface ChangePasswordPayload {
  currentPassword: string
  newPassword: string
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
        role: 'staff',
        isStaff: true,
        isAuthor: true,
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

export async function registerRequest(payload: RegisterPayload): Promise<LoginResult> {
  const data = await apiFetch<DjangoLoginResponse>('/auth/register/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return {
    token: data.access,
    refresh: data.refresh,
    user: data.user,
  }
}

export interface SiteAuthor {
  displayName: string
  bio: string
  avatar: string
}

export interface AboutStat {
  label: string
  value: string
  sub: string
}

export interface AboutTimelineItem {
  year: string
  title: string
  desc: string
}

export interface AboutInfluence {
  name: string
  field: string
  quote: string
}

export interface AboutStackItem {
  name: string
  type: string
}

export interface SiteAbout {
  displayName: string
  avatar: string
  tagline: string
  quote: string
  body: string
  focusTags: string[]
  stats: AboutStat[]
  timeline: AboutTimelineItem[]
  timelineSubtitle: string
  influences: AboutInfluence[]
  techStack: AboutStackItem[]
  stackNote: string
}

export type SiteAboutUpdatePayload = Partial<
  Omit<SiteAbout, 'displayName' | 'avatar'>
>

export async function fetchMe(): Promise<AuthUser> {
  return apiFetch<AuthUser>('/auth/me/')
}

export async function fetchSiteAuthor(): Promise<SiteAuthor> {
  return apiFetch<SiteAuthor>('/auth/site-author/')
}

export async function fetchSiteAbout(): Promise<SiteAbout> {
  return apiFetch<SiteAbout>('/auth/site-about/')
}

export async function updateSiteAbout(payload: SiteAboutUpdatePayload): Promise<SiteAbout> {
  return apiFetch<SiteAbout>('/auth/site-about/', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function updateProfile(payload: ProfileUpdatePayload): Promise<AuthUser> {
  return apiFetch<AuthUser>('/auth/me/', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function changePassword(payload: ChangePasswordPayload): Promise<{ detail: string }> {
  return apiFetch('/auth/password/change/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function requestPasswordReset(email: string): Promise<{ detail: string }> {
  return apiFetch('/auth/password/reset/', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

export async function confirmPasswordReset(
  token: string,
  newPassword: string,
): Promise<{ detail: string }> {
  return apiFetch('/auth/password/reset/confirm/', {
    method: 'POST',
    body: JSON.stringify({ token, newPassword }),
  })
}

export async function logoutRequest(refresh?: string): Promise<void> {
  if (!refresh) return
  await apiFetch<void>('/auth/logout/', {
    method: 'POST',
    body: JSON.stringify({ refresh }),
  })
}

export async function uploadAvatar(file: File): Promise<{ url: string; path: string }> {
  const form = new FormData()
  form.append('file', file)
  const token = localStorage.getItem('hoshino-token')
  const base = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  const res = await fetch(`${base}/uploads/avatar/`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail || '头像上传失败')
  }
  return res.json()
}

