import { computed, readonly, ref } from 'vue'
import type { Page } from '../types'

export type RouteName =
  | 'home'
  | 'articles'
  | 'article-detail'
  | 'article-write'
  | 'article-edit'
  | 'drafts'
  | 'photography'
  | 'about'
  | 'contact'
  | 'profile'
  | 'reset-password'

export interface AppRoute {
  name: RouteName
  params: Record<string, string>
}

export const paths = {
  home: () => '/',
  articles: (search?: string) => {
    if (!search?.trim()) return '/articles'
    return `/articles?search=${encodeURIComponent(search.trim())}`
  },
  article: (id: number) => `/articles/${id}`,
  write: () => '/write',
  edit: (id: number) => `/write/${id}`,
  drafts: () => '/drafts',
  photography: () => '/photography',
  about: () => '/about',
  contact: () => '/contact',
  profile: () => '/profile',
  resetPassword: (token?: string) =>
    token ? `/reset-password?token=${encodeURIComponent(token)}` : '/reset-password',
}

const PAGE_PATHS: Record<Page, string> = {
  首页: paths.home(),
  文章: paths.articles(),
  摄影: paths.photography(),
  关于: paths.about(),
  联系: paths.contact(),
}

function parsePath(pathname: string): AppRoute {
  const pathOnly = pathname.split('?')[0].replace(/\/+$/, '') || '/'
  const path = pathOnly
  if (path === '/') return { name: 'home', params: {} }
  if (path === '/articles') return { name: 'articles', params: {} }
  const detail = /^\/articles\/(\d+)$/.exec(path)
  if (detail) return { name: 'article-detail', params: { id: detail[1] } }
  if (path === '/write') return { name: 'article-write', params: {} }
  const edit = /^\/write\/(\d+)$/.exec(path)
  if (edit) return { name: 'article-edit', params: { id: edit[1] } }
  if (path === '/drafts') return { name: 'drafts', params: {} }
  if (path === '/photography') return { name: 'photography', params: {} }
  if (path === '/about') return { name: 'about', params: {} }
  if (path === '/contact') return { name: 'contact', params: {} }
  if (path === '/profile') return { name: 'profile', params: {} }
  if (path === '/reset-password') return { name: 'reset-password', params: {} }
  return { name: 'home', params: {} }
}

const currentRoute = ref<AppRoute>(parsePath(window.location.pathname))
let initialized = false

function scrollTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

export function initRouter() {
  if (initialized) return
  window.addEventListener('popstate', () => {
    currentRoute.value = parsePath(window.location.pathname)
    scrollTop()
  })
  initialized = true
}

export function useRouter() {
  initRouter()

  function push(path: string) {
    const next = parsePath(path)
    const target = path.startsWith('/') ? path : `/${path}`
    if (`${window.location.pathname}${window.location.search}` !== target) {
      history.pushState(null, '', target)
    }
    currentRoute.value = next
    scrollTop()
  }

  function replace(path: string) {
    history.replaceState(null, '', path)
    currentRoute.value = parsePath(path)
    scrollTop()
  }

  function goPage(page: Page) {
    push(PAGE_PATHS[page])
  }

  const activePage = computed<Page | null>(() => {
    const map: Record<RouteName, Page | null> = {
      home: '首页',
      articles: '文章',
      'article-detail': '文章',
      'article-write': '文章',
      'article-edit': '文章',
      drafts: '文章',
      photography: '摄影',
      about: '关于',
      contact: '联系',
      profile: null,
      'reset-password': null,
    }
    return map[currentRoute.value.name]
  })

  const isProfilePage = computed(() => currentRoute.value.name === 'profile')

  return {
    route: readonly(currentRoute),
    activePage,
    isProfilePage,
    push,
    replace,
    goPage,
    paths,
  }
}
