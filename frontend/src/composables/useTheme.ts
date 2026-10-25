import { ref, watch } from 'vue'

export type Theme = 'dark' | 'light'

const STORAGE_KEY = 'hoshino-theme'

const theme = ref<Theme>('dark')
let initialized = false

function applyTheme(value: Theme) {
  document.documentElement.setAttribute('data-theme', value)
}

function readStoredTheme(): Theme {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'light' || saved === 'dark') return saved
  return 'dark'
}

export function useTheme() {
  if (!initialized) {
    theme.value = readStoredTheme()
    applyTheme(theme.value)
    watch(theme, (value) => {
      applyTheme(value)
      localStorage.setItem(STORAGE_KEY, value)
    })
    initialized = true
  }

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  function setTheme(value: Theme) {
    theme.value = value
  }

  return { theme, toggleTheme, setTheme }
}
