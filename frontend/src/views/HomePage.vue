<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { categories as fallbackCategories, posts as fallbackPosts } from '../data/posts'
import { fetchPosts } from '../api/posts'
import type { Post } from '../types'
import HeroSection from '../components/HeroSection.vue'
import PostCard from '../components/PostCard.vue'
import HomeSidebar from '../components/HomeSidebar.vue'
import { useRouter } from '../router'

const { push, paths } = useRouter()

const activeCategory = ref('全部')
const posts = ref<Post[]>(fallbackPosts)
const categories = ref<string[]>(fallbackCategories)
const loading = ref(false)

const featuredPost = computed(() => posts.value.find((p) => p.featured) ?? posts.value[0])
const gridPosts = computed(() =>
  posts.value
    .filter((p) => p.id !== featuredPost.value?.id)
    .filter((p) => activeCategory.value === '全部' || p.tags.includes(activeCategory.value)),
)

onMounted(async () => {
  loading.value = true
  try {
    const remote = await fetchPosts({ ordering: '-published_at' })
    if (remote.length) {
      posts.value = remote
      const names = Array.from(new Set(remote.map((p) => p.category)))
      categories.value = ['全部', ...names]
    }
  } catch {
    /* 后端未启动时回退本地 mock */
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <HeroSection @read-more="push(paths.articles())" />

    <main class="home">
      <div class="home__featured-head">
        <p class="font-body">✦ &nbsp; FEATURED</p>
        <h2 class="font-display">精选文章</h2>
      </div>

      <div class="home__featured">
        <PostCard v-if="featuredPost" :post="featuredPost" featured @select="push(paths.article($event.id))" />
      </div>

      <div class="divider-light home__divider" />

      <div class="home__layout">
        <div>
          <div class="home__toolbar">
            <h2 class="font-display">近期文章</h2>
            <div class="home__filters">
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
          </div>

          <div v-if="gridPosts.length" class="home__grid">
            <PostCard v-for="post in gridPosts" :key="post.id" :post="post" @select="push(paths.article($event.id))" />
          </div>
          <div v-else class="home__empty">
            <p class="font-body">暂无该分类文章</p>
            <button type="button" class="font-body" @click="activeCategory = '全部'">清除筛选</button>
          </div>

          <div v-if="gridPosts.length" class="home__more">
            <button type="button" class="font-body" @click="push(paths.articles())">
              查看全部文章
              <svg width="14" height="8" viewBox="0 0 14 8" fill="none">
                <line x1="0" y1="4" x2="11" y2="4" stroke="currentColor" stroke-width="1.2" />
                <polyline points="7.5,1 11,4 7.5,7" fill="none" stroke="currentColor" stroke-width="1.2" />
              </svg>
            </button>
          </div>
        </div>

        <HomeSidebar />
      </div>
    </main>
  </div>
</template>

<style scoped lang="less">
.home {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 4rem 1.5rem;
}

.home__featured-head {
  margin-bottom: 2.5rem;

  p {
    font-size: 0.75rem;
    letter-spacing: 0.3em;
    color: var(--color-secondary);
    margin: 0 0 0.5rem;
    opacity: 0.7;
  }

  h2 {
    font-size: 1.125rem;
    color: var(--color-fg);
    letter-spacing: 0.08em;
    margin: 0;
  }
}

.home__featured {
  margin-bottom: 4rem;
}

.home__divider {
  margin-bottom: 3rem;
}

.home__layout {
  display: grid;
  gap: 3rem;

  @media (min-width: 1024px) {
    grid-template-columns: 1fr 280px;
  }
}

.home__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;

  h2 {
    font-size: 1rem;
    color: var(--color-fg);
    letter-spacing: 0.1em;
    margin: 0;
  }
}

.home__filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.home__grid {
  display: grid;
  gap: 1.5rem;

  @media (min-width: 640px) {
    grid-template-columns: 1fr 1fr;
  }
}

.home__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
  text-align: center;

  p {
    font-size: 0.875rem;
    color: #3d5070;
    letter-spacing: 0.05em;
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

.home__more {
  margin-top: 2.5rem;
  display: flex;
  justify-content: center;

  button {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    color: var(--color-muted-fg);
    border: 1px solid rgba(126, 184, 247, 0.15);
    padding: 0.75rem 2rem;
    transition: all 0.3s;

    svg {
      transition: transform 0.3s;
    }

    &:hover {
      border-color: rgba(126, 184, 247, 0.35);
      color: var(--color-fg);

      svg {
        transform: translateX(4px);
      }
    }
  }
}
</style>
