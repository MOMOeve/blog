<script setup lang="ts">
import { onMounted } from 'vue'
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
import { useTheme } from './composables/useTheme'
import { useAuth } from './composables/useAuth'
import { useRouter } from './router'

useTheme()
const { hydrateFromServer } = useAuth()
const { route } = useRouter()

onMounted(() => {
  void hydrateFromServer()
})
</script>

<template>
  <div class="app">
    <AppNav />

    <HomePage v-if="route.name === 'home'" />
    <ArticlesPage v-else-if="route.name === 'articles'" />
    <ArticleDetailPage v-else-if="route.name === 'article-detail'" />
    <ArticleEditorPage v-else-if="route.name === 'article-write' || route.name === 'article-edit'" />
    <DraftsPage v-else-if="route.name === 'drafts'" />
    <PhotographyPage v-else-if="route.name === 'photography'" />
    <AboutPage v-else-if="route.name === 'about'" />
    <ContactPage v-else-if="route.name === 'contact'" />

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
</style>
