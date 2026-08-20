<script setup lang="ts">
import type { Post } from '../types'
import MediaCover from './MediaCover.vue'

withDefaults(
  defineProps<{
    post: Post
    featured?: boolean
  }>(),
  { featured: false },
)

const emit = defineEmits<{
  select: [post: Post]
}>()

function truncate(text: string, len: number) {
  return text.length > len ? `${text.slice(0, len)}…` : text
}
</script>

<template>
  <article v-if="featured" class="featured card-hover" @click="emit('select', post)">
    <div class="featured__grid">
      <div class="img-overlay featured__media">
        <MediaCover :src="post.img" :alt="post.title" :label="post.title" :seed="post.id" />
      </div>
      <div class="featured__body">
        <div class="featured__meta">
          <span class="tag-pill">{{ post.category }}</span>
          <span class="font-body">精选</span>
        </div>
        <h2 class="font-display">{{ post.title }}</h2>
        <p class="featured__en font-serif">{{ post.titleEn }}</p>
        <p class="featured__excerpt font-body">{{ post.excerpt }}</p>
        <div class="featured__footer">
          <div class="featured__date font-body">
            <span>{{ post.date }}</span>
            <span class="dot" />
            <span>{{ post.readTime }}</span>
          </div>
          <button type="button" class="featured__more font-body">
            继续阅读
            <svg width="14" height="8" viewBox="0 0 14 8" fill="none">
              <line x1="0" y1="4" x2="11" y2="4" stroke="currentColor" stroke-width="1.2" />
              <polyline points="7.5,1 11,4 7.5,7" fill="none" stroke="currentColor" stroke-width="1.2" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </article>

  <article v-else class="card card-hover" @click="emit('select', post)">
    <div class="img-overlay card__media">
      <MediaCover :src="post.img" :alt="post.title" :label="post.title" :seed="post.id" />
      <div class="card__badge">
        <span class="tag-pill">{{ post.category }}</span>
      </div>
    </div>
    <div class="card__body">
      <h3 class="font-display">{{ post.title }}</h3>
      <p class="card__en font-serif">{{ post.titleEn }}</p>
      <p class="card__excerpt font-body">{{ truncate(post.excerpt, 80) }}</p>
      <div class="card__footer font-body">
        <span>{{ post.date }}</span>
        <span>{{ post.readTime }}</span>
      </div>
    </div>
  </article>
</template>

<style scoped lang="less">
.featured {
  cursor: pointer;
  border: 1px solid rgba(126, 184, 247, 0.08);
  background: linear-gradient(135deg, rgba(11, 16, 40, 0.9), rgba(8, 12, 28, 0.95));
  transition: border-color 0.5s;

  &:hover {
    border-color: rgba(126, 184, 247, 0.2);

    h2 {
      color: var(--color-primary);
    }

    img,
    :deep(.media-cover__img),
    :deep(.media-cover__ph) {
      opacity: 0.95;
      transform: scale(1.02);
    }
  }
}

.featured__grid {
  display: grid;

  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
  }
}

.featured__media {
  height: 18rem;
  background: var(--color-card);

  @media (min-width: 768px) {
    height: auto;
    min-height: 16rem;
  }

  :deep(.media-cover__img),
  :deep(.media-cover__ph) {
    opacity: 0.88;
    filter: saturate(1.1) brightness(0.95);
    transition: all 0.7s;
  }
}

.featured__body {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;

  @media (min-width: 768px) {
    padding: 3rem;
  }

  h2 {
    font-size: clamp(1.25rem, 2vw, 1.5rem);
    line-height: 1.4;
    color: var(--color-fg);
    letter-spacing: 0.04em;
    margin: 0 0 0.75rem;
    transition: color 0.3s;
  }
}

.featured__meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;

  .font-body {
    font-size: 0.75rem;
    color: var(--color-dim);
    letter-spacing: 0.1em;
  }
}

.featured__en {
  font-style: italic;
  font-size: 0.875rem;
  color: var(--color-dim);
  margin: 0 0 1.25rem;
}

.featured__excerpt {
  font-size: 0.875rem;
  color: var(--color-muted-fg);
  line-height: 1.8;
  font-weight: 300;
  margin: 0 0 1.75rem;
}

.featured__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.featured__date {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--color-dim);
  letter-spacing: 0.05em;
}

.dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--color-faint);
}

.featured__more {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-secondary);
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  transition: color 0.2s;

  svg {
    transition: transform 0.2s;
  }

  &:hover {
    color: var(--color-primary);

    svg {
      transform: translateX(4px);
    }
  }
}

.card {
  cursor: pointer;
  border: 1px solid rgba(126, 184, 247, 0.08);
  background: linear-gradient(145deg, rgba(11, 16, 40, 0.85), rgba(8, 12, 28, 0.92));
  display: flex;
  flex-direction: column;
  transition: border-color 0.5s;

  &:hover {
    border-color: rgba(126, 184, 247, 0.18);

    h3 {
      color: var(--color-primary);
    }

    :deep(.media-cover__img),
    :deep(.media-cover__ph) {
      opacity: 0.9;
      transform: scale(1.03);
    }
  }
}

.card__media {
  height: 12rem;
  background: var(--color-card);
  flex-shrink: 0;

  :deep(.media-cover__img),
  :deep(.media-cover__ph) {
    opacity: 0.85;
    filter: saturate(1.1) brightness(0.92);
    transition: all 0.7s;
  }
}

.card__badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  z-index: 10;
}

.card__body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  flex: 1;

  h3 {
    font-size: 1rem;
    line-height: 1.4;
    color: var(--color-fg);
    letter-spacing: 0.04em;
    margin: 0 0 0.5rem;
    transition: color 0.3s;
  }
}

.card__en {
  font-style: italic;
  font-size: 0.75rem;
  color: #3d5070;
  margin: 0 0 1rem;
}

.card__excerpt {
  font-size: 0.75rem;
  color: #5a6e88;
  line-height: 1.8;
  font-weight: 300;
  flex: 1;
  margin: 0 0 1.25rem;
}

.card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid rgba(126, 184, 247, 0.07);
  font-size: 0.68rem;
  color: #3d5070;
  letter-spacing: 0.05em;
}
</style>
