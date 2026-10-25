<script setup lang="ts">
import { ref } from 'vue'
import { navLinks } from '../data/posts'
import { SITE_DESC, SITE_NAME, SITE_TAGLINE } from '../data/site'
import BrandMark from './BrandMark.vue'
import { subscribeNewsletter } from '../api/inbox'
import { ApiError } from '../api/client'
import { useRouter } from '../router'

const { push } = useRouter()

const subscribeEmail = ref('')
const subscribeState = ref<'idle' | 'sending' | 'done' | 'error'>('idle')
const subscribeMessage = ref('')

async function handleSubscribe() {
  const email = subscribeEmail.value.trim()
  if (!email) return
  subscribeState.value = 'sending'
  subscribeMessage.value = ''
  try {
    const result = await subscribeNewsletter(email)
    subscribeState.value = 'done'
    subscribeMessage.value = result.detail ?? '订阅成功，感谢关注'
    subscribeEmail.value = ''
  } catch (err) {
    subscribeState.value = 'error'
    subscribeMessage.value = err instanceof ApiError ? err.message : '订阅失败，请稍后再试'
  }
}
</script>

<template>
  <footer class="footer">
    <div class="footer__glow" />
    <div class="footer__inner">
      <div class="footer__grid">
        <div>
          <div class="footer__brand">
            <BrandMark :size="28" class="footer__logo" />
            <span class="font-display">{{ SITE_NAME }}</span>
          </div>
          <p class="footer__desc font-body">
            {{ SITE_DESC }}
          </p>
        </div>

        <div>
          <h5 class="footer__heading font-display">导航</h5>
          <ul class="footer__nav">
            <li v-for="item in navLinks" :key="item.page">
              <button type="button" class="font-body" @click="push(item.path)">
                {{ item.label }}
              </button>
            </li>
          </ul>
        </div>

        <div>
          <h5 class="footer__heading font-display">订阅更新</h5>
          <p class="footer__desc font-body">像囤积香料一样，收好每一封新讯。</p>
          <div class="footer__subscribe">
            <input
              v-model="subscribeEmail"
              type="email"
              placeholder="your@email.com"
              class="font-body"
              :disabled="subscribeState === 'sending'"
              @keydown.enter.prevent="handleSubscribe"
            />
            <button
              type="button"
              class="font-body"
              :disabled="subscribeState === 'sending' || !subscribeEmail.trim()"
              @click="handleSubscribe"
            >
              {{ subscribeState === 'sending' ? '提交中…' : '订阅' }}
            </button>
          </div>
          <p v-if="subscribeMessage" class="footer__subscribe-msg font-body">{{ subscribeMessage }}</p>
        </div>
      </div>

      <div class="divider-light footer__divider" />

        <div class="footer__bottom">
        <p class="font-body">© 2026 {{ SITE_NAME }} · {{ SITE_TAGLINE }}</p>
        <div class="footer__socials">
          <a href="/api/v1/feed/rss/" target="_blank" rel="noopener noreferrer" class="font-body">
            RSS
          </a>
          <a href="/api/v1/feed/sitemap.xml" target="_blank" rel="noopener noreferrer" class="font-body">
            Sitemap
          </a>
          <button v-for="s in ['微博', 'GitHub', 'Twitter']" :key="s" type="button" class="font-body">
            {{ s }}
          </button>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped lang="less">
.footer {
  position: relative;
  border-top: 1px solid var(--color-border);
  overflow: hidden;
}

.footer__glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(180deg, transparent, var(--color-header-glow));
}

.footer__inner {
  position: relative;
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 4rem 1.5rem;
}

.footer__grid {
  display: grid;
  gap: 3rem;
  margin-bottom: 3rem;

  @media (min-width: 768px) {
    grid-template-columns: repeat(3, 1fr);
  }
}

.footer__brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;

  span {
    font-size: 0.875rem;
    letter-spacing: 0.2em;
    color: var(--color-fg);
  }
}

.footer__logo {
  width: 1.5rem;
  height: 1.5rem;
}

.footer__desc {
  font-size: 0.75rem;
  color: var(--color-dim);
  line-height: 1.8;
  font-weight: 300;
  margin: 0 0 1rem;
}

.footer__heading {
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: var(--color-secondary);
  margin: 0 0 1.25rem;
}

.footer__nav {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;

  button {
    font-size: 0.875rem;
    color: var(--color-dim);
    letter-spacing: 0.05em;
    transition: color 0.2s;

    &:hover {
      color: var(--color-fg);
    }
  }
}

.footer__subscribe {
  display: flex;

  input {
    flex: 1;
    background: rgba(126, 184, 247, 0.06);
    border: 1px solid rgba(126, 184, 247, 0.15);
    color: var(--color-fg);
    font-size: 0.75rem;
    padding: 0.625rem 1rem;
    outline: none;
    letter-spacing: 0.05em;

    &::placeholder {
      color: var(--color-faint);
    }

    &:focus {
      border-color: rgba(126, 184, 247, 0.4);
    }
  }

  button {
    padding: 0.625rem 1rem;
    background: rgba(245, 200, 66, 0.15);
    border: 1px solid rgba(245, 200, 66, 0.3);
    color: var(--color-primary);
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    transition: background 0.2s;

    &:hover:not(:disabled) {
      background: rgba(245, 200, 66, 0.25);
    }

    &:disabled {
      opacity: 0.45;
      cursor: not-allowed;
    }
  }
}

.footer__subscribe-msg {
  margin: 0.75rem 0 0;
  font-size: 0.65rem;
  color: var(--color-secondary);
  letter-spacing: 0.05em;
  line-height: 1.6;
}

.footer__divider {
  margin-bottom: 1.5rem;
}

.footer__bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;

  @media (min-width: 768px) {
    flex-direction: row;
  }

  p {
    margin: 0;
    font-size: 0.65rem;
    color: var(--color-faint);
    letter-spacing: 0.05em;
  }
}

.footer__socials {
  display: flex;
  align-items: center;
  gap: 1.5rem;

  a,
  button {
    font-size: 0.65rem;
    color: var(--color-faint);
    letter-spacing: 0.05em;
    transition: color 0.2s;

    &:hover {
      color: var(--color-secondary);
    }
  }
}
</style>
