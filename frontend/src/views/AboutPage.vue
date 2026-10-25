<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchSiteAbout, type SiteAbout } from '../api/auth'
import { useAuth } from '../composables/useAuth'
import { useRouter } from '../router'
import MediaCover from '../components/MediaCover.vue'

const emptyAbout = (): SiteAbout => ({
  displayName: '',
  avatar: '',
  tagline: '',
  quote: '',
  body: '',
  focusTags: [],
  stats: [],
  timeline: [],
  timelineSubtitle: '',
  influences: [],
  techStack: [],
  stackNote: '',
})

const { isStaff } = useAuth()
const { push, paths } = useRouter()
const about = ref<SiteAbout>(emptyAbout())
const loading = ref(true)

const bioParagraphs = computed(() =>
  about.value.body
    .split(/\n+/)
    .map((p) => p.trim())
    .filter(Boolean),
)

const hasProfile = computed(
  () =>
    Boolean(
      about.value.displayName ||
        about.value.avatar ||
        about.value.tagline ||
        about.value.quote ||
        about.value.body ||
        about.value.stats.length ||
        about.value.focusTags.length,
    ),
)

const hasLower = computed(
  () =>
    about.value.timeline.length > 0 ||
    about.value.influences.length > 0 ||
    about.value.techStack.length > 0 ||
    Boolean(about.value.stackNote),
)

onMounted(async () => {
  try {
    about.value = await fetchSiteAbout()
  } catch {
    /* keep empty */
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page-shell about">
    <div class="page-header" style="margin-bottom: 0">
      <div class="page-header__glow" />
      <div class="page-header__line" />
      <div class="page-header__inner" style="padding-bottom: 0">
        <p class="page-eyebrow">✦ &nbsp; ABOUT</p>
        <h1 class="page-title">
          关于
          <span class="page-title__sub">· 旅伴自述</span>
        </h1>
      </div>
    </div>

    <div v-if="loading" class="container about__empty font-body">加载中…</div>

    <template v-else>
      <div v-if="!hasProfile && !hasLower" class="container about__empty">
        <p class="font-body">暂无介绍内容。</p>
        <button
          v-if="isStaff"
          type="button"
          class="about__cta font-body"
          @click="push(paths.profile())"
        >
          前往个人资料配置关于页
        </button>
      </div>

      <div v-if="hasProfile" class="container about__profile">
        <div class="about__layout">
          <div class="about__aside">
            <div class="about__avatar">
              <MediaCover
                :src="about.avatar"
                :alt="about.displayName || '作者'"
                :label="about.displayName || '作者'"
                seed="avatar"
              />
            </div>
            <div class="about__identity">
              <h2 class="font-display">{{ about.displayName || '未命名' }}</h2>
              <p v-if="about.tagline" class="font-body about__tagline">{{ about.tagline }}</p>
              <div v-if="about.stats.length || isStaff" class="about__rule" />
              <div v-if="about.stats.length" class="about__stats">
                <div v-for="s in about.stats" :key="s.label + s.value" class="stat">
                  <p class="font-display">{{ s.value }}</p>
                  <p class="font-body">{{ s.label }}</p>
                  <span v-if="s.sub" class="font-body">{{ s.sub }}</span>
                </div>
              </div>
              <button
                v-if="isStaff"
                type="button"
                class="about__cta font-body"
                @click="push(paths.profile())"
              >
                编辑关于页
              </button>
            </div>
          </div>

          <div class="about__bio">
            <blockquote v-if="about.quote" class="font-serif">
              "{{ about.quote }}"
            </blockquote>
            <div v-if="bioParagraphs.length" class="about__text font-body">
              <p v-for="(p, i) in bioParagraphs" :key="i">{{ p }}</p>
            </div>
            <div v-if="about.focusTags.length" class="about__tags">
              <span v-for="tag in about.focusTags" :key="tag" class="font-body">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="hasLower" class="container">
        <div class="divider-light about__divider" />
      </div>

      <div v-if="about.timeline.length" class="container about__timeline">
        <h2 class="section-title font-display">
          <span class="bar" />
          学习时间线
          <span v-if="about.timelineSubtitle" class="sub font-serif">· {{ about.timelineSubtitle }}</span>
        </h2>
        <div class="timeline">
          <div v-for="(item, i) in about.timeline" :key="i" class="timeline__item">
            <div class="timeline__dot" />
            <div class="timeline__content">
              <span class="font-body year">{{ item.year }}</span>
              <div>
                <h3 class="font-display">{{ item.title }}</h3>
                <p class="font-body">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="about.influences.length || about.techStack.length || about.stackNote"
        class="container about__cols"
      >
        <div v-if="about.influences.length">
          <h2 class="section-title font-display">
            <span class="bar" />
            影响我的人和资源
          </h2>
          <div class="influences">
            <div v-for="(inf, i) in about.influences" :key="i" class="influence">
              <div class="influence__avatar font-display">{{ inf.name?.[0] || '?' }}</div>
              <div>
                <div class="influence__head">
                  <span class="font-display">{{ inf.name }}</span>
                  <span v-if="inf.field" class="font-body">· {{ inf.field }}</span>
                </div>
                <p class="font-serif">"{{ inf.quote }}"</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="about.techStack.length || about.stackNote">
          <h2 class="section-title font-display">
            <span class="bar" />
            工具与技术栈
          </h2>
          <div class="stack">
            <div v-for="(item, i) in about.techStack" :key="i" class="stack__row">
              <div>
                <span class="dot" />
                <span class="name">{{ item.name }}</span>
              </div>
              <span class="type font-body">{{ item.type }}</span>
            </div>
          </div>
          <div v-if="about.stackNote" class="stack__note">
            <p class="font-serif">{{ about.stackNote }}</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped lang="less">
.about__profile {
  padding-top: 4rem;
  padding-bottom: 4rem;
}

.about__layout {
  display: grid;
  gap: 3.5rem;
  align-items: start;

  @media (min-width: 768px) {
    grid-template-columns: 260px 1fr;
  }
}

.about__aside {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;

  @media (min-width: 768px) {
    align-items: flex-start;
  }
}

.about__avatar {
  width: 12rem;
  height: 12rem;
  overflow: hidden;
  border: 1px solid rgba(245, 200, 66, 0.25);
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.8;
    filter: saturate(0.85) brightness(0.85);
  }
}

.about__identity {
  text-align: center;
  width: 100%;

  @media (min-width: 768px) {
    text-align: left;
  }

  h2 {
    font-size: 1.125rem;
    color: var(--color-fg);
    letter-spacing: 0.1em;
    margin: 0 0 0.125rem;
  }

  > .about__tagline {
    font-size: 0.75rem;
    color: var(--color-secondary);
    letter-spacing: 0.2em;
    margin: 0.35rem 0 0;
  }

  > .font-body {
    font-size: 0.75rem;
    color: var(--color-secondary);
    letter-spacing: 0.2em;
    margin: 0 0 1.25rem;
  }
}

.about__rule {
  height: 1px;
  margin: 1.25rem 0;
  background: linear-gradient(90deg, rgba(245, 200, 66, 0.3), transparent);
}

.about__stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.stat {
  padding: 0.75rem;
  border: 1px solid rgba(126, 184, 247, 0.1);
  background: var(--color-surface-deep);

  .font-display {
    font-size: 1rem;
    color: var(--color-primary);
    letter-spacing: 0.05em;
    line-height: 1;
    margin: 0 0 0.25rem;
  }

  .font-body {
    font-size: 0.6rem;
    color: var(--color-dim);
    letter-spacing: 0.05em;
    line-height: 1;
    margin: 0;
  }

  span {
    display: block;
    font-size: 0.58rem;
    color: var(--color-quiet-deep);
    letter-spacing: 0.05em;
    margin-top: 0.125rem;
  }
}

.about__bio {
  blockquote {
    margin: 0 0 1.5rem;
    padding: 0 0 0 1.5rem;
    border-left: 2px solid rgba(245, 200, 66, 0.3);
    background: rgba(245, 200, 66, 0.02);
    font-style: italic;
    font-size: 1.125rem;
    color: var(--color-soft);
    line-height: 2;
    white-space: pre-line;
  }
}

.about__text {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  font-size: 0.875rem;
  color: var(--color-muted-fg);
  line-height: 1.8;
  font-weight: 300;

  p {
    margin: 0;
    white-space: pre-wrap;
  }
}

.about__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding-top: 0.5rem;

  span {
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    padding: 0.25rem 0.75rem;
    border: 1px solid rgba(126, 184, 247, 0.15);
    color: var(--color-secondary);
    background: rgba(126, 184, 247, 0.05);
  }
}

.about__divider {
  margin-bottom: 4rem;
}

.about__timeline {
  margin-bottom: 5rem;
}

.section-title {
  font-size: 1rem;
  color: var(--color-fg);
  letter-spacing: 0.12em;
  margin: 0 0 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;

  .bar {
    width: 1.5rem;
    height: 1px;
    background: var(--color-secondary);
    opacity: 0.5;
  }

  .sub {
    font-style: italic;
    color: var(--color-quiet);
    font-size: 0.875rem;
    font-weight: 400;
  }
}

.timeline {
  position: relative;
  padding-left: 1.5rem;

  @media (min-width: 768px) {
    padding-left: 3rem;
  }

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.5rem;
    bottom: 0.5rem;
    width: 1px;
    background: linear-gradient(
      180deg,
      rgba(126, 184, 247, 0.3),
      rgba(245, 200, 66, 0.2),
      rgba(126, 184, 247, 0.1)
    );

    @media (min-width: 768px) {
      left: 1rem;
    }
  }
}

.timeline__item {
  position: relative;
  margin-bottom: 2.5rem;

  &:hover .timeline__dot {
    border-color: var(--color-primary);
    box-shadow: 0 0 8px rgba(245, 200, 66, 0.4);
  }
}

.timeline__dot {
  position: absolute;
  left: -1.5rem;
  top: 0.375rem;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: var(--color-bg);
  border: 1px solid rgba(245, 200, 66, 0.5);
  transition: all 0.3s;

  @media (min-width: 768px) {
    left: -3rem;
  }
}

.timeline__content {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;

  .year {
    font-family: ui-monospace, monospace;
    font-size: 0.75rem;
    color: var(--color-primary);
    letter-spacing: 0.1em;
    flex-shrink: 0;
    margin-top: 0.125rem;
    opacity: 0.7;
  }

  h3 {
    font-size: 0.875rem;
    color: var(--color-fg);
    letter-spacing: 0.06em;
    margin: 0 0 0.5rem;
  }

  p {
    font-size: 0.75rem;
    color: var(--color-dim);
    line-height: 1.8;
    font-weight: 300;
    margin: 0;
  }
}

.about__cols {
  display: grid;
  gap: 2.5rem;
  padding-bottom: 4rem;

  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
  }
}

.influences {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.influence {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid rgba(126, 184, 247, 0.07);
  background: var(--color-surface-deep);
  transition: border-color 0.3s;

  &:hover {
    border-color: rgba(126, 184, 247, 0.18);
  }
}

.influence__avatar {
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  border: 1px solid rgba(245, 200, 66, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: var(--color-primary);
}

.influence__head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;

  .font-display {
    font-size: 0.75rem;
    color: var(--color-fg);
    letter-spacing: 0.05em;
  }

  .font-body {
    font-size: 0.6rem;
    color: var(--color-quiet);
    letter-spacing: 0.05em;
  }
}

.influence .font-serif {
  margin: 0;
  font-style: italic;
  font-size: 0.75rem;
  color: var(--color-dim);
  line-height: 1.6;
}

.stack__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(126, 184, 247, 0.07);

  > div {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--color-secondary);
    opacity: 0.5;
    transition: all 0.2s;
  }

  .name {
    font-family: ui-monospace, monospace;
    font-size: 0.875rem;
    color: var(--color-soft);
    transition: color 0.2s;
  }

  .type {
    font-size: 0.65rem;
    color: var(--color-quiet);
    letter-spacing: 0.05em;
  }

  &:hover {
    .dot {
      opacity: 1;
      box-shadow: 0 0 4px #7eb8f7;
    }

    .name {
      color: var(--color-fg);
    }
  }
}

.stack__note {
  margin-top: 2rem;
  padding: 1.25rem;
  border: 1px solid rgba(126, 184, 247, 0.1);
  background: linear-gradient(135deg, var(--color-card), var(--color-muted));

  p {
    margin: 0;
    font-style: italic;
    font-size: 0.875rem;
    color: var(--color-muted-fg);
    line-height: 1.8;
  }
}

.about__empty {
  padding: 4rem 0;
  text-align: center;
  color: var(--color-dim);
  font-size: 0.875rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;

  p {
    margin: 0;
  }
}

.about__cta {
  margin-top: 1.25rem;
  padding: 0.5rem 1rem;
  border: 1px solid rgba(245, 200, 66, 0.35);
  background: transparent;
  color: var(--color-primary);
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;

  &:hover {
    border-color: var(--color-primary);
    background: rgba(245, 200, 66, 0.08);
  }
}

.about__stats + .about__cta {
  margin-top: 1.25rem;
}
</style>
