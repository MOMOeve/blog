<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { photoCategories as fallbackCategories, photos as fallbackPhotos } from '../data/photos'
import {
  createPhoto,
  deletePhoto,
  fetchPhotoCategories,
  fetchPhotos,
  updatePhoto,
} from '../api/photos'
import { uploadImage } from '../api/upload'
import { ApiError } from '../api/client'
import type { Photo } from '../types'
import { useAuth } from '../composables/useAuth'
import MediaCover from '../components/MediaCover.vue'

const { isStaff, openLogin } = useAuth()

const activeCategory = ref('全部')
const lightboxPhoto = ref<Photo | null>(null)
const photos = ref<Photo[]>([])
const photoCategories = ref<string[]>(['全部'])
const useRemote = ref(false)
const loading = ref(true)

const showEditor = ref(false)
const isNewPhoto = ref(false)
const saving = ref(false)
const uploading = ref(false)
const editorError = ref('')
const imageInput = ref<HTMLInputElement | null>(null)

const editorForm = reactive({
  title: '',
  location: '',
  date: '',
  img: '',
  aspect: 'landscape' as 'landscape' | 'portrait',
  category: '自然',
  description: '',
  sort_order: 0,
  published: true,
})

const editingId = ref<number | null>(null)

const filtered = computed(() =>
  photos.value.filter((p) => activeCategory.value === '全部' || p.category === activeCategory.value),
)

async function loadPhotos() {
  loading.value = true
  try {
    const remote = await fetchPhotos({ category: activeCategory.value })
    photos.value = remote
    useRemote.value = true
  } catch {
    if (!useRemote.value) {
      photos.value = fallbackPhotos
      photoCategories.value = fallbackCategories
    }
  } finally {
    loading.value = false
  }
}

function resetEditorForm() {
  editorForm.title = ''
  editorForm.location = ''
  editorForm.date = ''
  editorForm.img = ''
  editorForm.aspect = 'landscape'
  editorForm.category = photoCategories.value.find((c) => c !== '全部') || '自然'
  editorForm.description = ''
  editorForm.sort_order = 0
  editorForm.published = true
  editingId.value = null
  editorError.value = ''
}

function openCreate() {
  if (!isStaff.value) {
    openLogin()
    return
  }
  isNewPhoto.value = true
  resetEditorForm()
  showEditor.value = true
}

function openEdit(photo: Photo) {
  if (!isStaff.value) {
    openLogin()
    return
  }
  isNewPhoto.value = false
  editingId.value = photo.id
  editorForm.title = photo.title
  editorForm.location = photo.location
  editorForm.date = photo.date
  editorForm.img = photo.img
  editorForm.aspect = photo.aspect
  editorForm.category = photo.category
  editorForm.description = photo.description
  editorForm.sort_order = photo.sort_order ?? 0
  editorForm.published = photo.published !== false
  editorError.value = ''
  showEditor.value = true
}

function closeEditor() {
  showEditor.value = false
  editorError.value = ''
}

async function savePhoto() {
  if (!isStaff.value) {
    openLogin()
    return
  }
  if (!editorForm.title.trim()) {
    editorError.value = '请填写标题'
    return
  }
  if (!editorForm.img.trim()) {
    editorError.value = '请上传或填写图片地址'
    return
  }
  if (!editorForm.category.trim()) {
    editorError.value = '请填写分类'
    return
  }

  saving.value = true
  editorError.value = ''
  const payload = {
    title: editorForm.title.trim(),
    location: editorForm.location.trim(),
    date: editorForm.date.trim(),
    img: editorForm.img.trim(),
    aspect: editorForm.aspect,
    category: editorForm.category.trim(),
    description: editorForm.description.trim(),
    sort_order: editorForm.sort_order,
    published: editorForm.published,
  }

  try {
    if (isNewPhoto.value) {
      await createPhoto(payload)
    } else if (editingId.value) {
      await updatePhoto(editingId.value, payload)
    }
    showEditor.value = false
    lightboxPhoto.value = null
    useRemote.value = true
    await loadPhotos()
  } catch (err) {
    editorError.value = err instanceof ApiError ? err.message : '保存失败'
  } finally {
    saving.value = false
  }
}

async function removePhoto(photo: Photo) {
  if (!isStaff.value) return
  if (!window.confirm(`确定删除「${photo.title}」？`)) return
  try {
    await deletePhoto(photo.id)
    if (lightboxPhoto.value?.id === photo.id) lightboxPhoto.value = null
    await loadPhotos()
  } catch (err) {
    editorError.value = err instanceof ApiError ? err.message : '删除失败'
  }
}

async function onImageSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!isStaff.value) {
    openLogin()
    return
  }
  uploading.value = true
  editorError.value = ''
  try {
    const result = await uploadImage(file)
    editorForm.img = result.path || result.url
  } catch (err) {
    editorError.value = err instanceof ApiError ? err.message : '图片上传失败'
  } finally {
    uploading.value = false
    input.value = ''
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
          <span class="page-title__sub">· 路上的风景</span>
        </h1>
        <p class="page-desc animate-fade-up-delay-2">把旅途中遇见的光，收进行囊</p>
        <button
          v-if="isStaff"
          type="button"
          class="photo__add font-body animate-fade-up-delay-2"
          @click="openCreate"
        >
          添加照片
        </button>
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
        <span class="photo__count font-body">{{ loading ? '加载中…' : `${filtered.length} 张照片` }}</span>
      </div>

      <p v-if="loading" class="photo__loading font-body">加载中…</p>
      <p v-else-if="!filtered.length" class="photo__empty font-body">暂无照片</p>
      <div v-else class="photo__masonry">
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
          <button
            v-if="isStaff"
            type="button"
            class="photo-card__edit font-body"
            aria-label="编辑"
            @click.stop="openEdit(photo)"
          >
            编辑
          </button>
        </div>
      </div>
    </div>

    <div v-if="lightboxPhoto" class="lightbox" @click="lightboxPhoto = null">
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
          <div v-if="isStaff" class="lightbox__actions">
            <button type="button" class="font-body" @click="openEdit(lightboxPhoto)">编辑</button>
            <button type="button" class="font-body is-danger" @click="removePhoto(lightboxPhoto)">
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditor" class="photo-editor" @click.self="closeEditor">
      <div class="photo-editor__panel" role="dialog" aria-modal="true" aria-labelledby="photo-editor-title">
        <div class="photo-editor__head">
          <h3 id="photo-editor-title" class="font-display">{{ isNewPhoto ? '添加照片' : '编辑照片' }}</h3>
          <button type="button" class="photo-editor__close" aria-label="关闭" @click="closeEditor">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <line x1="5" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="1.5" />
              <line x1="19" y1="5" x2="5" y2="19" stroke="currentColor" stroke-width="1.5" />
            </svg>
          </button>
        </div>

        <form class="photo-editor__form" @submit.prevent="savePhoto">
          <label class="photo-editor__field photo-editor__field--full">
            <span class="font-body">标题 <em>*</em></span>
            <input v-model="editorForm.title" class="font-body" autocomplete="off" />
          </label>

          <div class="photo-editor__row">
            <label class="photo-editor__field">
              <span class="font-body">地点</span>
              <input v-model="editorForm.location" class="font-body" autocomplete="off" />
            </label>
            <label class="photo-editor__field">
              <span class="font-body">拍摄时间</span>
              <input v-model="editorForm.date" class="font-body" placeholder="2026年5月" autocomplete="off" />
            </label>
          </div>

          <div class="photo-editor__row">
            <label class="photo-editor__field">
              <span class="font-body">分类 <em>*</em></span>
              <input v-model="editorForm.category" list="photo-cat-list" class="font-body" autocomplete="off" />
              <datalist id="photo-cat-list">
                <option v-for="c in photoCategories.filter((x) => x !== '全部')" :key="c" :value="c" />
              </datalist>
            </label>
            <label class="photo-editor__field">
              <span class="font-body">比例</span>
              <select v-model="editorForm.aspect" class="font-body">
                <option value="landscape">横图</option>
                <option value="portrait">竖图</option>
              </select>
            </label>
          </div>

          <label class="photo-editor__field photo-editor__field--full">
            <span class="font-body">描述</span>
            <textarea v-model="editorForm.description" class="font-body" rows="3" />
          </label>

          <div class="photo-editor__row photo-editor__row--meta">
            <label class="photo-editor__field">
              <span class="font-body">排序</span>
              <span class="photo-editor__hint font-body">越小越靠前</span>
              <input v-model.number="editorForm.sort_order" type="number" min="0" class="font-body" />
            </label>
            <div class="photo-editor__field photo-editor__field--check">
              <span class="font-body">状态</span>
              <label class="photo-editor__check font-body">
                <input v-model="editorForm.published" type="checkbox" />
                <span class="photo-editor__check-box" aria-hidden="true" />
                已发布
              </label>
            </div>
          </div>

          <label class="photo-editor__field photo-editor__field--full">
            <span class="font-body">图片 <em>*</em></span>
            <div class="photo-editor__img">
              <input v-model="editorForm.img" class="font-body" placeholder="上传后自动填入" />
              <input
                ref="imageInput"
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif,image/svg+xml"
                hidden
                @change="onImageSelected"
              />
              <button
                type="button"
                class="font-body"
                :disabled="uploading"
                @click="imageInput?.click()"
              >
                {{ uploading ? '上传中…' : '上传' }}
              </button>
            </div>
          </label>

          <p v-if="editorError" class="photo-editor__error font-body">{{ editorError }}</p>

          <div class="photo-editor__actions">
            <button type="button" class="font-body" @click="closeEditor">取消</button>
            <button type="submit" class="font-body is-primary" :disabled="saving">
              {{ saving ? '保存中…' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.photo__add {
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
  color: var(--color-quiet-deep);
  letter-spacing: 0.05em;
}

.photo__loading,
.photo__empty {
  margin: 2rem 0 4rem;
  font-size: 0.875rem;
  color: var(--color-dim);
  letter-spacing: 0.08em;
  text-align: center;
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
    .photo-card__badge,
    .photo-card__edit {
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
    color: var(--color-quiet);
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

.photo-card__edit {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  z-index: 10;
  opacity: 0;
  font-size: 0.6rem;
  letter-spacing: 0.1em;
  padding: 0.2rem 0.55rem;
  background: rgba(18, 26, 46, 0.85);
  border: 1px solid rgba(245, 200, 66, 0.35);
  color: var(--color-primary);
  transition: opacity 0.3s;
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
  color: var(--color-quiet-deep);
  letter-spacing: 0.05em;
}

.lightbox__actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.25rem;

  button {
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    padding: 0.4rem 0.75rem;
    border: 1px solid rgba(126, 184, 247, 0.25);
    color: var(--color-secondary);

    &:hover {
      color: var(--color-fg);
    }

    &.is-danger {
      border-color: rgba(224, 112, 112, 0.35);
      color: #e07070;
    }
  }
}

.photo-editor {
  position: fixed;
  inset: 0;
  z-index: 110;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  background: rgba(6, 10, 24, 0.82);
  backdrop-filter: blur(6px);
}

.photo-editor__panel {
  width: 100%;
  max-width: 36rem;
  max-height: min(90vh, 720px);
  overflow: auto;
  padding: 1.5rem 1.5rem 1.25rem;
  border: 1px solid rgba(126, 184, 247, 0.18);
  background: var(--color-modal-bg, var(--color-nav-mobile-bg));
  box-shadow: var(--shadow-modal, 0 24px 48px rgba(0, 0, 0, 0.35));
}

.photo-editor__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(126, 184, 247, 0.1);

  h3 {
    margin: 0;
    font-size: 1.05rem;
    color: var(--color-fg);
    letter-spacing: 0.1em;
  }
}

.photo-editor__close {
  flex-shrink: 0;
  color: var(--color-dim);
  transition: color 0.2s;

  &:hover {
    color: var(--color-fg);
  }
}

.photo-editor__form {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.photo-editor__field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  min-width: 0;

  > span {
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    color: var(--color-dim);

    em {
      font-style: normal;
      color: var(--color-primary);
    }
  }

  input,
  textarea,
  select {
    width: 100%;
    background: var(--color-input-bg);
    border: 1px solid var(--color-border);
    color: var(--color-fg);
    font-size: 0.875rem;
    padding: 0.7rem 0.85rem;
    outline: none;
    transition: border-color 0.2s;

    &::placeholder {
      color: var(--color-faint);
    }

    &:focus {
      border-color: var(--color-border-focus);
    }
  }

  textarea {
    resize: vertical;
    min-height: 5.5rem;
    line-height: 1.6;
  }

  select {
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12' fill='none'%3E%3Cpath d='M2.5 4.5L6 8L9.5 4.5' stroke='%238eb8f7' stroke-width='1.2' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
    padding-right: 2rem;
  }
}

.photo-editor__hint {
  margin: -0.2rem 0 0;
  font-size: 0.62rem;
  letter-spacing: 0.06em;
  color: var(--color-faint);
  font-weight: 300;
}

.photo-editor__row {
  display: grid;
  gap: 1rem;
  margin-bottom: 1rem;

  @media (min-width: 520px) {
    grid-template-columns: 1fr 1fr;
  }
}

.photo-editor__field--full {
  margin-bottom: 1rem;
}

.photo-editor__row--meta {
  align-items: end;
}

.photo-editor__field--check {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.photo-editor__check {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 2.65rem;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--color-border);
  background: var(--color-input-bg);
  cursor: pointer;
  user-select: none;
  font-size: 0.875rem;
  color: var(--color-soft);
  letter-spacing: 0.06em;
  transition: border-color 0.2s;

  input {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
    pointer-events: none;
  }

  &:has(input:checked) {
    border-color: rgba(126, 184, 247, 0.45);
    color: var(--color-fg);
  }

  &:has(input:focus-visible) {
    border-color: var(--color-border-focus);
  }
}

.photo-editor__check-box {
  width: 0.95rem;
  height: 0.95rem;
  flex-shrink: 0;
  border: 1px solid rgba(126, 184, 247, 0.45);
  background: transparent;
  position: relative;
  transition: background 0.2s, border-color 0.2s;

  .photo-editor__check:has(input:checked) & {
    background: rgba(126, 184, 247, 0.85);
    border-color: rgba(126, 184, 247, 0.85);

    &::after {
      content: '';
      position: absolute;
      left: 0.22rem;
      top: 0.08rem;
      width: 0.28rem;
      height: 0.48rem;
      border: solid #0a1020;
      border-width: 0 1.5px 1.5px 0;
      transform: rotate(45deg);
    }
  }
}

.photo-editor__img {
  display: flex;
  gap: 0.5rem;
  align-items: stretch;

  input {
    flex: 1;
    min-width: 0;
  }

  button {
    flex-shrink: 0;
    min-width: 4.5rem;
    padding: 0 1rem;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    border: 1px solid rgba(142, 196, 250, 0.35);
    color: var(--color-secondary);
    background: rgba(142, 196, 250, 0.06);
    transition: all 0.2s;

    &:hover:not(:disabled) {
      background: rgba(142, 196, 250, 0.12);
      border-color: rgba(142, 196, 250, 0.55);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

.photo-editor__error {
  margin: 0 0 1rem;
  font-size: 0.78rem;
  color: #e07070;
  letter-spacing: 0.04em;
}

.photo-editor__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.25rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(126, 184, 247, 0.08);

  button {
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    padding: 0.6rem 1.1rem;
    border: 1px solid var(--color-border);
    color: var(--color-muted-fg);
    transition: all 0.2s;

    &:hover:not(:disabled) {
      color: var(--color-fg);
    }

    &.is-primary {
      border-color: rgba(245, 200, 66, 0.4);
      color: var(--color-primary);
      background: rgba(245, 200, 66, 0.12);

      &:hover:not(:disabled) {
        background: rgba(245, 200, 66, 0.2);
      }
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}
</style>
