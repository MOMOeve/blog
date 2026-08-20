<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { photoCategories as fallbackCategories, photos as fallbackPhotos } from '../data/photos'
import { fetchPhotoCategories, fetchPhotos } from '../api/photos'
import type { Photo } from '../types'
import MediaCover from '../components/MediaCover.vue'

const activeCategory = ref('全部')
const lightboxPhoto = ref<Photo | null>(null)
const photos = ref<Photo[]>(fallbackPhotos)
const photoCategories = ref<string[]>(fallbackCategories)
const useRemote = ref(false)

const filtered = computed(() =>
  photos.value.filter((p) => activeCategory.value === '全部' || p.category === activeCategory.value),
)

async function loadPhotos() {
  try {
    const remote = await fetchPhotos({ category: activeCategory.value })
    if (remote.length || useRemote.value) {
      photos.value = remote
      useRemote.value = true
    }
  } catch {
    /* keep fallback */
  }
}

onMounted(async () => {
  try {
    const names = await fetchPhotoCategories()
    if (names.length) photoCategories.value = names
  } catch {
    /* keep fallback */
  }
  await loadPhotos()
})

watch(activeCategory, () => {
  if (useRemote.value) void loadPhotos()
})
</script>

<template>
  <div class="page-shell">
    <div class="page-header">
      <div class="page-header__glow" />
      <div class="page-header__line" />
      <div class="page-header__inner">
        <p class="page-eyebrow animate-fade-up">✦ &nbsp; PHOTOGRAPHY</p>
        <h1 class="page-title animate-fade-up-delay-1">
          摄影
          <span class="page-title__sub">· 光的记忆</span>
        </h1>
        <p class="page-desc animate-fade-up-delay-2">用镜头捕捉那些一旦错过便永不复返的光</p>
      </div>
    </div>

    <div class="container">
      <div class="photo__filters">
        <button
          v-for="cat in photoCategories"
          :key="cat"
          type="button"
          class="filter-btn"
          :class="{ 'is-active': activeCategory === cat }"
          @click="activeCategory = cat"
        >
          {{ cat }}
        </button>
        <span class="photo__count font-body">{{ filtered.length }} 张照片</span>
      </div>

      <div class="photo__masonry">
        <div
          v-for="photo in filtered"
          :key="photo.id"
          class="photo-card"
          @click="lightboxPhoto = photo"
        >
          <div class="photo-card__media" :class="photo.aspect">
            <MediaCover :src="photo.img" :alt="photo.title" :label="photo.title" :seed="photo.id" />
          </div>
          <div class="photo-card__overlay">
            <h3 class="font-display">{{ photo.title }}</h3>
            <div class="photo-card__loc font-body">
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                <circle cx="5" cy="4" r="2.5" stroke="currentColor" stroke-width="1" />
                <path
                  d="M5 9 C5 9 2 6 2 4 C2 2.3 3.3 1 5 1 C6.7 1 8 2.3 8 4 C8 6 5 9 5 9Z"
                  stroke="currentColor"
                  stroke-width="1"
                  fill="none"
                />
              </svg>
              <span>{{ photo.location }}</span>
              <span>· {{ photo.date }}</span>
            </div>
          </div>
          <span class="photo-card__badge font-body">{{ photo.category }}</span>
        </div>
      </div>
    </div>

    <div
      v-if="lightboxPhoto"
      class="lightbox"
      @click="lightboxPhoto = null"
    >
      <button type="button" class="lightbox__close" aria-label="关闭" @click="lightboxPhoto = null">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <line x1="5" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="1.5" />
          <line x1="19" y1="5" x2="5" y2="19" stroke="currentColor" stroke-width="1.5" />
        </svg>
      </button>

      <div class="lightbox__panel" @click.stop>
        <div class="lightbox__image">
          <MediaCover
            :src="lightboxPhoto.img"
            :alt="lightboxPhoto.title"
            :label="lightboxPhoto.title"
            :seed="lightboxPhoto.id"
          />
        </div>
        <div class="lightbox__info">
          <span class="font-body">{{ lightboxPhoto.category }}</span>
          <h2 class="font-display">{{ lightboxPhoto.title }}</h2>
          <div class="lightbox__loc font-body">
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
              <circle cx="5" cy="4" r="2.5" stroke="currentColor" stroke-width="1" />
              <path
                d="M5 9 C5 9 2 6 2 4 C2 2.3 3.3 1 5 1 C6.7 1 8 2.3 8 4 C8 6 5 9 5 9Z"
                stroke="currentColor"
                stroke-width="1"
                fill="none"
              />
            </svg>
            <span>{{ lightboxPhoto.location }}</span>
          </div>
          <div class="lightbox__line" />
          <p class="font-serif">"{{ lightboxPhoto.description }}"</p>
          <span class="lightbox__date font-body">{{ lightboxPhoto.date }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.photo__filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2.5rem;
}

.photo__count {
  margin-left: auto;
  font-size: 0.75rem;
  color: #2f3f56;
  letter-spacing: 0.05em;
}

.photo__masonry {
  columns: 1;
  column-gap: 1rem;

  @media (min-width: 640px) {
    columns: 2;
  }

  @media (min-width: 1024px) {
    columns: 3;
  }
}

.photo-card {
  position: relative;
  overflow: hidden;
  break-inside: avoid;
  margin-bottom: 1rem;
  cursor: pointer;
  border: 1px solid rgba(126, 184, 247, 0.08);
  transition: border-color 0.5s;

  &:hover {
    border-color: rgba(126, 184, 247, 0.25);

    :deep(.media-cover__img),
    :deep(.media-cover__ph) {
      opacity: 1;
      transform: scale(1.03);
    }

    .photo-card__overlay,
    .photo-card__badge {
      opacity: 1;
    }
  }
}

.photo-card__media {
  background: var(--color-card);
  aspect-ratio: 3 / 2;

  &.portrait {
    aspect-ratio: 2 / 3;
  }

  :deep(.media-cover__img),
  :deep(.media-cover__ph) {
    opacity: 0.92;
    filter: saturate(1.05) brightness(1);
    transition: all 0.7s;
  }
}

.photo-card__overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1.25rem;
  opacity: 0;
  transition: opacity 0.4s;
  background: linear-gradient(transparent 30%, rgba(18, 26, 46, 0.88));

  h3 {
    font-size: 0.875rem;
    color: var(--color-fg);
    letter-spacing: 0.06em;
    margin: 0 0 0.25rem;
  }
}

.photo-card__loc {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.65rem;
  color: var(--color-muted-fg);
  letter-spacing: 0.05em;

  svg {
    color: var(--color-secondary);
    flex-shrink: 0;
  }

  span:last-child {
    color: #3d5070;
  }
}

.photo-card__badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  z-index: 10;
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 0.6rem;
  letter-spacing: 0.1em;
  padding: 0.125rem 0.5rem;
  background: rgba(18, 26, 46, 0.8);
  border: 1px solid rgba(126, 184, 247, 0.2);
  color: var(--color-secondary);
}

.lightbox {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(12, 18, 34, 0.88);

  @media (min-width: 768px) {
    padding: 2.5rem;
  }
}

.lightbox__close {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  color: var(--color-dim);
  z-index: 10;
  transition: color 0.2s;

  &:hover {
    color: var(--color-fg);
  }
}

.lightbox__panel {
  max-width: 56rem;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;

  @media (min-width: 768px) {
    flex-direction: row;
  }
}

.lightbox__image {
  flex: 1;
  max-height: 75vh;
  min-height: 16rem;
  overflow: hidden;
  border: 1px solid rgba(126, 184, 247, 0.12);

  :deep(.media-cover__img) {
    object-fit: contain;
    filter: saturate(1.1) brightness(0.95);
  }

  :deep(.media-cover__ph) {
    min-height: 16rem;
  }
}

.lightbox__info {
  width: 100%;
  flex-shrink: 0;

  @media (min-width: 768px) {
    width: 14rem;
  }

  > .font-body:first-child {
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    padding: 0.25rem 0.625rem;
    border: 1px solid rgba(126, 184, 247, 0.2);
    color: var(--color-secondary);
    display: inline-block;
    margin-bottom: 0.25rem;
  }

  h2 {
    font-size: 1.25rem;
    color: var(--color-fg);
    letter-spacing: 0.06em;
    margin: 0.25rem 0 0.5rem;
  }

  .font-serif {
    font-style: italic;
    font-size: 0.875rem;
    color: var(--color-muted-fg);
    line-height: 1.6;
    margin: 0 0 1.25rem;
  }
}

.lightbox__loc {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-bottom: 1.25rem;
  font-size: 0.75rem;
  color: var(--color-dim);
  letter-spacing: 0.05em;

  svg {
    color: var(--color-secondary);
  }
}

.lightbox__line {
  height: 1px;
  margin-bottom: 1.25rem;
  background: linear-gradient(90deg, rgba(126, 184, 247, 0.2), transparent);
}

.lightbox__date {
  font-size: 0.65rem;
  color: #2f3f56;
  letter-spacing: 0.05em;
}
</style>
