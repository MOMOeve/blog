<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { deletePost, fetchDrafts, patchPost } from '../api/posts'
import type { Post } from '../types'
import { useAuth } from '../composables/useAuth'
import { useRouter } from '../router'

const { isStaff, openLogin } = useAuth()
const { push, paths } = useRouter()

const drafts = ref<Post[]>([])
const loading = ref(true)
const error = ref('')
const actingId = ref<number | null>(null)

async function load() {
  if (!isStaff.value) {
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    drafts.value = await fetchDrafts()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

async function publish(id: number) {
  actingId.value = id
  error.value = ''
  try {
    await patchPost(id, { published: true })
    drafts.value = drafts.value.filter((d) => d.id !== id)
  } catch (e) {
    error.value = e instanceof Error ? e.message : '发布失败'
  } finally {
    actingId.value = null
  }
}

async function remove(id: number) {
  if (!window.confirm('确定删除这篇草稿？')) return
  actingId.value = id
  error.value = ''
  try {
    await deletePost(id)
    drafts.value = drafts.value.filter((d) => d.id !== id)
  } catch (e) {
    error.value = e instanceof Error ? e.message : '删除失败'
  } finally {
    actingId.value = null
  }
}

onMounted(() => {
  void load()
})
</script>

<template>
  <div class="page-shell">
    <div class="page-header">
      <div class="page-header__glow" />
      <div class="page-header__line" />
      <div class="page-header__inner">
        <p class="page-eyebrow animate-fade-up">✦ &nbsp; DRAFTS</p>
        <h1 class="page-title animate-fade-up-delay-1">
          草稿箱
          <span class="page-title__sub">· 未发布</span>
        </h1>
        <p class="page-desc animate-fade-up-delay-2">
          共 {{ drafts.length }} 篇草稿，可随时继续编辑或发布
        </p>
      </div>
    </div>

    <div class="container drafts">
      <div v-if="!isStaff" class="drafts__warn font-body">
        需要 staff 账号才能查看草稿。
        <button type="button" class="drafts__link" @click="openLogin">去登录</button>
      </div>

      <div v-else-if="loading" class="drafts__state font-body">加载中…</div>
      <div v-else-if="error" class="drafts__state font-body">{{ error }}</div>

      <div v-else-if="!drafts.length" class="drafts__empty">
        <p class="font-body">还没有草稿</p>
        <button type="button" class="drafts__cta font-body" @click="push(paths.write())">写一篇</button>
      </div>

      <ul v-else class="drafts__list">
        <li v-for="post in drafts" :key="post.id" class="drafts__item">
          <div class="drafts__main">
            <div class="drafts__meta font-body">
              <span class="tag-pill">{{ post.category }}</span>
              <span>{{ post.date || '未设定日期' }}</span>
            </div>
            <h2 class="drafts__title font-display">{{ post.title }}</h2>
            <p class="drafts__excerpt font-body">{{ post.excerpt }}</p>
          </div>
          <div class="drafts__actions">
            <button
              type="button"
              class="font-body"
              :disabled="actingId === post.id"
              @click="push(paths.edit(post.id))"
            >
              继续编辑
            </button>
            <button
              type="button"
              class="font-body is-primary"
              :disabled="actingId === post.id"
              @click="publish(post.id)"
            >
              发布
            </button>
            <button
              type="button"
              class="font-body is-danger"
              :disabled="actingId === post.id"
              @click="remove(post.id)"
            >
              删除
            </button>
          </div>
        </li>
      </ul>

      <div v-if="isStaff && drafts.length" class="drafts__foot">
        <button type="button" class="font-body" @click="push(paths.write())">+ 新建草稿</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.drafts {
  padding-bottom: 4rem;
}

.drafts__warn {
  padding: 1rem;
  border: 1px solid rgba(245, 200, 66, 0.35);
  background: rgba(245, 200, 66, 0.08);
  color: var(--color-soft);
  font-size: 0.85rem;
}

.drafts__link {
  margin-left: 0.5rem;
  color: var(--color-primary);
  text-decoration: underline;
}

.drafts__state {
  color: var(--color-muted-fg);
  padding: 3rem 0;
}

.drafts__empty {
  text-align: center;
  padding: 4rem 0;
  color: var(--color-dim);

  p {
    margin: 0 0 1rem;
  }
}

.drafts__cta {
  padding: 0.55rem 1.25rem;
  border: 1px solid rgba(245, 200, 66, 0.4);
  color: var(--color-primary);
  letter-spacing: 0.1em;
  font-size: 0.85rem;

  &:hover {
    background: rgba(245, 200, 66, 0.12);
  }
}

.drafts__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.drafts__item {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border: 1px solid var(--color-border);
  background: var(--color-card);

  @media (min-width: 768px) {
    flex-direction: row;
    align-items: flex-start;
    justify-content: space-between;
  }
}

.drafts__meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-dim);
}

.drafts__title {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: var(--color-fg);
  letter-spacing: 0.06em;
}

.drafts__excerpt {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-soft);
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.drafts__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  flex-shrink: 0;

  button {
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    padding: 0.45rem 0.85rem;
    border: 1px solid var(--color-border);
    color: var(--color-muted-fg);
    white-space: nowrap;

    &:hover:not(:disabled) {
      color: var(--color-fg);
      border-color: var(--color-border-strong);
    }

    &:disabled {
      opacity: 0.5;
    }

    &.is-primary {
      border-color: rgba(245, 200, 66, 0.4);
      color: var(--color-primary);
    }

    &.is-danger {
      border-color: rgba(224, 112, 112, 0.35);
      color: #e07070;
    }
  }
}

.drafts__foot {
  margin-top: 2rem;
  text-align: center;

  button {
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    color: var(--color-secondary);
    border: 1px solid rgba(142, 196, 250, 0.35);
    padding: 0.5rem 1rem;

    &:hover {
      background: rgba(142, 196, 250, 0.1);
    }
  }
}
</style>
