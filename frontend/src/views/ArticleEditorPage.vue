<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { createPost, fetchCategoryNames, fetchPost, updatePost } from '../api/posts'
import { uploadImage } from '../api/upload'
import { useAuth } from '../composables/useAuth'
import { renderMarkdown } from '../utils/markdown'
import { useRouter } from '../router'

const { isStaff, openLogin } = useAuth()
const { route, push, paths } = useRouter()

const title = ref('')
const titleEn = ref('')
const category = ref('随笔')
const tagsInput = ref('')
const excerpt = ref('')
const body = ref('')
const img = ref('')
const readTime = ref('5 分钟')
const featured = ref(false)
const published = ref(false)

const categories = ref<string[]>([])
const loading = ref(false)
const saving = ref(false)
const uploadingCover = ref(false)
const uploadingBody = ref(false)
const error = ref('')
const showPreview = ref(true)
const coverInput = ref<HTMLInputElement | null>(null)
const bodyImageInput = ref<HTMLInputElement | null>(null)

const editPostId = computed(() =>
  route.value.name === 'article-edit' ? Number(route.value.params.id) : null,
)
const isEdit = computed(() => editPostId.value !== null && !Number.isNaN(editPostId.value!))
const pageTitle = computed(() => (isEdit.value ? '编辑文章' : '写文章'))
const previewHtml = computed(() => renderMarkdown(body.value))

async function loadCategories() {
  try {
    const names = await fetchCategoryNames()
    categories.value = names.filter((n) => n !== '全部')
    if (!category.value && categories.value[0]) category.value = categories.value[0]
  } catch {
    categories.value = ['随笔', '技术', '旅行']
  }
}

async function loadPost() {
  if (!isEdit.value || !editPostId.value) return
  loading.value = true
  error.value = ''
  try {
    const post = await fetchPost(editPostId.value)
    title.value = post.title
    titleEn.value = post.titleEn || ''
    category.value = post.category
    tagsInput.value = (post.tags || []).join(', ')
    excerpt.value = post.excerpt
    body.value = post.body || ''
    img.value = post.img || ''
    readTime.value = post.readTime || '5 分钟'
    featured.value = Boolean(post.featured)
    published.value = post.published !== false
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

function parseTags(): string[] {
  return tagsInput.value
    .split(/[,，]/)
    .map((t) => t.trim())
    .filter(Boolean)
}

async function save(publishNow: boolean) {
  if (!isStaff.value) {
    openLogin()
    error.value = '需要工作人员账号才能发布'
    return
  }
  if (!title.value.trim()) {
    error.value = '请填写标题'
    return
  }
  if (!excerpt.value.trim()) {
    error.value = '请填写摘要'
    return
  }
  if (!category.value.trim()) {
    error.value = '请填写分类'
    return
  }

  saving.value = true
  error.value = ''
  published.value = publishNow
  const payload = {
    title: title.value.trim(),
    titleEn: titleEn.value.trim(),
    category: category.value.trim(),
    tags: parseTags(),
    excerpt: excerpt.value.trim(),
    body: body.value,
    img: img.value.trim(),
    readTime: readTime.value.trim() || '5 分钟',
    featured: featured.value,
    published: publishNow,
  }

  try {
    const saved = isEdit.value && editPostId.value
      ? await updatePost(editPostId.value, payload)
      : await createPost(payload)
    if (saved.published !== false) {
      push(paths.article(saved.id))
    } else {
      push(paths.drafts())
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : '保存失败'
  } finally {
    saving.value = false
  }
}

function insertSnippet(snippet: string) {
  body.value = body.value ? `${body.value}\n\n${snippet}` : snippet
}

function saveDraft() {
  void save(false)
}

function savePublished() {
  void save(true)
}

function cancelEdit() {
  push(paths.drafts())
}

async function onCoverSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!isStaff.value) {
    openLogin()
    return
  }
  uploadingCover.value = true
  error.value = ''
  try {
    const result = await uploadImage(file)
    img.value = result.path || result.url
  } catch (e) {
    error.value = e instanceof Error ? e.message : '封面上传失败'
  } finally {
    uploadingCover.value = false
    input.value = ''
  }
}

async function onBodyImageSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!isStaff.value) {
    openLogin()
    return
  }
  uploadingBody.value = true
  error.value = ''
  try {
    const result = await uploadImage(file)
    const md = `![${file.name}](${result.path || result.url})`
    insertSnippet(md)
  } catch (e) {
    error.value = e instanceof Error ? e.message : '图片上传失败'
  } finally {
    uploadingBody.value = false
    input.value = ''
  }
}

onMounted(async () => {
  await loadCategories()
  await loadPost()
})

watch(
  () => route.value.name + route.value.params.id,
  async () => {
    if (route.value.name === 'article-write') {
      title.value = ''
      titleEn.value = ''
      excerpt.value = ''
      body.value = ''
      img.value = ''
      tagsInput.value = ''
      featured.value = false
      published.value = false
      error.value = ''
    } else if (isEdit.value) {
      await loadPost()
    }
  },
)
</script>

<template>
  <div class="page-shell editor">
    <div class="container">
      <div class="editor__top">
        <button type="button" class="editor__back font-body" @click="cancelEdit">← 返回</button>
        <h1 class="editor__title font-display">{{ pageTitle }}</h1>
        <p class="editor__hint font-body">正文使用 Markdown（支持标题、列表、链接、代码块等）</p>
      </div>

      <div v-if="!isStaff" class="editor__warn font-body">
        当前账号无写作权限，请使用 staff 账号登录（demo@example.com）。
        <button type="button" class="editor__link" @click="openLogin">去登录</button>
      </div>

      <div v-if="loading" class="editor__state font-body">加载中…</div>

      <form v-else class="editor__form" @submit.prevent>
        <label class="field">
          <span class="font-body">标题 *</span>
          <input v-model="title" class="font-body" required placeholder="文章标题" />
        </label>

        <label class="field">
          <span class="font-body">英文标题</span>
          <input v-model="titleEn" class="font-serif" placeholder="Optional English title" />
        </label>

        <div class="editor__row">
          <label class="field">
            <span class="font-body">分类 *</span>
            <input v-model="category" list="cat-list" class="font-body" required />
            <datalist id="cat-list">
              <option v-for="c in categories" :key="c" :value="c" />
            </datalist>
          </label>
          <label class="field">
            <span class="font-body">阅读时长</span>
            <input v-model="readTime" class="font-body" placeholder="5 分钟" />
          </label>
        </div>

        <label class="field">
          <span class="font-body">标签（逗号分隔）</span>
          <input v-model="tagsInput" class="font-body" placeholder="语言, 旅行, 随笔" />
        </label>

        <div class="field">
          <span class="font-body">封面图</span>
          <div class="editor__cover">
            <input v-model="img" class="font-body" placeholder="上传后自动填入，也可粘贴 URL" />
            <input
              ref="coverInput"
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif,image/svg+xml"
              hidden
              @change="onCoverSelected"
            />
            <button
              type="button"
              class="btn-upload font-body"
              :disabled="!isStaff || uploadingCover"
              @click="coverInput?.click()"
            >
              {{ uploadingCover ? '上传中…' : '上传封面' }}
            </button>
          </div>
          <img v-if="img" :src="img" alt="封面预览" class="editor__cover-preview" />
        </div>

        <label class="field">
          <span class="font-body">摘要 *</span>
          <textarea v-model="excerpt" class="font-body" rows="3" required placeholder="列表页展示的短摘要" />
        </label>

        <div class="field">
          <div class="editor__body-bar">
            <span class="font-body">正文 Markdown</span>
            <div class="editor__snippets">
              <button type="button" class="font-body" @click="insertSnippet('## 小标题')">H2</button>
              <button type="button" class="font-body" @click="insertSnippet('- 列表项')">列表</button>
              <button type="button" class="font-body" @click="insertSnippet('```\n代码\n```')">代码</button>
              <button type="button" class="font-body" @click="insertSnippet('> 引用')">引用</button>
              <input
                ref="bodyImageInput"
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif,image/svg+xml"
                hidden
                @change="onBodyImageSelected"
              />
              <button
                type="button"
                class="font-body"
                :disabled="!isStaff || uploadingBody"
                @click="bodyImageInput?.click()"
              >
                {{ uploadingBody ? '上传中…' : '插图' }}
              </button>
              <button type="button" class="font-body" @click="showPreview = !showPreview">
                {{ showPreview ? '隐藏预览' : '显示预览' }}
              </button>
            </div>
          </div>
          <div class="editor__split" :class="{ 'is-preview': showPreview }">
            <textarea
              v-model="body"
              class="font-body editor__md"
              rows="16"
              placeholder="# 标题&#10;&#10;正文从这里开始…"
            />
            <div v-if="showPreview" class="editor__preview md-body" v-html="previewHtml" />
          </div>
        </div>

        <div class="editor__checks">
          <label class="check font-body">
            <input v-model="featured" type="checkbox" />
            精选
          </label>
        </div>

        <p v-if="error" class="editor__error font-body">{{ error }}</p>

        <div class="editor__actions">
          <button type="button" class="btn-ghost font-body" @click="cancelEdit">取消</button>
          <button
            type="button"
            class="btn-ghost font-body"
            :disabled="saving || !isStaff"
            @click="saveDraft()"
          >
            {{ saving ? '保存中…' : '保存草稿' }}
          </button>
          <button
            type="button"
            class="btn-primary font-body"
            :disabled="saving || !isStaff"
            @click="savePublished()"
          >
            {{ saving ? '保存中…' : '发布文章' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped lang="less">
.editor {
  padding-top: 6rem;
  padding-bottom: 4rem;
}

.container {
  max-width: 56rem;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.editor__top {
  margin-bottom: 2rem;
}

.editor__back {
  font-size: 0.85rem;
  letter-spacing: 0.1em;
  color: var(--color-muted-fg);
  margin-bottom: 1rem;

  &:hover {
    color: var(--color-primary);
  }
}

.editor__title {
  margin: 0 0 0.5rem;
  font-size: 1.75rem;
  color: var(--color-fg);
  letter-spacing: 0.08em;
}

.editor__hint {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-dim);
}

.editor__warn {
  padding: 0.85rem 1rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(245, 200, 66, 0.35);
  background: rgba(245, 200, 66, 0.08);
  color: var(--color-soft);
  font-size: 0.85rem;
}

.editor__link {
  margin-left: 0.5rem;
  color: var(--color-primary);
  text-decoration: underline;
}

.editor__state {
  color: var(--color-muted-fg);
}

.editor__form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.editor__row {
  display: grid;
  gap: 1rem;

  @media (min-width: 640px) {
    grid-template-columns: 1fr 1fr;
  }
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;

  > span {
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    color: var(--color-secondary);
  }

  input,
  textarea {
    background: var(--color-input-bg);
    border: 1px solid var(--color-border);
    color: var(--color-fg);
    padding: 0.7rem 0.9rem;
    outline: none;
    border-radius: 2px;

    &:focus {
      border-color: var(--color-border-focus);
    }
  }
}

.editor__cover {
  display: flex;
  gap: 0.5rem;

  input {
    flex: 1;
  }
}

.btn-upload {
  flex-shrink: 0;
  padding: 0.7rem 0.9rem;
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  border: 1px solid rgba(142, 196, 250, 0.35);
  color: var(--color-secondary);
  white-space: nowrap;

  &:hover:not(:disabled) {
    background: rgba(142, 196, 250, 0.1);
  }

  &:disabled {
    opacity: 0.5;
  }
}

.editor__cover-preview {
  margin-top: 0.5rem;
  max-height: 10rem;
  width: auto;
  max-width: 100%;
  object-fit: cover;
  border: 1px solid var(--color-border);
}

.editor__body-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.45rem;

  > .font-body {
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    color: var(--color-secondary);
  }
}

.editor__snippets {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;

  button {
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    padding: 0.25rem 0.55rem;
    border: 1px solid var(--color-border);
    color: var(--color-muted-fg);

    &:hover {
      color: var(--color-fg);
      border-color: var(--color-border-strong);
    }
  }
}

.editor__split {
  display: grid;
  gap: 0.75rem;

  &.is-preview {
    @media (min-width: 900px) {
      grid-template-columns: 1fr 1fr;
    }
  }
}

.editor__md {
  min-height: 22rem;
  font-family: ui-monospace, 'Cascadia Code', Consolas, monospace;
  font-size: 0.85rem;
  line-height: 1.65;
  resize: vertical;
}

.editor__preview {
  min-height: 22rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--color-border);
  background: var(--color-card);
  overflow: auto;
}

.editor__checks {
  display: flex;
  gap: 1.5rem;
}

.check {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.85rem;
  color: var(--color-soft);
}

.editor__error {
  margin: 0;
  color: #e07070;
  font-size: 0.85rem;
}

.editor__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
}

.btn-ghost,
.btn-primary {
  padding: 0.65rem 1.25rem;
  font-size: 0.85rem;
  letter-spacing: 0.1em;
}

.btn-ghost {
  border: 1px solid var(--color-border);
  color: var(--color-muted-fg);

  &:hover {
    color: var(--color-fg);
  }
}

.btn-primary {
  background: rgba(245, 200, 66, 0.18);
  border: 1px solid rgba(245, 200, 66, 0.4);
  color: var(--color-primary);

  &:hover:not(:disabled) {
    background: rgba(245, 200, 66, 0.28);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}
</style>
