<script setup lang="ts">
import { computed, ref } from 'vue'
import { navLinks } from '../data/posts'
import { useTheme } from '../composables/useTheme'
import { useAuth } from '../composables/useAuth'
import { useRouter } from '../router'

const menuOpen = ref(false)
const searchOpen = ref(false)
const searchQuery = ref('')
const { theme, toggleTheme } = useTheme()
const { isLoggedIn, isAuthor, user, openLogin, logout } = useAuth()
const { activePage, push, paths, route } = useRouter()
const isDraftsPage = computed(() => route.value.name === 'drafts')

function go(path: string) {
  push(path)
  menuOpen.value = false
}

function openSearch() {
  searchOpen.value = true
  menuOpen.value = false
}

function closeSearch() {
  searchOpen.value = false
  searchQuery.value = ''
}

function submitSearch() {
  const q = searchQuery.value.trim()
  if (!q) return
  push(paths.articles(q))
  closeSearch()
}

function onSearchKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') submitSearch()
  if (e.key === 'Escape') closeSearch()
}
</script>

<template>
  <nav class="nav nav-blur">
    <div class="nav__inner">
      <button class="nav__logo" type="button" @click="go('/')">
        <svg viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" class="nav__logo-icon">
          <circle cx="14" cy="14" r="12" stroke="#7eb8f7" stroke-width="1" opacity="0.4" />
          <circle cx="14" cy="14" r="6" fill="none" stroke="#f5c842" stroke-width="1.5" opacity="0.8" />
          <line x1="14" y1="2" x2="14" y2="8" stroke="#7eb8f7" stroke-width="1" opacity="0.5" />
          <line x1="14" y1="20" x2="14" y2="26" stroke="#7eb8f7" stroke-width="1" opacity="0.5" />
          <line x1="2" y1="14" x2="8" y2="14" stroke="#7eb8f7" stroke-width="1" opacity="0.5" />
          <line x1="20" y1="14" x2="26" y2="14" stroke="#7eb8f7" stroke-width="1" opacity="0.5" />
          <circle cx="14" cy="14" r="2.5" fill="#f5c842" opacity="0.9" />
        </svg>
        <span class="nav__brand font-display">星野文记</span>
      </button>

      <ul class="nav__links">
        <li v-for="item in navLinks" :key="item.page">
          <button
            type="button"
            class="nav__link font-body"
            :class="{ 'is-active': activePage === item.page }"
            @click="go(item.path)"
          >
            {{ item.label }}
            <span v-if="activePage === item.page" class="nav__underline" />
          </button>
        </li>
      </ul>

      <div class="nav__actions">
        <button
          class="nav__icon-btn"
          type="button"
          :aria-label="theme === 'dark' ? '切换为浅色主题' : '切换为深色主题'"
          @click="toggleTheme"
        >
          <!-- moon: currently dark, click to light -->
          <svg v-if="theme === 'dark'" width="18" height="18" viewBox="0 0 18 18" fill="none">
            <circle cx="9" cy="9" r="3.5" stroke="currentColor" stroke-width="1.4" />
            <path
              d="M9 1.5v1.8M9 14.7v1.8M1.5 9h1.8M14.7 9h1.8M3.4 3.4l1.3 1.3M13.3 13.3l1.3 1.3M14.6 3.4l-1.3 1.3M4.7 13.3l-1.3 1.3"
              stroke="currentColor"
              stroke-width="1.3"
              stroke-linecap="round"
            />
          </svg>
          <!-- sun shown when light; click back to dark -->
          <svg v-else width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path
              d="M14.5 10.2A5.5 5.5 0 0 1 7.8 3.5 5.6 5.6 0 1 0 14.5 10.2Z"
              stroke="currentColor"
              stroke-width="1.4"
              stroke-linejoin="round"
            />
          </svg>
        </button>

        <button class="nav__icon-btn" type="button" aria-label="搜索" @click="openSearch">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <circle cx="7.5" cy="7.5" r="5.5" stroke="currentColor" stroke-width="1.4" />
            <line
              x1="11.5"
              y1="11.5"
              x2="16"
              y2="16"
              stroke="currentColor"
              stroke-width="1.4"
              stroke-linecap="round"
            />
          </svg>
        </button>

        <div v-if="isLoggedIn" class="nav__user">
          <button
            v-if="isAuthor"
            type="button"
            class="nav__write-btn font-body"
            :class="{ 'is-active': isDraftsPage }"
            @click="go(paths.drafts())"
          >
            草稿箱
          </button>
          <button
            v-if="isAuthor"
            type="button"
            class="nav__write-btn font-body"
            @click="go(paths.write())"
          >
            写文章
          </button>
          <button type="button" class="nav__user-name font-body nav__profile-link" @click="go(paths.profile())">
            {{ user?.displayName }}
          </button>
          <button type="button" class="nav__login-btn font-body" @click="logout">退出</button>
        </div>
        <button v-else type="button" class="nav__login-btn font-body" @click="openLogin">登录</button>

        <button class="nav__icon-btn nav__menu-btn" type="button" aria-label="菜单" @click="menuOpen = !menuOpen">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <line x1="2" y1="5" x2="18" y2="5" stroke="currentColor" stroke-width="1.5" />
            <line x1="2" y1="10" x2="18" y2="10" stroke="currentColor" stroke-width="1.5" />
            <line x1="2" y1="15" x2="14" y2="15" stroke="currentColor" stroke-width="1.5" />
          </svg>
        </button>
      </div>
    </div>

    <div v-if="menuOpen" class="nav__mobile">
      <button
        v-for="item in navLinks"
        :key="item.page"
        type="button"
        class="nav__mobile-link font-body"
        @click="go(item.path)"
      >
        {{ item.label }}
      </button>
      <div class="nav__mobile-actions">
        <button type="button" class="nav__mobile-link font-body" @click="openSearch">
          搜索文章
        </button>
        <button
          v-if="isAuthor"
          type="button"
          class="nav__mobile-link font-body"
          @click="go(paths.drafts()); menuOpen = false"
        >
          草稿箱
        </button>
        <button
          v-if="isAuthor"
          type="button"
          class="nav__mobile-link font-body"
          @click="go(paths.write()); menuOpen = false"
        >
          写文章
        </button>
        <button
          v-if="isLoggedIn"
          type="button"
          class="nav__mobile-link font-body"
          @click="go(paths.profile()); menuOpen = false"
        >
          个人资料
        </button>
        <button type="button" class="nav__mobile-link font-body" @click="toggleTheme">
          {{ theme === 'dark' ? '浅色主题' : '深色主题' }}
        </button>
        <button
          v-if="isLoggedIn"
          type="button"
          class="nav__mobile-link font-body"
          @click="logout"
        >
          退出登录
        </button>
        <button v-else type="button" class="nav__mobile-link font-body" @click="openLogin(); menuOpen = false">
          登录
        </button>
      </div>
    </div>

    <div v-if="searchOpen" class="nav__search-overlay" @click.self="closeSearch">
      <div class="nav__search-panel">
        <label class="nav__search-label font-body" for="nav-search">搜索文章</label>
        <div class="nav__search-field">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" stroke-width="1.2" />
            <line x1="10" y1="10" x2="14" y2="14" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" />
          </svg>
          <input
            id="nav-search"
            v-model="searchQuery"
            type="search"
            placeholder="输入关键词…"
            class="font-body"
            autofocus
            @keydown="onSearchKeydown"
          />
          <button type="button" class="nav__search-go font-body" :disabled="!searchQuery.trim()" @click="submitSearch">
            搜索
          </button>
        </div>
        <button type="button" class="nav__search-close font-body" @click="closeSearch">取消</button>
      </div>
    </div>
  </nav>
</template>

<style scoped lang="less">
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-nav-bg);
}

.nav__inner {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav__logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav__logo-icon {
  width: 1.75rem;
  height: 1.75rem;
}

.nav__brand {
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 0.2em;
  color: var(--color-fg);
}

.nav__links {
  display: none;
  list-style: none;
  margin: 0;
  padding: 0;
  align-items: center;
  gap: 2rem;

  @media (min-width: 768px) {
    display: flex;
  }
}

.nav__link {
  position: relative;
  font-size: 1rem;
  letter-spacing: 0.1em;
  color: var(--color-muted-fg);
  padding-bottom: 2px;
  transition: color 0.2s;

  &:hover {
    color: var(--color-fg);
  }

  &.is-active {
    color: var(--color-primary);
  }
}

.nav__underline {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -2px;
  height: 1px;
  background: var(--color-primary);
  opacity: 0.7;
}

.nav__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav__icon-btn {
  color: var(--color-muted-fg);
  transition: color 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: var(--color-fg);
  }
}

.nav__write-btn {
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  color: var(--color-secondary);
  border: 1px solid rgba(142, 196, 250, 0.35);
  padding: 0.35rem 0.75rem;
  transition: all 0.2s;

  &:hover {
    background: rgba(142, 196, 250, 0.1);
    border-color: rgba(142, 196, 250, 0.55);
  }

  &.is-active {
    background: rgba(142, 196, 250, 0.15);
    border-color: rgba(142, 196, 250, 0.6);
    color: var(--color-fg);
  }
}

.nav__login-btn {
  font-size: 0.75rem;
  letter-spacing: 0.14em;
  color: var(--color-primary);
  border: 1px solid rgba(245, 200, 66, 0.35);
  padding: 0.35rem 0.85rem;
  transition: all 0.2s;

  &:hover {
    background: rgba(245, 200, 66, 0.1);
    border-color: rgba(245, 200, 66, 0.55);
  }
}

.nav__user {
  display: none;
  align-items: center;
  gap: 0.65rem;

  @media (min-width: 768px) {
    display: flex;
  }
}

.nav__user-name,
.nav__profile-link {
  font-size: 0.75rem;
  color: var(--color-soft);
  letter-spacing: 0.08em;
  max-width: 6rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav__profile-link {
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;

  &:hover {
    color: var(--color-fg);
  }
}

.nav__menu-btn {
  @media (min-width: 768px) {
    display: none;
  }
}

.nav__mobile {
  display: block;
  border-top: 1px solid var(--color-border);
  background: var(--color-nav-mobile-bg);

  @media (min-width: 768px) {
    display: none;
  }
}

.nav__mobile-actions {
  border-top: 1px solid var(--color-border);
}

.nav__mobile-link {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  letter-spacing: 0.1em;
  color: var(--color-muted-fg);
  transition:
    color 0.2s,
    background 0.2s;

  &:hover {
    color: var(--color-fg);
    background: rgba(126, 184, 247, 0.05);
  }
}

.nav__search-overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  background: rgba(6, 10, 24, 0.72);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 6rem 1.5rem 1.5rem;
}

.nav__search-panel {
  width: 100%;
  max-width: 32rem;
  padding: 1.5rem;
  border: 1px solid rgba(126, 184, 247, 0.18);
  background: var(--color-nav-mobile-bg);
}

.nav__search-label {
  display: block;
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  color: var(--color-dim);
  margin-bottom: 0.75rem;
}

.nav__search-field {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(126, 184, 247, 0.15);
  background: rgba(126, 184, 247, 0.04);
  color: var(--color-dim);

  input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--color-fg);
    font-size: 0.875rem;
    letter-spacing: 0.05em;

    &::placeholder {
      color: var(--color-faint);
    }
  }
}

.nav__search-go {
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  color: var(--color-primary);
  border: 1px solid rgba(245, 200, 66, 0.35);
  padding: 0.35rem 0.75rem;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    background: rgba(245, 200, 66, 0.1);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.nav__search-close {
  margin-top: 1rem;
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  color: var(--color-muted-fg);
  transition: color 0.2s;

  &:hover {
    color: var(--color-fg);
  }
}
</style>
