<script setup lang="ts">
import { HERO_IMG } from '../data/posts'
import MediaCover from './MediaCover.vue'

defineEmits<{
  'read-more': []
}>()

const particles = [
  { cx: '15%', cy: '25%', r: 1.5, delay: '0s' },
  { cx: '72%', cy: '18%', r: 1, delay: '1.2s' },
  { cx: '88%', cy: '42%', r: 1.5, delay: '0.6s' },
  { cx: '45%', cy: '65%', r: 1, delay: '2s' },
  { cx: '62%', cy: '78%', r: 2, delay: '0.4s' },
  { cx: '28%', cy: '55%', r: 1, delay: '1.8s' },
]
</script>

<template>
  <section class="hero">
    <div class="hero__bg">
      <MediaCover :src="HERO_IMG" alt="黄昏天空" label="星野文记" seed="hero" />
    </div>
    <div class="hero__grad-v" />
    <div class="hero__grad-h" />

    <svg class="hero__rays" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
      <defs>
        <linearGradient id="ray1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#f5c842" stop-opacity="0" />
          <stop offset="50%" stop-color="#f5c842" stop-opacity="0.12" />
          <stop offset="100%" stop-color="#f5c842" stop-opacity="0" />
        </linearGradient>
        <linearGradient id="ray2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#7eb8f7" stop-opacity="0" />
          <stop offset="50%" stop-color="#7eb8f7" stop-opacity="0.07" />
          <stop offset="100%" stop-color="#7eb8f7" stop-opacity="0" />
        </linearGradient>
      </defs>
      <polygon class="light-ray" points="30%,0 55%,0 78%,100% 5%,100%" fill="url(#ray1)" />
      <polygon
        class="light-ray"
        style="animation-delay: 2.5s"
        points="50%,0 65%,0 90%,100% 72%,100%"
        fill="url(#ray2)"
      />
      <polygon
        class="light-ray"
        style="animation-delay: 1.2s"
        points="20%,0 30%,0 48%,100% 35%,100%"
        fill="url(#ray1)"
      />
    </svg>

    <svg class="hero__particles" xmlns="http://www.w3.org/2000/svg">
      <circle
        v-for="(p, i) in particles"
        :key="i"
        :cx="p.cx"
        :cy="p.cy"
        :r="p.r"
        fill="#f5c842"
        opacity="0.7"
        :style="{ animation: `particleFloat 6s ${p.delay} ease-in-out infinite` }"
      />
    </svg>

    <div class="hero__content">
      <div class="hero__copy">
        <p class="hero__eyebrow font-body animate-fade-up">✦ &nbsp; 代码 · 语言 · 生活记录</p>
        <h1 class="hero__title font-display animate-fade-up-delay-1">
          <span class="gold-shimmer">学习这件事，没有终点</span>
          <br />
          <span class="hero__subtitle">只有一个又一个的此刻</span>
        </h1>
        <p class="hero__desc font-body animate-fade-up-delay-2">
          记录写代码时的思考与踩坑，以及学语言路上那些笨拙而真实的进步。 偶尔也写一点生活里细小的事。
        </p>
        <div class="hero__cta animate-fade-up-delay-3">
          <button type="button" class="hero__btn font-body" @click="$emit('read-more')">
            阅读全文
            <svg width="16" height="10" viewBox="0 0 16 10" fill="none">
              <line x1="0" y1="5" x2="13" y2="5" stroke="currentColor" stroke-width="1.2" />
              <polyline points="9,1 13,5 9,9" fill="none" stroke="currentColor" stroke-width="1.2" />
            </svg>
          </button>
          <span class="font-body">10 分钟阅读</span>
        </div>
      </div>
    </div>

    <div class="hero__fade" />
    <div class="hero__scroll">
      <span class="font-body">SCROLL</span>
      <div class="hero__scroll-line" />
    </div>
  </section>
</template>

<style scoped lang="less">
.hero {
  position: relative;
  width: 100%;
  height: 92vh;
  min-height: 600px;
  overflow: hidden;
}

.hero__bg {
  position: absolute;
  inset: 0;
  background: var(--color-card);

  :deep(.media-cover__img),
  :deep(.media-cover__ph) {
    filter: saturate(1.15) brightness(0.55);
  }
}

.hero__grad-v {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(18, 26, 46, 0.2) 0%,
    rgba(18, 26, 46, 0.05) 35%,
    rgba(18, 26, 46, 0.55) 70%,
    rgba(18, 26, 46, 0.92) 100%
  );
}

.hero__grad-h {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(18, 26, 46, 0.5) 0%, transparent 50%, rgba(18, 26, 46, 0.2) 100%);
}

.hero__rays,
.hero__particles {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.hero__content {
  position: relative;
  z-index: 10;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 0 2rem 5rem;
  max-width: var(--max-width);
  margin: 0 auto;
}

.hero__copy {
  max-width: 42rem;
}

.hero__eyebrow {
  font-size: 0.75rem;
  letter-spacing: 0.35em;
  color: var(--color-secondary);
  margin: 0 0 1.25rem;
  opacity: 0.8;
}

.hero__title {
  margin: 0 0 1.5rem;
  line-height: 1.2;
  font-size: clamp(2.2rem, 5vw, 3.8rem);
  letter-spacing: 0.04em;
}

.hero__subtitle {
  color: var(--color-fg);
  font-size: 0.6em;
  font-weight: 300;
  letter-spacing: 0.08em;
}

.hero__desc {
  color: var(--color-soft);
  font-size: 1rem;
  line-height: 1.8;
  font-weight: 300;
  margin: 0 0 2rem;
  max-width: 32rem;
}

.hero__cta {
  display: flex;
  align-items: center;
  gap: 1.25rem;

  span {
    font-size: 0.75rem;
    color: var(--color-dim);
    letter-spacing: 0.1em;
  }
}

.hero__btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  letter-spacing: 0.18em;
  color: var(--color-primary);
  border: 1px solid rgba(245, 200, 66, 0.35);
  padding: 0.75rem 1.5rem;
  transition: all 0.3s;

  svg {
    transition: transform 0.3s;
  }

  &:hover {
    background: rgba(245, 200, 66, 0.08);
    border-color: rgba(245, 200, 66, 0.6);

    svg {
      transform: translateX(4px);
    }
  }
}

.hero__fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 8rem;
  pointer-events: none;
  background: linear-gradient(transparent, var(--color-hero-fade));
}

.hero__scroll {
  position: absolute;
  bottom: 2rem;
  right: 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.4;

  span {
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    color: var(--color-secondary);
    writing-mode: vertical-rl;
    margin-bottom: 0.25rem;
  }
}

.hero__scroll-line {
  width: 1px;
  height: 3rem;
  background: linear-gradient(to bottom, #7eb8f7, transparent);
}
</style>
