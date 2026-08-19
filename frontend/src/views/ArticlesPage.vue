<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { allPosts as fallbackPosts, categories as fallbackCategories } from '../data/posts'
import { fetchCategoryNames, fetchPosts } from '../api/posts'
import type { Post } from '../types'
import { useAuth } from '../composables/useAuth'
import { useRouter } from '../router'

type ViewMode = 'grid' | 'list'
type SortBy = 'newest' | 'oldest'

const { isStaff } = useAuth()
const { push, paths } = useRouter()

const activeCategory = ref('全部')
const searchQuery = ref('')
const viewMode = ref<ViewMode>('grid')
const sortBy = ref<SortBy>('newest')
const posts = ref<Post[]>(fallbackPosts)
const categories = ref<string[]>(fallbackCategories)
const useRemote = ref(false)

const filtered = computed(() => {
  let result = posts.value.filter((p) => {
    const matchCat = activeCategory.value === '全部' || p.category === activeCategory.value
    const q = searchQuery.value
    const matchSearch =
      !q || p.title.includes(q) || p.excerpt.includes(q) || p.tags.some((t) => t.includes(q))
    return matchCat && matchSearch
  })
  if (sortBy.value === 'oldest') result = [...result].reverse()
  return result
})

async function loadPosts() {
  try {
    const remote = await fetchPosts({
      category: activeCategory.value,
      search: searchQuery.value || undefined,
      ordering: sortBy.value === 'oldest' ? 'published_at' : '-published_at',
    })
    if (remote.length || useRemote.value) {
      posts.value = remote
      useRemote.value = true
    }
  } catch {
    /* keep fallback */
  }
}

onMounted(async () => {
  try {
    const names = await fetchCategoryNames()
    if (names.length) categories.value = names
  } catch {
    /* keep fallback */
  }
  await loadPosts()
})

watch([activeCategory, searchQuery, sortBy], () => {
  if (useRemote.value) void loadPosts()
})

function clearFilters() {
  searchQuery.value = ''
  activeCategory.value = '全部'
}
</script>

<template>
  <div class="page-shell">
    <div class="page-header">
      <div class="page-header__glow" />
      <div class="page-header__line" />
      <div class="page-header__inner">
        <p class="page-eyebrow animate-fade-up">✦ &nbsp; ARTICLES</p>
        <h1 class="page-title animate-fade-up-delay-1">
          文章
          <span class="page-title__sub">· 所有文字</span>
        </h1>
        <p class="page-desc animate-fade-up-delay-2">
          共 {{ posts.length }} 篇文章，关于代码、语言与那些值得记下来的日子
        </p>
        <button
          v-if="isStaff"
          type="button"
          class="articles__write font-body animate-fade-up-delay-2"
          @click="push(paths.drafts())"
        >
          草稿箱
        </button>
        <button
          v-if="isStaff"
          type="button"
          class="articles__write font-body animate-fade-up-delay-2"
          @click="push(paths.write())"
        >
          写文章
        </button>
      </div>
    </div>

    <div class="container">
      <div class="articles__controls">
        <div class="articles__cats">
          <button
            v-for="cat in categories"
            :key="cat"
            type="button"
            class="filter-btn"
            :class="{ 'is-active': activeCategory === cat }"
            @click="activeCategory = cat"
          >
            {{ cat }}
          </button>
        </div>

        <div class="articles__tools">
          <div class="articles__search">
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <circle cx="5.5" cy="5.5" r="4" stroke="currentColor" stroke-width="1.2" />
              <line
                x1="8.5"
                y1="8.5"
                x2="12"
                y2="12"
                stroke="currentColor"
                stroke-width="1.2"
                stroke-linecap="round"
              />
            </svg>
            <input v-model="searchQuery" type="text" placeholder="搜索文章…" class="font-body" />
          </div>

          <select v-model="sortBy" class="font-body">
            <option value="newest">最新</option>
            <option value="oldest">最早</option>
          </select>

          <div class="articles__view">
            <button
              type="button"
              :class="{ 'is-active': viewMode === 'grid' }"
              @click="viewMode = 'grid'"
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <rect x="1" y="1" width="5" height="5" stroke="currentColor" stroke-width="1.2" />
                <rect x="8" y="1" width="5" height="5" stroke="currentColor" stroke-width="1.2" />
                <rect x="1" y="8" width="5" height="5" stroke="currentColor" stroke-width="1.2" />
                <rect x="8" y="8" width="5" height="5" stroke="currentColor" stroke-width="1.2" />
              </svg>
            </button>
            <button
              type="button"
              :class="{ 'is-active': viewMode === 'list' }"
              @click="viewMode = 'list'"
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <line x1="1" y1="3" x2="13" y2="3" stroke="currentColor" stroke-width="1.2" />
                <line x1="1" y1="7" x2="13" y2="7" stroke="currentColor" stroke-width="1.2" />
                <line x1="1" y1="11" x2="13" y2="11" stroke="currentColor" stroke-width="1.2" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <p v-if="searchQuery || activeCategory !== '全部'" class="articles__count font-body">
        找到 {{ filtered.length }} 篇文章
        <span v-if="searchQuery">「{{ searchQuery }}」</span>
      </p>

      <div v-if="!filtered.length" class="articles__empty">
        <p class="font-display">未找到相关文章</p>
        <button type="button" class="font-body" @click="clearFilters">清除筛选</button>
      </div>

      <div v-else-if="viewMode === 'grid'" class="articles__grid">
        <article v-for="post in filtered" :key="post.id" class="grid-card" @click="push(paths.article(post.id))">
          <div class="grid-card__media">
            <img :src="post.img" :alt="post.title" />
            <span class="font-body">{{ post.category }}</span>
          </div>
          <div class="grid-card__body">
            <h3 class="font-display">{{ post.title }}</h3>
            <p class="en font-serif">{{ post.titleEn }}</p>
            <p class="excerpt font-body">{{ post.excerpt.slice(0, 72) }}…</p>
            <div class="meta font-body">
              <span>{{ post.date }}</span>
              <span>{{ post.readTime }}</span>
            </div>
          </div>
        </article>
      </div>

      <div v-else class="articles__list">
        <article v-for="post in filtered" :key="post.id" class="list-row" @click="push(paths.article(post.id))">
          <div class="list-row__thumb">
            <img :src="post.img" :alt="post.title" />
          </div>
          <div class="list-row__body">
            <div class="list-row__meta font-body">
              <span class="cat">{{ post.category }}</span>
              <span>{{ post.date }}</span>
              <span>{{ post.readTime }}</span>
            </div>
            <h3 class="font-display">{{ post.title }}</h3>
            <p class="font-body">{{ post.excerpt.slice(0, 100) }}…</p>
          </div>
          <svg width="16" height="10" viewBox="0 0 16 10" fill="none" class="list-row__arrow">
            <line x1="0" y1="5" x2="13" y2="5" stroke="currentColor" stroke-width="1.2" />
            <polyline points="9,1 13,5 9,9" fill="none" stroke="currentColor" stroke-width="1.2" />
          </svg>
        </article>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.articles__controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(126, 184, 247, 0.1);

  @media (min-width: 768px) {
    flex-direction: row;
    align-items: center;
  }
}

.articles__write {
  margin-top: 1.25rem;
  font-size: 0.8rem;
  letter-spacing: 0.12em;
  padding: 0.45rem 1rem;
  border: 1px solid rgba(245, 200, 66, 0.4);
  color: var(--color-primary);
  background: rgba(245, 200, 66, 0.1);

  &:hover {
    background: rgba(245, 200, 66, 0.2);
  }
}

.articles__cats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.articles__tools {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.articles__search {
  position: relative;
  color: #3d5070;

  svg {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
  }

  input {
    padding: 0.5rem 1rem 0.5rem 2rem;
    background: rgba(126, 184, 247, 0.04);
    border: 1px solid rgba(126, 184, 247, 0.12);
    color: var(--color-fg);
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    width: 9rem;
    outline: none;

    &::placeholder {
      color: var(--color-faint);
    }

    &:focus {
      border-color: rgba(126, 184, 247, 0.35);
    }
  }
}

select {
  background: rgba(126, 184, 247, 0.04);
  border: 1px solid rgba(126, 184, 247, 0.12);
  color: var(--color-muted-fg);
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  padding: 0.5rem 0.75rem;
  outline: none;
  cursor: pointer;

  &:focus {
    border-color: rgba(126, 184, 247, 0.35);
  }
}

.articles__view {
  display: flex;
  border: 1px solid rgba(126, 184, 247, 0.12);

  button {
    padding: 0.5rem;
    color: #3d5070;
    transition: color 0.2s, background 0.2s;

    &.is-active {
      background: rgba(126, 184, 247, 0.1);
      color: var(--color-secondary);
    }

    &:hover {
      color: var(--color-muted-fg);
    }
  }
}

.articles__count {
  font-size: 0.75rem;
  color: #3d5070;
  letter-spacing: 0.05em;
  margin: 0 0 1.5rem;

  span {
    color: var(--color-secondary);
    margin-left: 0.25rem;
  }
}

.articles__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 7rem 0;
  text-align: center;

  p {
    font-size: 0.875rem;
    color: #3d5070;
    letter-spacing: 0.2em;
    margin: 0;
  }

  button {
    margin-top: 1rem;
    font-size: 0.75rem;
    color: var(--color-secondary);
    letter-spacing: 0.05em;
    text-decoration: underline;
    text-underline-offset: 4px;
  }
}

.articles__grid {
  display: grid;
  gap: 1.5rem;

  @media (min-width: 640px) {
    grid-template-columns: 1fr 1fr;
  }

  @media (min-width: 1024px) {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

.grid-card {
  border: 1px solid rgba(126, 184, 247, 0.08);
  background: linear-gradient(145deg, rgba(11, 16, 40, 0.85), rgba(8, 12, 28, 0.92));
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: border-color 0.5s;

  &:hover {
    border-color: rgba(126, 184, 247, 0.22);

    h3 {
      color: var(--color-primary);
    }

    img {
      opacity: 0.9;
      transform: scale(1.04);
    }
  }
}

.grid-card__media {
  position: relative;
  height: 11rem;
  overflow: hidden;
  background: var(--color-card);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.7;
    filter: saturate(1.1);
    transition: all 0.7s;
  }

  span {
    position: absolute;
    top: 0.75rem;
    left: 0.75rem;
    z-index: 10;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    padding: 0.25rem 0.625rem;
    background: rgba(18, 26, 46, 0.7);
    border: 1px solid rgba(126, 184, 247, 0.2);
    color: var(--color-secondary);
  }

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, transparent 40%, rgba(18, 26, 46, 0.8));
  }
}

.grid-card__body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  flex: 1;

  h3 {
    font-size: 0.875rem;
    line-height: 1.4;
    color: var(--color-fg);
    letter-spacing: 0.04em;
    margin: 0 0 0.375rem;
    transition: color 0.3s;
  }

  .en {
    font-style: italic;
    font-size: 0.68rem;
    color: #3a4e68;
    margin: 0 0 0.75rem;
  }

  .excerpt {
    font-size: 0.75rem;
    color: var(--color-dim);
    line-height: 1.8;
    font-weight: 300;
    flex: 1;
    margin: 0 0 1rem;
  }

  .meta {
    display: flex;
    justify-content: space-between;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(126, 184, 247, 0.06);
    font-size: 0.65rem;
    color: #2f3f56;
    letter-spacing: 0.05em;
  }
}

.articles__list {
  display: flex;
  flex-direction: column;
}

.list-row {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
  padding: 1.5rem 0.5rem;
  margin: 0 -0.5rem;
  cursor: pointer;
  border-bottom: 1px solid rgba(126, 184, 247, 0.08);
  transition: background 0.3s;

  &:hover {
    background: rgba(126, 184, 247, 0.02);

    h3 {
      color: var(--color-primary);
    }

    .list-row__arrow {
      color: var(--color-secondary);
      transform: translateX(4px);
    }

    img {
      opacity: 0.85;
    }
  }
}

.list-row__thumb {
  width: 6rem;
  height: 4rem;
  flex-shrink: 0;
  overflow: hidden;
  background: var(--color-card);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.65;
    transition: opacity 0.4s;
  }
}

.list-row__body {
  flex: 1;
  min-width: 0;

  h3 {
    font-size: 0.875rem;
    line-height: 1.4;
    color: var(--color-fg);
    letter-spacing: 0.04em;
    margin: 0 0 0.25rem;
    transition: color 0.3s;
  }

  > .font-body {
    font-size: 0.75rem;
    color: var(--color-dim);
    line-height: 1.8;
    font-weight: 300;
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.list-row__meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  font-size: 0.65rem;
  color: #2f3f56;
  letter-spacing: 0.05em;

  .cat {
    letter-spacing: 0.12em;
    padding: 0.125rem 0.5rem;
    border: 1px solid rgba(126, 184, 247, 0.18);
    color: var(--color-secondary);
  }
}

.list-row__arrow {
  flex-shrink: 0;
  align-self: center;
  color: #2f3f56;
  transition: all 0.2s;
}
</style>
