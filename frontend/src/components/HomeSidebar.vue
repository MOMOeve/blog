<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchSiteAuthor, type SiteAuthor } from '../api/auth'
import { posts as fallbackPosts } from '../data/posts'
import type { Post } from '../types'
import { useRouter } from '../router'
import MediaCover from './MediaCover.vue'

const props = withDefaults(
  defineProps<{ posts?: Post[] }>(),
  { posts: undefined },
)

const { push, paths } = useRouter()
const author = ref<SiteAuthor>({ displayName: '', bio: '', avatar: '' })
const recent = computed(() => (props.posts ?? fallbackPosts).slice(0, 3))
const tags = computed(() => {
  const source = props.posts ?? []
  return Array.from(new Set(source.flatMap((p) => p.tags))).slice(0, 12)
})

onMounted(async () => {
  try {
    author.value = await fetchSiteAuthor()
  } catch {
    /* keep empty */
  }
})
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__profile">
      <div class="sidebar__avatar">
        <MediaCover
          :src="author.avatar"
          :alt="author.displayName || '作者头像'"
          :label="author.displayName || '作者'"
          seed="avatar"
        />
      </div>
      <h4 class="font-display">{{ author.displayName || '作者' }}</h4>
      <div class="divider-light" />
      <p v-if="author.bio" class="sidebar__bio font-body">{{ author.bio }}</p>
      <p v-else class="sidebar__bio font-body">简介尚未填写</p>
      <button type="button" class="sidebar__about font-body" @click="push(paths.about())">了解更多</button>
    </div>

    <div v-if="recent.length">
      <h4 class="sidebar__heading font-display">
        <span class="bar" />
        最近发布
        <span class="line" />
      </h4>
      <ul class="sidebar__recent">
        <li v-for="p in recent" :key="p.id" class="sidebar__recent-item">
          <div class="thumb">
            <MediaCover :src="p.img" :alt="p.title" :label="p.title" :seed="p.id" />
          </div>
          <div>
            <p class="font-display">{{ p.title }}</p>
            <span class="font-body">{{ p.date }}</span>
          </div>
        </li>
      </ul>
    </div>

    <div v-if="tags.length">
      <h4 class="sidebar__heading font-display">
        <span class="bar" />
        标签云
        <span class="line" />
      </h4>
      <div class="sidebar__tags">
        <button v-for="tag in tags" :key="tag" type="button" class="tag-pill"># {{ tag }}</button>
      </div>
    </div>
  </aside>
</template>

<style scoped lang="less">
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sidebar__profile {
  padding: 1.5rem;
  border: 1px solid var(--color-border);
  background: linear-gradient(145deg, var(--color-card), var(--color-muted));
  box-shadow: var(--shadow-card);
  text-align: center;

  h4 {
    font-size: 0.875rem;
    color: var(--color-fg);
    letter-spacing: 0.1em;
    margin: 0 0 0.25rem;
  }

  > .font-body {
    font-size: 0.75rem;
    color: var(--color-dim);
    letter-spacing: 0.05em;
    margin: 0 0 1.25rem;
  }

  .divider-light {
    margin-bottom: 1.25rem;
  }
}

.sidebar__avatar {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 1rem;
  ring: 1px;
  box-shadow: 0 0 0 1px rgba(245, 200, 66, 0.3);
  background: var(--color-card);

  :deep(.media-cover__img),
  :deep(.media-cover__ph) {
    opacity: 0.85;
  }
}

.sidebar__bio {
  font-size: 0.75rem;
  color: #5a6e88;
  line-height: 1.8;
  font-weight: 300;
  margin: 0;
}

.sidebar__about {
  margin-top: 1.25rem;
  width: 100%;
  text-align: center;
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  color: var(--color-secondary);
  border: 1px solid rgba(126, 184, 247, 0.15);
  padding: 0.5rem;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(126, 184, 247, 0.35);
    color: var(--color-fg);
  }
}

.sidebar__heading {
  font-size: 0.75rem;
  letter-spacing: 0.25em;
  color: var(--color-secondary);
  margin: 0 0 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;

  .bar {
    width: 1rem;
    height: 1px;
    background: var(--color-secondary);
    opacity: 0.5;
  }

  .line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, rgba(126, 184, 247, 0.2), transparent);
  }
}

.sidebar__recent {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sidebar__recent-item {
  display: flex;
  gap: 0.75rem;
  cursor: pointer;

  .thumb {
    width: 3.5rem;
    height: 3.5rem;
    flex-shrink: 0;
    overflow: hidden;
    background: var(--color-card);

    :deep(.media-cover__img),
    :deep(.media-cover__ph) {
      opacity: 0.75;
      transition: opacity 0.2s;
    }

    :deep(.media-cover__ph) {
      min-height: 0;
    }

    :deep(.media-cover__label) {
      font-size: 0.55rem;
      letter-spacing: 0.06em;
    }
  }

  p {
    margin: 0;
    font-size: 0.75rem;
    line-height: 1.4;
    color: var(--color-soft);
    letter-spacing: 0.03em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: color 0.2s;
  }

  span {
    display: block;
    font-size: 0.65rem;
    color: var(--color-quiet);
    margin-top: 0.25rem;
    letter-spacing: 0.05em;
  }

  &:hover {
    img {
      opacity: 0.9;
    }

    p {
      color: var(--color-primary);
    }
  }
}

.sidebar__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.sidebar__quote {
  margin: 0;
  padding: 1.25rem;
  border-left: 2px solid rgba(245, 200, 66, 0.4);
  background: rgba(245, 200, 66, 0.04);

  p {
    margin: 0;
    font-style: italic;
    font-size: 0.875rem;
    color: var(--color-soft);
    line-height: 1.6;
  }

  cite {
    display: block;
    font-style: normal;
    font-size: 0.65rem;
    color: var(--color-dim);
    margin-top: 0.75rem;
    letter-spacing: 0.05em;
  }
}
</style>
