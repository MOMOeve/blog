<script setup lang="ts">
import { reactive, ref } from 'vue'
import { submitContact } from '../api/inbox'
import { ApiError } from '../api/client'
import { AVATAR_IMG } from '../data/posts'
import MediaCover from '../components/MediaCover.vue'

type FormState = 'idle' | 'sending' | 'sent' | 'error'

const form = reactive({ name: '', email: '', subject: '', message: '' })
const formState = ref<FormState>('idle')
const errorMessage = ref('')

const socialLinks = [
  { name: '微博', handle: '@星野凛_Rin', desc: '日常碎片与学习记录' },
  { name: 'GitHub', handle: 'hoshino-rin', desc: '开源项目与代码片段' },
  { name: 'Twitter / X', handle: '@hoshino_codes', desc: '技术碎碎念 · 语言学习打卡' },
  { name: '邮箱', handle: 'hello@hoshino-rin.com', desc: '合作 · 交流 · 互相学习' },
]

const faqs = [
  {
    q: '可以问代码/语言相关问题吗？',
    a: '当然可以，能帮上忙的我会尽力回答。问题越具体，越容易得到有用的回复。',
  },
  {
    q: '博客内容可以转载吗？',
    a: '非商业用途注明出处即可，商业用途请先联系我。',
  },
  {
    q: '可以交流语言学习经验吗？',
    a: '非常欢迎！同样在学语言的朋友随时都可以来聊，一起进步。',
  },
]

async function handleSubmit(e: Event) {
  e.preventDefault()
  formState.value = 'sending'
  errorMessage.value = ''
  try {
    await submitContact({
      name: form.name.trim(),
      email: form.email.trim(),
      subject: form.subject.trim(),
      message: form.message.trim(),
    })
    formState.value = 'sent'
  } catch (err) {
    formState.value = 'error'
    errorMessage.value = err instanceof ApiError ? err.message : '发送失败，请稍后再试'
  }
}

function resetForm() {
  formState.value = 'idle'
  errorMessage.value = ''
  form.name = ''
  form.email = ''
  form.subject = ''
  form.message = ''
}
</script>

<template>
  <div class="page-shell">
    <div class="page-header">
      <div class="page-header__glow" />
      <div class="page-header__line" />
      <div class="page-header__inner">
        <p class="page-eyebrow animate-fade-up">✦ &nbsp; CONTACT</p>
        <h1 class="page-title animate-fade-up-delay-1">
          联系
          <span class="page-title__sub">· 说点什么</span>
        </h1>
        <p class="page-desc animate-fade-up-delay-2">关于代码、语言、学习方法，或者只是想打个招呼——都欢迎</p>
      </div>
    </div>

    <div class="container contact">
      <div class="contact__layout">
        <div>
          <div v-if="formState === 'sent'" class="sent">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none" class="animate-fade-up">
              <circle cx="32" cy="32" r="28" stroke="#7eb8f7" stroke-width="0.8" opacity="0.3" />
              <circle cx="32" cy="32" r="18" stroke="#f5c842" stroke-width="1" opacity="0.6" />
              <circle cx="32" cy="32" r="6" fill="#f5c842" opacity="0.9" />
              <line x1="32" y1="4" x2="32" y2="16" stroke="#f5c842" stroke-width="1" opacity="0.5" />
              <line x1="32" y1="48" x2="32" y2="60" stroke="#f5c842" stroke-width="1" opacity="0.5" />
              <line x1="4" y1="32" x2="16" y2="32" stroke="#f5c842" stroke-width="1" opacity="0.5" />
              <line x1="48" y1="32" x2="60" y2="32" stroke="#f5c842" stroke-width="1" opacity="0.5" />
            </svg>
            <h3 class="font-display animate-fade-up-delay-1">消息已送出</h3>
            <p class="font-body animate-fade-up-delay-2">
              消息已收到，通常在 48 小时内回复。如果是代码或语言相关的问题，可以多等一会儿，我会认真想一想再回。
            </p>
            <button type="button" class="font-body" @click="resetForm">再发一条</button>
          </div>

          <form v-else class="form" @submit="handleSubmit">
            <div class="form__row">
              <label class="field">
                <span class="font-body">你的名字</span>
                <input v-model="form.name" type="text" placeholder="星野 凛" class="font-body" />
              </label>
              <label class="field">
                <span class="font-body">邮箱地址</span>
                <input v-model="form.email" type="email" placeholder="your@email.com" class="font-body" />
              </label>
            </div>
            <label class="field">
              <span class="font-body">主题</span>
              <input v-model="form.subject" type="text" placeholder="关于这次联系的主题…" class="font-body" />
            </label>
            <label class="field">
              <span class="font-body">留言内容</span>
              <textarea
                v-model="form.message"
                rows="6"
                placeholder="想说的话，不必太长，写清楚就好…"
                class="font-body"
              />
            </label>
            <p v-if="formState === 'error'" class="form__error font-body">{{ errorMessage }}</p>
            <button
              type="submit"
              class="form__submit font-body"
              :disabled="formState === 'sending' || !form.name || !form.email || !form.message"
            >
              <template v-if="formState === 'sending'">
                <span class="spinner" />
                发送中…
              </template>
              <template v-else>
                发送消息
                <svg width="16" height="10" viewBox="0 0 16 10" fill="none">
                  <line x1="0" y1="5" x2="13" y2="5" stroke="currentColor" stroke-width="1.2" />
                  <polyline points="9,1 13,5 9,9" fill="none" stroke="currentColor" stroke-width="1.2" />
                </svg>
              </template>
            </button>
          </form>
        </div>

        <aside class="aside">
          <div class="aside__note">
            <p class="font-serif">
              "能和同样在学代码或语言的人交流，是写这个博客最开心的事之一。"
            </p>
            <div class="aside__author">
              <div class="aside__avatar">
                <MediaCover :src="AVATAR_IMG" alt="星野凛" label="星野凛" seed="avatar" />
              </div>
              <div>
                <p class="font-display">星野 凛</p>
                <span class="font-body">Frontend Dev · 语言 N2</span>
              </div>
            </div>
          </div>

          <div>
            <h3 class="aside__heading font-display">
              <span class="bar" />
              社交媒体
              <span class="line" />
            </h3>
            <div class="socials">
              <div v-for="link in socialLinks" :key="link.name" class="social">
                <div>
                  <div class="social__head">
                    <span class="font-display">{{ link.name }}</span>
                    <span class="font-body">{{ link.handle }}</span>
                  </div>
                  <p class="font-body">{{ link.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 class="aside__heading font-display">
              <span class="bar" />
              常见问题
            </h3>
            <div class="faqs">
              <div v-for="(faq, i) in faqs" :key="i" class="faq">
                <p class="font-display">{{ faq.q }}</p>
                <p class="font-body">{{ faq.a }}</p>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less">
.contact__layout {
  display: grid;
  gap: 3.5rem;

  @media (min-width: 1024px) {
    grid-template-columns: 1fr 360px;
  }
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form__row {
  display: grid;
  gap: 1.25rem;

  @media (min-width: 640px) {
    grid-template-columns: 1fr 1fr;
  }
}

.field {
  display: block;

  span {
    display: block;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: var(--color-dim);
    margin-bottom: 0.5rem;
  }

  input,
  textarea {
    width: 100%;
    background: rgba(126, 184, 247, 0.03);
    border: 1px solid rgba(126, 184, 247, 0.12);
    color: var(--color-fg);
    font-size: 0.875rem;
    letter-spacing: 0.03em;
    padding: 0.75rem 1rem;
    outline: none;
    font-weight: 300;
    transition: border-color 0.2s;
    resize: none;

    &::placeholder {
      color: var(--color-faint);
    }

    &:focus {
      border-color: rgba(126, 184, 247, 0.35);
    }
  }
}

.form__submit {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  align-self: flex-start;
  font-size: 0.875rem;
  letter-spacing: 0.18em;
  border: 1px solid rgba(245, 200, 66, 0.35);
  color: var(--color-primary);
  padding: 0.875rem 2rem;
  transition: all 0.3s;

  svg {
    transition: transform 0.3s;
  }

  &:hover:not(:disabled) {
    background: rgba(245, 200, 66, 0.08);
    border-color: rgba(245, 200, 66, 0.6);
    box-shadow: 0 0 24px rgba(245, 200, 66, 0.15);

    svg {
      transform: translateX(4px);
    }
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.form__error {
  margin: 0;
  font-size: 0.75rem;
  color: #f08080;
  letter-spacing: 0.05em;
}

.spinner {
  display: inline-block;
  width: 0.75rem;
  height: 0.75rem;
  border: 1px solid #f5c842;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.sent {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
  text-align: center;

  h3 {
    font-size: 1.125rem;
    color: var(--color-fg);
    letter-spacing: 0.08em;
    margin: 2rem 0 0.75rem;
  }

  p {
    font-size: 0.875rem;
    color: var(--color-dim);
    line-height: 1.8;
    font-weight: 300;
    margin: 0 0 2rem;
    max-width: 24rem;
  }

  button {
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    color: var(--color-secondary);
    border: 1px solid rgba(126, 184, 247, 0.2);
    padding: 0.625rem 1.5rem;
    transition: all 0.2s;

    &:hover {
      border-color: rgba(126, 184, 247, 0.4);
      color: var(--color-fg);
    }
  }
}

.aside {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.aside__note {
  padding: 1.5rem;
  border: 1px solid rgba(126, 184, 247, 0.1);
  background: linear-gradient(145deg, rgba(11, 16, 40, 0.8), rgba(8, 12, 28, 0.9));

  .font-serif {
    margin: 0 0 1rem;
    font-style: italic;
    font-size: 0.875rem;
    color: var(--color-muted-fg);
    line-height: 1.8;
  }
}

.aside__author {
  display: flex;
  align-items: center;
  gap: 0.75rem;

  .font-display {
    font-size: 0.75rem;
    color: var(--color-fg);
    letter-spacing: 0.05em;
    margin: 0;
  }

  .font-body {
    font-size: 0.6rem;
    color: #3d5070;
    letter-spacing: 0.05em;
  }
}

.aside__avatar {
  width: 1.75rem;
  height: 1.75rem;
  overflow: hidden;
  border: 1px solid rgba(245, 200, 66, 0.2);
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.8;
  }
}

.aside__heading {
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

.socials {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.social {
  padding: 0.875rem;
  border: 1px solid rgba(126, 184, 247, 0.07);
  background: rgba(11, 16, 40, 0.4);
  cursor: pointer;
  transition: border-color 0.3s;

  &:hover {
    border-color: rgba(126, 184, 247, 0.2);
  }
}

.social__head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.125rem;

  .font-display {
    font-size: 0.75rem;
    color: var(--color-fg);
    letter-spacing: 0.05em;
  }

  .font-body {
    font-size: 0.6rem;
    color: #3d5070;
    letter-spacing: 0.05em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.social p {
  margin: 0;
  font-size: 0.6rem;
  color: #3d5070;
  letter-spacing: 0.05em;
}

.faq {
  padding: 1rem 0;
  border-bottom: 1px solid rgba(126, 184, 247, 0.07);

  .font-display {
    font-size: 0.75rem;
    color: var(--color-soft);
    letter-spacing: 0.05em;
    margin: 0 0 0.5rem;
  }

  .font-body {
    font-size: 0.75rem;
    color: var(--color-dim);
    line-height: 1.8;
    font-weight: 300;
    margin: 0;
  }
}
</style>
