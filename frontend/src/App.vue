<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppNav from './components/AppNav.vue'
import AppFooter from './components/AppFooter.vue'
import LoginModal from './components/LoginModal.vue'
import HomePage from './views/HomePage.vue'
import ArticlesPage from './views/ArticlesPage.vue'
import ArticleDetailPage from './views/ArticleDetailPage.vue'
import ArticleEditorPage from './views/ArticleEditorPage.vue'
import DraftsPage from './views/DraftsPage.vue'
import PhotographyPage from './views/PhotographyPage.vue'
import AboutPage from './views/AboutPage.vue'
import ContactPage from './views/ContactPage.vue'
import ProfilePage from './views/ProfilePage.vue'
import FavoritesPage from './views/FavoritesPage.vue'
import ResetPasswordPage from './views/ResetPasswordPage.vue'
import TravelerCursor from './components/TravelerCursor.vue'
import { useTheme } from './composables/useTheme'
import { useAuth } from './composables/useAuth'
import { useRouter, type RouteName } from './router'
import { SITE_NAME } from './data/site'
import { updatePageSeo } from './utils/seo'

useTheme()
const { hydrateFromServer } = useAuth()
const { route } = useRouter()
const showIntro = ref(false)
let introTimer: number | undefined

function closeIntro() {
  showIntro.value = false
  sessionStorage.setItem('hoshino-intro-seen', '1')
  if (introTimer) window.clearTimeout(introTimer)
}

function handleIntroKey(event: KeyboardEvent) {
  if (event.key === 'Escape' && showIntro.value) closeIntro()
}

const TITLE_MAP: Record<RouteName, string> = {
  home: SITE_NAME,
  articles: `文章 · ${SITE_NAME}`,
  'article-detail': `文章 · ${SITE_NAME}`,
  'article-write': `写文章 · ${SITE_NAME}`,
  'article-edit': `编辑文章 · ${SITE_NAME}`,
  drafts: `草稿箱 · ${SITE_NAME}`,
  photography: `摄影 · ${SITE_NAME}`,
  about: `关于 · ${SITE_NAME}`,
  contact: `联系 · ${SITE_NAME}`,
  profile: `个人资料 · ${SITE_NAME}`,
  favorites: `我的收藏 · ${SITE_NAME}`,
  'reset-password': `重置密码 · ${SITE_NAME}`,
}

watch(
  () => route.value.name,
  (name) => {
    updatePageSeo({
      title: TITLE_MAP[name] || SITE_NAME,
      description: '星野文记：记录代码、语言、旅行与慢慢生活。',
      url: window.location.href,
    })
  },
  { immediate: true },
)

onMounted(() => {
  void hydrateFromServer()
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (!reduced && !sessionStorage.getItem('hoshino-intro-seen')) {
    showIntro.value = true
    introTimer = window.setTimeout(closeIntro, 7200)
    window.addEventListener('keydown', handleIntroKey)
  }
})

onBeforeUnmount(() => {
  if (introTimer) window.clearTimeout(introTimer)
  window.removeEventListener('keydown', handleIntroKey)
})
</script>

<template>
  <div class="app">
    <Transition name="intro">
      <div v-if="showIntro" class="intro-screen" role="dialog" aria-label="进入星野文记">
        <div class="intro-screen__grain" />
        <div class="intro-screen__sun" />
        <div class="intro-screen__wheat intro-screen__wheat--left">✦</div>
        <div class="intro-screen__wheat intro-screen__wheat--right">✦</div>
        <div class="intro-screen__content">
          <p class="intro-screen__eyebrow font-body">✦ 旅途 · 麦香 · 算计 ✦</p>
          <div class="intro-screen__logo" aria-label="星野文记">
            <span v-for="(letter, index) in '星野文记'.split('')" :key="letter" :style="{ '--i': index }">{{ letter }}</span>
          </div>
          <div class="intro-screen__rule" />
          <p class="intro-screen__subtitle font-serif">把沿途见闻，写成一册温柔的手记</p>
          <button type="button" class="intro-screen__enter font-body" @click="closeIntro">
            踏上旅途 <span>→</span>
          </button>
          <p class="intro-screen__hint font-body">按 Esc 跳过</p>
        </div>
      </div>
    </Transition>
    <TravelerCursor />
    <AppNav />

    <Transition name="page-transition" mode="out-in">
      <div :key="route.name">
        <HomePage v-if="route.name === 'home'" />
        <ArticlesPage v-else-if="route.name === 'articles'" />
        <ArticleDetailPage v-else-if="route.name === 'article-detail'" />
        <ArticleEditorPage v-else-if="route.name === 'article-write' || route.name === 'article-edit'" />
        <DraftsPage v-else-if="route.name === 'drafts'" />
        <PhotographyPage v-else-if="route.name === 'photography'" />
        <AboutPage v-else-if="route.name === 'about'" />
        <ContactPage v-else-if="route.name === 'contact'" />
        <ProfilePage v-else-if="route.name === 'profile'" />
        <FavoritesPage v-else-if="route.name === 'favorites'" />
        <ResetPasswordPage v-else-if="route.name === 'reset-password'" />
      </div>
    </Transition>

    <AppFooter />
    <LoginModal />
  </div>
</template>

<style scoped lang="less">
.app {
  min-height: 100%;
  background: var(--color-bg);
  transition: background-color 0.35s ease;
}

.intro-screen {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: grid;
  place-items: center;
  overflow: hidden;
  color: #f8ede4;
  background:
    radial-gradient(circle at 50% 38%, rgba(211, 164, 92, 0.16), transparent 28%),
    linear-gradient(145deg, #1b0b0e 0%, #3c171b 48%, #16090b 100%);
}

.intro-screen::before,
.intro-screen::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 50%;
  z-index: 2;
  background:
    linear-gradient(90deg, rgba(10, 4, 5, 0.68), transparent 72%),
    repeating-linear-gradient(90deg, rgba(217, 188, 166, 0.035) 0 1px, transparent 1px 18px),
    #2b1014;
  box-shadow: inset 0 0 5rem rgba(0, 0, 0, 0.35);
  transition: transform 0.75s cubic-bezier(0.76, 0, 0.24, 1);
}

.intro-screen::before { left: 0; transform-origin: left center; }
.intro-screen::after { right: 0; transform-origin: right center; transform: scaleX(-1); }

.intro-leave-active::before { transform: translateX(-100%); }
.intro-leave-active::after { transform: translateX(100%) scaleX(-1); }

.intro-screen__grain {
  position: absolute;
  inset: 0;
  opacity: 0.25;
  background-image: repeating-linear-gradient(0deg, transparent 0 4px, rgba(244, 217, 180, 0.035) 5px), repeating-linear-gradient(90deg, transparent 0 6px, rgba(116, 48, 49, 0.04) 7px);
  mix-blend-mode: screen;
}

.intro-screen__sun {
  position: absolute;
  width: min(56vw, 34rem);
  aspect-ratio: 1;
  border: 1px solid rgba(217, 188, 166, 0.18);
  border-radius: 50%;
  box-shadow: 0 0 0 2rem rgba(217, 188, 166, 0.025), 0 0 7rem rgba(201, 146, 73, 0.16);
  animation: introSun 4.2s ease both;
}

.intro-screen__content {
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  animation: introRise 1.1s 0.18s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.intro-screen__eyebrow {
  margin: 0 0 1.1rem;
  color: #d9bca6;
  font-size: 0.7rem;
  letter-spacing: 0.32em;
}

.intro-screen__rule {
  width: 5rem;
  height: 1px;
  margin-bottom: 1.2rem;
  background: linear-gradient(90deg, transparent, #d9bca6, transparent);
}

.intro-screen__logo {
  display: flex;
  gap: clamp(0.25rem, 1.5vw, 0.8rem);
  margin: 0;
  color: #f6dfc8;
  font-family: var(--font-display);
  font-size: clamp(2.7rem, 8vw, 5.6rem);
  letter-spacing: 0.05em;
  text-shadow: 0 0 2rem rgba(245, 200, 66, 0.16);

  span {
    display: inline-block;
    opacity: 0;
    filter: blur(0.5rem);
    transform: translateY(-1.8rem) rotate(calc((var(--i) - 2) * 16deg)) scale(0.72);
    animation: introLogoIn 1.05s calc(0.18s + var(--i) * 0.24s) cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }
}

.intro-screen__subtitle {
  margin: 0.8rem 0 2.1rem;
  color: rgba(248, 237, 228, 0.7);
  font-size: 0.9rem;
  letter-spacing: 0.12em;
}

.intro-screen__enter {
  padding: 0.7rem 1.3rem;
  border: 1px solid rgba(217, 188, 166, 0.45);
  color: #f6dfc8;
  letter-spacing: 0.16em;
  transition: background 0.25s ease, border-color 0.25s ease, transform 0.25s ease;

  span { display: inline-block; margin-left: 0.55rem; transition: transform 0.25s ease; }
  &:hover { background: rgba(116, 48, 49, 0.4); border-color: #d9bca6; transform: translateY(-2px); }
  &:hover span { transform: translateX(4px); }
}

.intro-screen__hint {
  margin: 1.1rem 0 0;
  color: rgba(248, 237, 228, 0.38);
  font-size: 0.62rem;
  letter-spacing: 0.1em;
}

.intro-leave-active .intro-screen__content {
  transition: opacity 0.35s ease, transform 0.55s ease;
}

.intro-leave-to .intro-screen__content {
  opacity: 0;
  transform: translateY(-0.8rem) scale(1.04);
}

.intro-screen__wheat {
  position: absolute;
  color: rgba(217, 188, 166, 0.42);
  font-size: 1.4rem;
  animation: introFloat 3.6s ease-in-out infinite;
}

.intro-screen__wheat--left { left: 18%; top: 28%; }
.intro-screen__wheat--right { right: 17%; bottom: 27%; animation-delay: 1.2s; }

@keyframes introRise { from { opacity: 0; transform: translateY(1.5rem) scale(0.97); } to { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes introSun { from { opacity: 0; transform: scale(0.72); } to { opacity: 1; transform: scale(1); } }
@keyframes introFloat { 0%, 100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-0.7rem) rotate(12deg); } }
@keyframes introLogoIn { 0% { opacity: 0; filter: blur(0.5rem); transform: translateY(-1.8rem) rotate(calc((var(--i) - 2) * 16deg)) scale(0.72); } 62% { opacity: 1; filter: blur(0); } 100% { opacity: 1; filter: blur(0); transform: translateY(0) rotate(0) scale(1); } }

.intro-enter-active,
.intro-leave-active { transition: opacity 0.7s ease, transform 0.7s ease; }
.intro-enter-from,
.intro-leave-to { opacity: 0; transform: scale(1.04); }

@media (max-width: 640px) {
  .intro-screen__subtitle { max-width: 16rem; line-height: 1.7; }
  .intro-screen__wheat--left { left: 8%; }
  .intro-screen__wheat--right { right: 8%; }
}
</style>
