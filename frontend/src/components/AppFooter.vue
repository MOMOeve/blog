<script setup lang="ts">
import { navLinks } from '../data/posts'
import { useRouter } from '../router'

const { push } = useRouter()
</script>

<template>
  <footer class="footer">
    <div class="footer__glow" />
    <div class="footer__inner">
      <div class="footer__grid">
        <div>
          <div class="footer__brand">
            <svg viewBox="0 0 28 28" fill="none" class="footer__logo">
              <circle cx="14" cy="14" r="6" fill="none" stroke="#f5c842" stroke-width="1.5" opacity="0.8" />
              <circle cx="14" cy="14" r="2.5" fill="#f5c842" opacity="0.9" />
            </svg>
            <span class="font-display">星野文记</span>
          </div>
          <p class="footer__desc font-body">
            记录代码与语言的学习历程。
            <br />
            写给未来那个回头看的自己。
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
          <p class="footer__desc font-body">不错过每一次日落与文字。</p>
          <div class="footer__subscribe">
            <input type="email" placeholder="your@email.com" class="font-body" />
            <button type="button" class="font-body">订阅</button>
          </div>
        </div>
      </div>

      <div class="divider-light footer__divider" />

      <div class="footer__bottom">
        <p class="font-body">© 2026 星野文记 · 代码与语言，慢慢来</p>
        <div class="footer__socials">
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
  border-top: 1px solid rgba(126, 184, 247, 0.1);
  overflow: hidden;
}

.footer__glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(180deg, transparent, rgba(14, 21, 53, 0.3));
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

    &:hover {
      background: rgba(245, 200, 66, 0.25);
    }
  }
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
