<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  createComment,
  fetchPost,
  fetchPostComments,
  togglePostLike,
} from '../api/posts'
import type { Comment, PostDetail } from '../types'
import { useAuth } from '../composables/useAuth'
import { renderMarkdownDocument } from '../utils/markdown'
import { useRouter } from '../router'
import MediaCover from '../components/MediaCover.vue'
import PostCard from '../components/PostCard.vue'
import { updatePageSeo } from '../utils/seo'

const { isAuthor, isStaff, isLoggedIn, openLogin } = useAuth()
const { route, push, paths } = useRouter()

const postKey = computed(() => route.value.params.id || '')

const post = ref<PostDetail | null>(null)
const comments = ref<Comment[]>([])
const loading = ref(true)
const error = ref('')
const liking = ref(false)
const commentBody = ref('')
const commentSending = ref(false)
const commentMessage = ref('')
const commentError = ref('')
const readingProgress = ref(0)
const bookmarked = ref(false)
const copied = ref(false)
const lightboxSrc = ref('')
const lightboxAlt = ref('')
const showTopButton = ref(false)

const markdownDoc = computed(() =>
  renderMarkdownDocument(post.value?.body || post.value?.excerpt || ''),
)
const bodyHtml = computed(() => markdownDoc.value.html)
const toc = computed(() => markdownDoc.value.toc)

function updateProgress() {
  const root = document.documentElement
  const max = root.scrollHeight - root.clientHeight
  readingProgress.value = max > 0 ? Math.min(100, Math.round((window.scrollY / max) * 100)) : 0
  showTopButton.value = window.scrollY > 520
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function applyArticleEnhancements() {
  nextTick(() => {
    document.querySelectorAll<HTMLElement>('.detail__body pre').forEach((pre) => {
      if (pre.querySelector('.code-copy')) return
      const button = document.createElement('button')
      button.className = 'code-copy font-body'
      button.type = 'button'
      button.textContent = '复制'
      button.addEventListener('click', async (event) => {
        event.stopPropagation()
        const code = pre.querySelector('code')?.textContent || ''
        await navigator.clipboard?.writeText(code)
        button.textContent = '已复制'
        window.setTimeout(() => (button.textContent = '复制'), 1400)
      })
      pre.appendChild(button)
    })

    document.querySelectorAll<HTMLElement>('.detail__body h2[id], .detail__body h3[id]').forEach((heading) => {
      if (heading.querySelector('.md-heading-copy')) return
      const button = document.createElement('button')
      button.className = 'md-heading-copy'
      button.type = 'button'
      button.setAttribute('aria-label', '复制标题链接')
      button.textContent = '⌘'
      button.addEventListener('click', async (event) => {
        event.preventDefault()
        event.stopPropagation()
        const url = `${window.location.href.split('#')[0]}#${heading.id}`
        window.history.replaceState({}, '', url)
        await navigator.clipboard?.writeText(url)
        button.textContent = '✓'
        window.setTimeout(() => (button.textContent = '⌘'), 1200)
      })
      heading.appendChild(button)
    })
  })
}

function handleBodyClick(event: Event) {
  const target = event.target as HTMLElement
  if (target.tagName === 'IMG') {
    lightboxSrc.value = (target as HTMLImageElement).src
    lightboxAlt.value = (target as HTMLImageElement).alt
  }
}

function toggleBookmark() {
  if (!post.value) return
  bookmarked.value = !bookmarked.value
  localStorage.setItem(`blog-bookmark:${post.value.id}`, bookmarked.value ? '1' : '0')
}

async function shareArticle() {
  if (!post.value) return
  const data = { title: post.value.title, text: post.value.excerpt, url: window.location.href }
  if (navigator.share) await navigator.share(data).catch(() => undefined)
  else {
    await navigator.clipboard?.writeText(window.location.href)
    copied.value = true
    window.setTimeout(() => (copied.value = false), 1500)
  }
}

function scrollToHeading(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function formatCommentTime(iso: string) {
  try {
    return new Date(iso).toLocaleString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

async function loadComments() {
  if (!postKey.value) return
  try {
    comments.value = await fetchPostComments(Number(post.value?.id || postKey.value))
  } catch {
    comments.value = []
  }
}

async function load() {
  if (!postKey.value) {
    error.value = '无效的文章链接'
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  post.value = null
  try {
    post.value = await fetchPost(postKey.value)
    bookmarked.value = localStorage.getItem(`blog-bookmark:${post.value.id}`) === '1'
    updatePageSeo({
      title: `${post.value.title} · 星野文记`,
      description: post.value.excerpt,
      url: window.location.href,
      image: post.value.img,
      type: 'article',
    })
    await loadComments()
    applyArticleEnhancements()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

async function handleLike() {
  if (!post.value || liking.value) return
  liking.value = true
  try {
    const result = await togglePostLike(post.value.id)
    post.value = { ...post.value, likeCount: result.likeCount, liked: result.liked }
  } catch {
    /* ignore */
  } finally {
    liking.value = false
  }
}

async function submitComment() {
  if (!post.value) return
  if (!isLoggedIn.value) {
    openLogin()
    return
  }
  const body = commentBody.value.trim()
  if (body.length < 2) {
    commentError.value = '评论至少 2 个字'
    return
  }
  commentSending.value = true
  commentError.value = ''
  commentMessage.value = ''
  try {
    const result = await createComment(post.value.id, body)
    commentBody.value = ''
    commentMessage.value = result.detail || '评论已提交'
    await loadComments()
  } catch (e) {
    commentError.value = e instanceof Error ? e.message : '发送失败'
  } finally {
    commentSending.value = false
  }
}

function goBack() {
  push(paths.articles())
}

function goEdit() {
  push(paths.edit(post.value?.id || postKey.value))
}

onMounted(() => {
  window.addEventListener('scroll', updateProgress, { passive: true })
  void load()
})

onBeforeUnmount(() => window.removeEventListener('scroll', updateProgress))

watch(postKey, () => {
  void load()
})

watch(bodyHtml, applyArticleEnhancements)
</script>

<template>
  <div class="page-shell detail">
    <div class="detail__progress" :style="{ width: `${readingProgress}%` }" aria-hidden="true" />
    <Transition name="page-transition">
      <button
        v-if="showTopButton"
        type="button"
        class="detail__top-button font-body"
        aria-label="回到顶部"
        @click="scrollToTop"
      >
        ↑<span>回到顶部</span>
      </button>
    </Transition>
    <div class="container">
      <div class="detail__toolbar">
        <button type="button" class="detail__back font-body" @click="goBack">
          <svg width="14" height="8" viewBox="0 0 14 8" fill="none">
            <line x1="14" y1="4" x2="3" y2="4" stroke="currentColor" stroke-width="1.2" />
            <polyline points="6.5,1 3,4 6.5,7" fill="none" stroke="currentColor" stroke-width="1.2" />
          </svg>
          返回文章列表
        </button>
        <button v-if="isAuthor && post" type="button" class="detail__edit font-body" @click="goEdit">
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

        <div class="detail__stats">
          <span class="font-body">{{ post.viewCount ?? 0 }} 阅读</span>
          <button
            type="button"
            class="detail__like font-body"
            :class="{ 'is-liked': post.liked }"
            :disabled="liking"
            @click="handleLike"
          >
            {{ post.liked ? '已赞' : '点赞' }} · {{ post.likeCount ?? 0 }}
          </button>
          <button type="button" class="detail__action font-body" :class="{ 'is-active': bookmarked }" @click="toggleBookmark">
            {{ bookmarked ? '已收藏' : '收藏' }}
          </button>
          <button type="button" class="detail__action font-body" @click="shareArticle">
            {{ copied ? '链接已复制' : '分享' }}
          </button>
        </div>

        <div class="detail__cover img-overlay">
          <MediaCover :src="post.img" :alt="post.title" :label="post.title" :seed="post.id" />
        </div>

        <p class="detail__excerpt font-body">{{ post.excerpt }}</p>
        <div class="divider-light" />

        <div class="detail__content" :class="{ 'has-toc': toc.length > 0 }">
          <aside v-if="toc.length > 0" class="detail__toc">
            <p class="detail__toc-title font-body">目录</p>
            <nav>
              <button
                v-for="item in toc"
                :key="item.id"
                type="button"
                class="detail__toc-link font-body"
                :class="`is-h${item.level}`"
                @click="scrollToHeading(item.id)"
              >
                {{ item.text }}
              </button>
            </nav>
          </aside>
          <div class="detail__body md-body" v-html="bodyHtml" @click="handleBodyClick" />
        </div>

        <div v-if="post.tags?.length" class="detail__tags">
          <span v-for="tag in post.tags" :key="tag" class="tag-pill"># {{ tag }}</span>
        </div>

        <nav v-if="post.prev || post.next" class="detail__nav">
          <button
            v-if="post.prev"
            type="button"
            class="detail__nav-item font-body"
            @click="push(paths.article(post.prev!.slug || post.prev!.id))"
          >
            <span>上一篇</span>
            <strong>{{ post.prev.title }}</strong>
          </button>
          <button
            v-if="post.next"
            type="button"
            class="detail__nav-item font-body is-next"
            @click="push(paths.article(post.next!.slug || post.next!.id))"
          >
            <span>下一篇</span>
            <strong>{{ post.next.title }}</strong>
          </button>
        </nav>

        <section v-if="post.related?.length" class="detail__related">
          <h2 class="font-display">相关文章</h2>
          <div class="detail__related-grid">
            <PostCard
              v-for="item in post.related"
              :key="item.id"
              :post="item"
              @select="(p) => push(paths.article(p.slug || p.id))"
            />
          </div>
        </section>

        <section class="detail__comments">
          <h2 class="font-display">评论</h2>

          <div v-if="comments.length" class="detail__comment-list">
            <article v-for="c in comments" :key="c.id" class="detail__comment">
              <div class="detail__comment-head">
                <span class="font-display">{{ c.authorName }}</span>
                <span class="font-body">{{ formatCommentTime(c.createdAt) }}</span>
                <span v-if="isStaff && c.approved === false" class="detail__pending font-body">
                  待审核
                </span>
              </div>
              <p class="font-body">{{ c.body }}</p>
            </article>
          </div>
          <p v-else class="detail__comment-empty font-body">暂无评论，来抢沙发吧。</p>

          <div class="detail__comment-form">
            <textarea
              v-model="commentBody"
              rows="4"
              class="font-body"
              placeholder="登录后发表评论，审核通过后将显示…"
              :disabled="commentSending"
            />
            <p v-if="commentError" class="detail__comment-msg is-error font-body">{{ commentError }}</p>
            <p v-if="commentMessage" class="detail__comment-msg font-body">{{ commentMessage }}</p>
            <button
              type="button"
              class="detail__comment-submit font-body"
              :disabled="commentSending"
              @click="submitComment"
            >
              {{ commentSending ? '发送中…' : isLoggedIn ? '发表评论' : '登录后评论' }}
            </button>
          </div>
        </section>
      </article>

      <div v-if="lightboxSrc" class="detail__lightbox" role="dialog" aria-modal="true" @click="lightboxSrc = ''">
        <button type="button" class="detail__lightbox-close" aria-label="关闭图片预览" @click="lightboxSrc = ''">×</button>
        <img :src="lightboxSrc" :alt="lightboxAlt" @click.stop />
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.detail__progress {
  position: fixed;
  z-index: 100;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--color-secondary), var(--color-primary));
  transition: width 0.12s ease-out;
  animation: progressGlow 2.4s ease-in-out infinite;
}

.detail__top-button {
  position: fixed;
  right: clamp(1rem, 3vw, 2rem);
  bottom: 1.5rem;
  z-index: 90;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--color-border-strong);
  border-radius: 999px;
  color: var(--color-secondary);
  background: color-mix(in srgb, var(--color-nav-bg) 88%, transparent);
  box-shadow: 0 0.6rem 1.6rem rgba(30, 12, 14, 0.2);
  backdrop-filter: blur(12px);
  transition: color 0.2s ease, transform 0.2s ease, border-color 0.2s ease;

  span {
    font-size: 0.62rem;
    letter-spacing: 0.08em;
  }

  &:hover {
    color: var(--color-fg);
    border-color: var(--color-secondary);
    transform: translateY(-3px);
  }
}

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
  margin: 0 0 1rem;
  font-size: 1rem;
  color: var(--color-muted-fg);
  font-style: italic;
}

.detail__stats {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;

  > .font-body {
    font-size: 0.75rem;
    color: var(--color-dim);
    letter-spacing: 0.08em;
  }
}

.detail__like {
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  padding: 0.35rem 0.75rem;
  border: 1px solid rgba(126, 184, 247, 0.25);
  color: var(--color-secondary);
  transition: all 0.2s;

  &:hover:not(:disabled) {
    border-color: rgba(245, 200, 66, 0.45);
    color: var(--color-primary);
  }

  &.is-liked {
    border-color: rgba(245, 200, 66, 0.45);
    color: var(--color-primary);
    background: rgba(245, 200, 66, 0.1);
  }

  &:disabled {
    opacity: 0.6;
  }
}

.detail__action {
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  color: var(--color-dim);
  transition: color 0.2s, border-color 0.2s;

  &:hover,
  &.is-active {
    color: var(--color-primary);
  }
}

.detail__lightbox {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: grid;
  place-items: center;
  padding: 2rem;
  background: rgba(10, 7, 8, 0.92);
  cursor: zoom-out;

  img {
    max-width: min(92vw, 1100px);
    max-height: 88vh;
    object-fit: contain;
    box-shadow: 0 1rem 4rem rgba(0, 0, 0, 0.45);
  }
}

.detail__lightbox-close {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  color: #fff;
  font-size: 2rem;
  line-height: 1;
}

:deep(.detail__body pre) {
  position: relative;
}

:deep(.code-copy) {
  position: absolute;
  top: 0.5rem;
  right: 0.6rem;
  padding: 0.2rem 0.5rem;
  color: var(--color-dim);
  border: 1px solid var(--color-border);
  font-size: 0.65rem;
  letter-spacing: 0.08em;

  &:hover {
    color: var(--color-primary);
    border-color: var(--color-border-strong);
  }
}

:deep(.detail__body img) {
  cursor: zoom-in;
  transition: opacity 0.2s, transform 0.2s;

  &:hover {
    opacity: 0.86;
    transform: scale(1.01);
  }
}

.detail__cover {
  margin-bottom: 1.75rem;
  overflow: hidden;
  background: var(--color-card);
  height: min(26rem, 50vw);
  min-height: 12rem;

  :deep(.media-cover__ph) {
    min-height: 12rem;
  }
}

.detail__excerpt {
  font-size: 1rem;
  color: var(--color-soft);
  line-height: 1.9;
  margin: 0 0 1.5rem;
}

.detail__content {
  display: block;

  &.has-toc {
    @media (min-width: 960px) {
      display: grid;
      grid-template-columns: 11rem 1fr;
      gap: 2.5rem;
      align-items: start;
    }
  }
}

.detail__toc {
  position: sticky;
  top: 5.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid rgba(126, 184, 247, 0.12);
  background: rgba(126, 184, 247, 0.03);
}

.detail__toc-title {
  margin: 0 0 0.75rem;
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  color: var(--color-secondary);
}

.detail__toc-link {
  display: block;
  width: 100%;
  text-align: left;
  margin: 0.35rem 0;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--color-dim);
  transition: color 0.2s;

  &:hover {
    color: var(--color-primary);
  }

  &.is-h3 {
    padding-left: 0.75rem;
    font-size: 0.7rem;
  }
}

.detail__body {
  margin: 0 0 2rem;
  min-width: 0;
}

.detail__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2.5rem;
}

.detail__nav {
  display: grid;
  gap: 1rem;
  margin-bottom: 3rem;

  @media (min-width: 640px) {
    grid-template-columns: 1fr 1fr;
  }
}

.detail__nav-item {
  text-align: left;
  padding: 1rem 1.1rem;
  border: 1px solid rgba(126, 184, 247, 0.12);
  background: rgba(126, 184, 247, 0.03);
  transition: border-color 0.2s;

  span {
    display: block;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: var(--color-dim);
    margin-bottom: 0.35rem;
  }

  strong {
    display: block;
    font-weight: 400;
    font-size: 0.85rem;
    color: var(--color-fg);
    line-height: 1.5;
  }

  &:hover {
    border-color: rgba(245, 200, 66, 0.35);
  }

  &.is-next {
    text-align: right;
  }
}

.detail__related {
  margin-bottom: 3rem;

  h2 {
    font-size: 1rem;
    letter-spacing: 0.15em;
    color: var(--color-secondary);
    margin: 0 0 1.25rem;
  }
}

.detail__related-grid {
  display: grid;
  gap: 1rem;

  @media (min-width: 640px) {
    grid-template-columns: repeat(3, 1fr);
  }
}

.detail__comments {
  padding-top: 2rem;
  border-top: 1px solid rgba(126, 184, 247, 0.1);

  h2 {
    font-size: 1rem;
    letter-spacing: 0.15em;
    color: var(--color-secondary);
    margin: 0 0 1.5rem;
  }
}

.detail__comment-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail__comment {
  padding: 1rem 1.1rem;
  border: 1px solid rgba(126, 184, 247, 0.1);
  background: rgba(126, 184, 247, 0.02);

  p {
    margin: 0;
    font-size: 0.875rem;
    line-height: 1.8;
    color: var(--color-soft);
  }
}

.detail__comment-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.5rem;

  .font-display {
    font-size: 0.75rem;
    color: var(--color-fg);
  }

  .font-body {
    font-size: 0.65rem;
    color: var(--color-faint);
  }
}

.detail__pending {
  font-size: 0.6rem;
  letter-spacing: 0.08em;
  padding: 0.1rem 0.4rem;
  border: 1px solid rgba(245, 200, 66, 0.35);
  color: var(--color-primary);
}

.detail__comment-empty {
  margin: 0 0 1.5rem;
  font-size: 0.85rem;
  color: var(--color-dim);
}

.detail__comment-form {
  textarea {
    width: 100%;
    background: var(--color-input-bg);
    border: 1px solid var(--color-border);
    color: var(--color-fg);
    padding: 0.85rem 1rem;
    outline: none;
    resize: vertical;
    font-size: 0.875rem;
    line-height: 1.7;

    &:focus {
      border-color: var(--color-border-focus);
    }
  }
}

.detail__comment-msg {
  margin: 0.65rem 0 0;
  font-size: 0.75rem;
  color: var(--color-secondary);

  &.is-error {
    color: #e07070;
  }
}

.detail__comment-submit {
  margin-top: 0.85rem;
  font-size: 0.8rem;
  letter-spacing: 0.12em;
  padding: 0.55rem 1.1rem;
  border: 1px solid rgba(245, 200, 66, 0.35);
  color: var(--color-primary);

  &:hover:not(:disabled) {
    background: rgba(245, 200, 66, 0.1);
  }

  &:disabled {
    opacity: 0.55;
  }
}
</style>
