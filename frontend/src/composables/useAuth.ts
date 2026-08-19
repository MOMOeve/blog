import { computed, ref } from 'vue'
import { fetchMe, loginRequest, logoutRequest, type AuthUser, type LoginPayload } from '../api/auth'

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

export function useAuth() {
  const isLoggedIn = computed(() => Boolean(user.value))
  const isStaff = computed(() => Boolean(user.value?.isStaff))

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
      user.value = result.user
      localStorage.setItem(STORAGE_KEY, JSON.stringify(result.user))
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

  async function logout() {
    const refresh = localStorage.getItem(REFRESH_KEY) || undefined
    try {
      await logoutRequest(refresh)
    } catch {
      /* ignore network errors on logout */
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
      user.value = me
      localStorage.setItem(STORAGE_KEY, JSON.stringify(me))
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
    loginOpen,
    loading,
    error,
    openLogin,
    closeLogin,
    login,
    logout,
    hydrateFromServer,
  }
}
