<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchPosts } from '../api/posts'
import type { Post } from '../types'
import PostCard from '../components/PostCard.vue'
import { useRouter } from '../router'

const { push, paths } = useRouter()
const posts = ref<Post[]>([])
const loading = ref(true)

const savedIds = () => Object.keys(localStorage).filter((key) => key.startsWith('blog-bookmark:')).filter((key) => localStorage.getItem(key) === '1').map((key) => Number(key.split(':')[1]))
const favorites = computed(() => {
  const ids = new Set(savedIds())
  return posts.value.filter((post) => ids.has(post.id))
})

onMounted(async () => {
  try {
    posts.value = await fetchPosts({ ordering: '-published_at' })
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="page-shell favorites-page">
    <div class="page-header"><div class="page-header__inner"><p class="page-eyebrow">✦ &nbsp; 收藏</p><h1 class="page-title">我的收藏</h1><p class="page-desc">把想再次阅读的文章收进自己的小书架。</p></div></div>
    <div class="container">
      <p v-if="loading" class="font-body">加载中…</p>
      <div v-else-if="favorites.length" class="favorites-page__grid">
        <PostCard v-for="post in favorites" :key="post.id" :post="post" @select="push(paths.article($event.slug || $event.id))" />
      </div>
      <div v-else class="favorites-page__empty"><p class="font-display">还没有收藏文章</p><button class="font-body" type="button" @click="push(paths.articles())">去文章列表看看</button></div>
    </div>
  </main>
</template>

<style scoped lang="less">
.favorites-page__grid { display: grid; gap: 1.5rem; @media (min-width: 640px) { grid-template-columns: repeat(2, 1fr); } @media (min-width: 1024px) { grid-template-columns: repeat(3, 1fr); } }
.favorites-page__empty { padding: 6rem 0; text-align: center; color: var(--color-dim); button { margin-top: 1rem; color: var(--color-secondary); text-decoration: underline; } }
</style>
