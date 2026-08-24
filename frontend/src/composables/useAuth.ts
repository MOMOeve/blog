import { computed, ref } from 'vue'
import {
  changePassword,
  fetchMe,
  loginRequest,
  logoutRequest,
  registerRequest,
  updateProfile,
  type AuthUser,
  type ChangePasswordPayload,
  type LoginPayload,
  type ProfileUpdatePayload,
  type RegisterPayload,
} from '../api/auth'

const STORAGE_KEY = 'hoshino-auth'
const TOKEN_KEY = 'hoshino-token'
const REFRESH_KEY = 'hoshino-refresh'

function loadUser(): AuthUser | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as AuthUser
  } catch {
    return null
  }
}

const user = ref<AuthUser | null>(loadUser())
const loginOpen = ref(false)
const loading = ref(false)
const error = ref('')

function persistUser(next: AuthUser) {
  user.value = next
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
}

export function useAuth() {
  const isLoggedIn = computed(() => Boolean(user.value))
  const isStaff = computed(() => Boolean(user.value?.isStaff))
  const isAuthor = computed(() => Boolean(user.value?.isAuthor || user.value?.isStaff))

  function openLogin() {
    error.value = ''
    loginOpen.value = true
  }

  function closeLogin() {
    loginOpen.value = false
    error.value = ''
  }

  async function login(payload: LoginPayload) {
    loading.value = true
    error.value = ''
    try {
      const result = await loginRequest(payload)
      persistUser(result.user)
      localStorage.setItem(TOKEN_KEY, result.token)
      if (result.refresh) {
        localStorage.setItem(REFRESH_KEY, result.refresh)
      }
      loginOpen.value = false
    } catch (e) {
      error.value = e instanceof Error ? e.message : '登录失败，请稍后重试'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function register(payload: RegisterPayload) {
    loading.value = true
    error.value = ''
    try {
      const result = await registerRequest(payload)
      persistUser(result.user)
      localStorage.setItem(TOKEN_KEY, result.token)
      if (result.refresh) {
        localStorage.setItem(REFRESH_KEY, result.refresh)
      }
      loginOpen.value = false
    } catch (e) {
      error.value = e instanceof Error ? e.message : '注册失败，请稍后重试'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function saveProfile(payload: ProfileUpdatePayload) {
    const next = await updateProfile(payload)
    persistUser(next)
    return next
  }

  async function updatePassword(payload: ChangePasswordPayload) {
    return changePassword(payload)
  }

  async function logout() {
    const refresh = localStorage.getItem(REFRESH_KEY) || undefined
    try {
      await logoutRequest(refresh)
    } catch {
      /* ignore */
    }
    user.value = null
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
  }

  async function hydrateFromServer() {
    if (!localStorage.getItem(TOKEN_KEY)) return
    try {
      const me = await fetchMe()
      persistUser(me)
    } catch {
      user.value = null
      localStorage.removeItem(STORAGE_KEY)
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_KEY)
    }
  }

  return {
    user,
    isLoggedIn,
    isStaff,
    isAuthor,
    loginOpen,
    loading,
    error,
    openLogin,
    closeLogin,
    login,
    register,
    saveProfile,
    updatePassword,
    logout,
    hydrateFromServer,
  }
}
