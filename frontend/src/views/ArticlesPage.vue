<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { allPosts as fallbackPosts, categories as fallbackCategories } from '../data/posts'
import { fetchArchive, fetchCategoryNames, fetchPostsPage, fetchTagCloud, POSTS_PAGE_SIZE, type ArchiveItem, type TagCloudItem } from '../api/posts'
import type { Post } from '../types'
import { useAuth } from '../composables/useAuth'
import { useRouter } from '../router'
import MediaCover from '../components/MediaCover.vue'

type ViewMode = 'grid' | 'list'
type SortBy = 'newest' | 'oldest'

const { isAuthor } = useAuth()
const { push, paths, route } = useRouter()

const activeCategory = ref('全部')
const activeTag = ref('')
const activeYear = ref<number | null>(null)
const activeMonth = ref<number | null>(null)
const searchQuery = ref('')
const viewMode = ref<ViewMode>('grid')
const sortBy = ref<SortBy>('newest')
const currentPage = ref(1)
const totalCount = ref(0)
const posts = ref<Post[]>([])
const categories = ref<string[]>(['全部'])
const useRemote = ref(false)
const loading = ref(true)
const tagCloud = ref<TagCloudItem[]>([])
const archive = ref<ArchiveItem[]>([])

function readUrlState() {
  const params = new URLSearchParams(window.location.search)
  searchQuery.value = params.get('search') ?? ''
  activeTag.value = params.get('tag') ?? ''
  activeYear.value = params.get('year') ? Number(params.get('year')) : null
  activeMonth.value = params.get('month') ? Number(params.get('month')) : null
  currentPage.value = Math.max(1, Number(params.get('page') || 1))
}

function syncUrl() {
  const params = new URLSearchParams()
  if (searchQuery.value.trim()) params.set('search', searchQuery.value.trim())
  if (activeTag.value) params.set('tag', activeTag.value)
  if (activeYear.value) params.set('year', String(activeYear.value))
  if (activeMonth.value) params.set('month', String(activeMonth.value))
  if (currentPage.value > 1) params.set('page', String(currentPage.value))
  const qs = params.toString()
  const path = qs ? `/articles?${qs}` : '/articles'
  if (`${window.location.pathname}${window.location.search}` !== path) {
    history.replaceState(null, '', path)
  }
}

const filtered = computed(() => {
  if (useRemote.value) return posts.value
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

const totalPages = computed(() =>
  useRemote.value ? Math.max(1, Math.ceil(totalCount.value / POSTS_PAGE_SIZE)) : 1,
)

const displayCount = computed(() => (useRemote.value ? totalCount.value : filtered.value.length))

const pageNumbers = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages: number[] = []
  const start = Math.max(1, current - 2)
  const end = Math.min(total, current + 2)
  for (let i = start; i <= end; i += 1) pages.push(i)
  return pages
})

async function loadPosts() {
  loading.value = true
  try {
    const data = await fetchPostsPage({
      category: activeCategory.value,
      tag: activeTag.value || undefined,
      year: activeYear.value ?? undefined,
      month: activeMonth.value ?? undefined,
      search: searchQuery.value || undefined,
      ordering: sortBy.value === 'oldest' ? 'published_at' : '-published_at',
      page: currentPage.value,
    })
    posts.value = data.results
    totalCount.value = data.count
    useRemote.value = true
  } catch {
    if (!useRemote.value) {
      posts.value = fallbackPosts
      categories.value = fallbackCategories
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  readUrlState()
  try {
    const [names, tags, months] = await Promise.all([
      fetchCategoryNames(),
      fetchTagCloud(),
      fetchArchive(),
    ])
    if (names.length) categories.value = names
    tagCloud.value = tags
    archive.value = months
  } catch {
    /* keep fallback */
  }
  await loadPosts()
})

watch(route, (r) => {
  if (r.name !== 'articles') return
  readUrlState()
  void loadPosts()
})

watch([activeCategory, activeTag, activeYear, activeMonth, searchQuery, sortBy], () => {
  if (!useRemote.value) return
  currentPage.value = 1
  syncUrl()
  void loadPosts()
})

watch(currentPage, () => {
  if (!useRemote.value) return
  syncUrl()
  void loadPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
})

function clearFilters() {
  searchQuery.value = ''
  activeCategory.value = '全部'
  activeTag.value = ''
  activeYear.value = null
  activeMonth.value = null
  currentPage.value = 1
  syncUrl()
  if (useRemote.value) void loadPosts()
}

function selectTag(name: string) {
  activeTag.value = activeTag.value === name ? '' : name
  activeYear.value = null
  activeMonth.value = null
  currentPage.value = 1
  syncUrl()
  if (useRemote.value) void loadPosts()
}

function selectArchive(year: number, month: number) {
  const same = activeYear.value === year && activeMonth.value === month
  activeYear.value = same ? null : year
  activeMonth.value = same ? null : month
  activeTag.value = ''
  currentPage.value = 1
  syncUrl()
  if (useRemote.value) void loadPosts()
}

const archiveByYear = computed(() => {
  const map = new Map<number, ArchiveItem[]>()
  for (const item of archive.value) {
    const list = map.get(item.year) ?? []
    list.push(item)
    map.set(item.year, list)
  }
  return [...map.entries()].sort((a, b) => b[0] - a[0])
})

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
}
</script>

<template>
  <div class="page-shell">
    <div class="page-header">
      <div class="page-header__glow" />
      <div class="page-header__line" />
      <div class="page-header__inner">
        <p class="page-eyebrow animate-fade-up">✦ &nbsp; 手记</p>
        <h1 class="page-title animate-fade-up-delay-1">
          文章
          <span class="page-title__sub">· 旅途见闻</span>
        </h1>
        <p class="page-desc animate-fade-up-delay-2">
          共 {{ displayCount }} 篇，像货单一样列着沿途记下的事
        </p>
        <button
          v-if="isAuthor"
          type="button"
          class="articles__write font-body animate-fade-up-delay-2"
          @click="push(paths.drafts())"
        >
          草稿箱
        </button>
        <button
          v-if="isAuthor"
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

      <div class="articles__layout">
        <aside v-if="tagCloud.length || archiveByYear.length" class="articles__sidebar">
          <section v-if="tagCloud.length" class="articles__side-block">
            <h3 class="font-display">标签云</h3>
            <div class="articles__tags">
              <button
                v-for="tag in tagCloud"
                :key="tag.name"
                type="button"
                class="font-body"
                :class="{ 'is-active': activeTag === tag.name }"
                :style="{ fontSize: `${0.65 + Math.min(tag.count, 10) * 0.04}rem` }"
                @click="selectTag(tag.name)"
              >
                {{ tag.name }} ({{ tag.count }})
              </button>
            </div>
          </section>
          <section v-if="archiveByYear.length" class="articles__side-block">
            <h3 class="font-display">归档</h3>
            <div v-for="[year, months] in archiveByYear" :key="year" class="articles__archive-year">
              <p class="articles__archive-year-label font-body">{{ year }}</p>
              <div class="articles__archive-months">
                <button
                  v-for="item in months"
                  :key="`${item.year}-${item.month}`"
                  type="button"
                  class="font-body"
                  :class="{ 'is-active': activeYear === item.year && activeMonth === item.month }"
                  @click="selectArchive(item.year, item.month)"
                >
                  {{ item.month }}月 ({{ item.count }})
                </button>
              </div>
            </div>
          </section>
        </aside>

        <div class="articles__main">
      <p v-if="searchQuery || activeCategory !== '全部' || activeTag || activeYear" class="articles__count font-body">
        找到 {{ displayCount }} 篇文章
        <span v-if="searchQuery">「{{ searchQuery }}」</span>
        <span v-if="activeTag"> · 标签 {{ activeTag }}</span>
        <span v-if="activeYear"> · {{ activeYear }}年{{ activeMonth }}月</span>
      </p>

      <p v-if="loading" class="articles__loading font-body">加载中…</p>

      <div v-else-if="!filtered.length" class="articles__empty">
        <p class="font-display">未找到相关文章</p>
        <button type="button" class="font-body" @click="clearFilters">清除筛选</button>
      </div>

      <div v-else-if="viewMode === 'grid'" class="articles__grid">
        <article v-for="post in filtered" :key="post.id" class="grid-card" @click="push(paths.article(post.id))">
          <div class="grid-card__media">
            <MediaCover :src="post.img" :alt="post.title" :label="post.title" :seed="post.id" />
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
            <MediaCover :src="post.img" :alt="post.title" :label="post.title" :seed="post.id" />
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

      <nav v-if="useRemote && totalPages > 1" class="articles__pagination" aria-label="文章分页">
        <button
          type="button"
          class="font-body"
          :disabled="currentPage <= 1"
          @click="goToPage(currentPage - 1)"
        >
          上一页
        </button>
        <div class="articles__pages">
          <button
            v-for="page in pageNumbers"
            :key="page"
            type="button"
            class="font-body"
            :class="{ 'is-active': page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
        </div>
        <button
          type="button"
          class="font-body"
          :disabled="currentPage >= totalPages"
          @click="goToPage(currentPage + 1)"
        >
          下一页
        </button>
      </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.articles__layout {
  display: grid;
  gap: 2rem;

  @media (min-width: 960px) {
    grid-template-columns: 14rem 1fr;
    align-items: start;
  }
}

.articles__sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.articles__side-block {
  h3 {
    font-size: 0.75rem;
    letter-spacing: 0.16em;
    color: var(--color-secondary);
    margin: 0 0 0.75rem;
  }
}

.articles__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;

  button {
    padding: 0.25rem 0.5rem;
    border: 1px solid rgba(126, 184, 247, 0.15);
    color: var(--color-dim);
    letter-spacing: 0.04em;
    transition: all 0.2s;

    &.is-active,
    &:hover {
      color: var(--color-primary);
      border-color: rgba(245, 200, 66, 0.35);
      background: rgba(245, 200, 66, 0.08);
    }
  }
}

.articles__archive-year {
  margin-bottom: 0.75rem;
}

.articles__archive-year-label {
  margin: 0 0 0.35rem;
  font-size: 0.7rem;
  color: var(--color-muted-fg);
  letter-spacing: 0.1em;
}

.articles__archive-months {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;

  button {
    font-size: 0.65rem;
    padding: 0.2rem 0.45rem;
    border: 1px solid rgba(126, 184, 247, 0.12);
    color: var(--color-dim);

    &.is-active,
    &:hover {
      color: var(--color-secondary);
      border-color: rgba(126, 184, 247, 0.35);
    }
  }
}

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
  color: var(--color-quiet);

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
    color: var(--color-quiet);
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
  color: var(--color-quiet);
  letter-spacing: 0.05em;
  margin: 0 0 1.5rem;

  span {
    color: var(--color-secondary);
    margin-left: 0.25rem;
  }
}

.articles__loading {
  font-size: 0.75rem;
  color: var(--color-dim);
  letter-spacing: 0.1em;
  margin: 0 0 1.5rem;
}

.articles__pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(126, 184, 247, 0.1);

  > button {
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    color: var(--color-secondary);
    border: 1px solid rgba(126, 184, 247, 0.2);
    padding: 0.5rem 0.875rem;
    transition: all 0.2s;

    &:hover:not(:disabled) {
      border-color: rgba(126, 184, 247, 0.45);
      color: var(--color-fg);
    }

    &:disabled {
      opacity: 0.35;
      cursor: not-allowed;
    }
  }
}

.articles__pages {
  display: flex;
  gap: 0.35rem;

  button {
    min-width: 2rem;
    height: 2rem;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    color: var(--color-dim);
    border: 1px solid transparent;
    transition: all 0.2s;

    &:hover {
      color: var(--color-fg);
      border-color: rgba(126, 184, 247, 0.2);
    }

    &.is-active {
      color: var(--color-primary);
      border-color: rgba(245, 200, 66, 0.35);
      background: rgba(245, 200, 66, 0.08);
    }
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
    color: var(--color-quiet);
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
  background: linear-gradient(145deg, var(--color-card), var(--color-muted));
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

  :deep(.media-cover__img),
  :deep(.media-cover__ph) {
    opacity: 0.75;
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
    pointer-events: none;
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
    color: var(--color-quiet-deep);
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

  :deep(.media-cover__img),
  :deep(.media-cover__ph) {
    opacity: 0.7;
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
  color: var(--color-quiet-deep);
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
  color: var(--color-quiet-deep);
  transition: all 0.2s;
}
</style>
