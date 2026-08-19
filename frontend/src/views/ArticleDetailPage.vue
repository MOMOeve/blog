<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { fetchPost } from '../api/posts'
import type { Post } from '../types'
import { useAuth } from '../composables/useAuth'
import { renderMarkdown } from '../utils/markdown'
import { useRouter } from '../router'

const { isStaff } = useAuth()
const { route, push, paths } = useRouter()

const postId = computed(() => Number(route.value.params.id))

const post = ref<(Post & { body?: string }) | null>(null)
const loading = ref(true)
const error = ref('')

const bodyHtml = computed(() => renderMarkdown(post.value?.body || post.value?.excerpt || ''))

async function load() {
  if (!postId.value || Number.isNaN(postId.value)) {
    error.value = '无效的文章链接'
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  post.value = null
  try {
    post.value = await fetchPost(postId.value)
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

function goBack() {
  push(paths.articles())
}

function goEdit() {
  push(paths.edit(postId.value))
}

onMounted(() => {
  void load()
})

watch(postId, () => {
  void load()
})
</script>

<template>
  <div class="page-shell detail">
    <div class="container">
      <div class="detail__toolbar">
        <button type="button" class="detail__back font-body" @click="goBack">
          <svg width="14" height="8" viewBox="0 0 14 8" fill="none">
            <line x1="14" y1="4" x2="3" y2="4" stroke="currentColor" stroke-width="1.2" />
            <polyline points="6.5,1 3,4 6.5,7" fill="none" stroke="currentColor" stroke-width="1.2" />
          </svg>
          返回文章列表
        </button>
        <button v-if="isStaff && post" type="button" class="detail__edit font-body" @click="goEdit">
          编辑
        </button>
      </div>

      <div v-if="loading" class="detail__state font-body">加载中…</div>
      <div v-else-if="error" class="detail__state font-body">{{ error }}</div>

      <article v-else-if="post" class="detail__article">
        <div class="detail__meta">
          <span class="tag-pill">{{ post.category }}</span>
          <span class="font-body">{{ post.date }}</span>
          <span class="dot" />
          <span class="font-body">{{ post.readTime }}</span>
        </div>

        <h1 class="detail__title font-display">{{ post.title }}</h1>
        <p class="detail__en font-serif">{{ post.titleEn }}</p>

        <div v-if="post.img" class="detail__cover img-overlay">
          <img :src="post.img" :alt="post.title" />
        </div>

        <p class="detail__excerpt font-body">{{ post.excerpt }}</p>
        <div class="divider-light" />
        <div class="detail__body md-body" v-html="bodyHtml" />

        <div v-if="post.tags?.length" class="detail__tags">
          <span v-for="tag in post.tags" :key="tag" class="tag-pill"># {{ tag }}</span>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped lang="less">
.detail__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
}

.detail__back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  color: var(--color-muted-fg);
  transition: color 0.2s;

  &:hover {
    color: var(--color-primary);
  }
}

.detail__edit {
  font-size: 0.75rem;
  letter-spacing: 0.12em;
  padding: 0.35rem 0.85rem;
  border: 1px solid rgba(245, 200, 66, 0.35);
  color: var(--color-primary);

  &:hover {
    background: rgba(245, 200, 66, 0.1);
  }
}

.detail__state {
  color: var(--color-muted-fg);
  padding: 3rem 0;
}

.detail__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;

  .font-body {
    font-size: 0.75rem;
    color: var(--color-dim);
  }
}

.dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--color-faint);
}

.detail__title {
  margin: 0 0 0.5rem;
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  color: var(--color-fg);
  letter-spacing: 0.06em;
  line-height: 1.35;
}

.detail__en {
  margin: 0 0 1.75rem;
  font-size: 1rem;
  color: var(--color-muted-fg);
  font-style: italic;
}

.detail__cover {
  margin-bottom: 1.75rem;
  overflow: hidden;
  background: var(--color-card);

  img {
    width: 100%;
    max-height: 26rem;
    object-fit: cover;
    display: block;
  }
}

.detail__excerpt {
  font-size: 1rem;
  color: var(--color-soft);
  line-height: 1.9;
  margin: 0 0 1.5rem;
}

.detail__body {
  margin: 1.5rem 0 2rem;
}

.detail__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>
