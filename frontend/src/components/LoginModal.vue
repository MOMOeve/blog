<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { requestPasswordReset } from '../api/auth'
import { useAuth } from '../composables/useAuth'

const { loginOpen, loading, error, closeLogin, login, register } = useAuth()

const mode = ref<'login' | 'register' | 'reset'>('login')
const resetMessage = ref('')

const form = reactive({
  email: '',
  password: '',
  displayName: '',
})

watch(loginOpen, (open) => {
  if (!open) {
    form.email = ''
    form.password = ''
    form.displayName = ''
    mode.value = 'login'
    resetMessage.value = ''
  }
})

function switchMode(next: 'login' | 'register' | 'reset') {
  mode.value = next
  error.value = ''
  resetMessage.value = ''
}

async function onSubmit(e: Event) {
  e.preventDefault()
  try {
    if (mode.value === 'reset') {
      const result = await requestPasswordReset(form.email.trim())
      resetMessage.value = result.detail
      return
    }
    if (mode.value === 'register') {
      await register({
        email: form.email.trim(),
        password: form.password,
        displayName: form.displayName.trim() || undefined,
      })
    } else {
      await login({ email: form.email.trim(), password: form.password })
    }
  } catch {
    /* error 已在 useAuth 中设置 */
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="loginOpen" class="login-mask" @click.self="closeLogin">
      <div class="login-modal" role="dialog" aria-modal="true" aria-labelledby="login-title">
        <button type="button" class="login-modal__close" aria-label="关闭" @click="closeLogin">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <line x1="5" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="1.5" />
            <line x1="19" y1="5" x2="5" y2="19" stroke="currentColor" stroke-width="1.5" />
          </svg>
        </button>

        <p class="login-modal__eyebrow font-body">✦ &nbsp; 旅社柜台</p>
        <h2 id="login-title" class="login-modal__title font-display">
          {{ mode === 'login' ? '登录' : mode === 'register' ? '注册' : '找回密码' }}
        </h2>
        <p class="login-modal__desc font-body">
          {{
            mode === 'login'
              ? '登录后可评论、点赞'
              : mode === 'register'
                ? '注册读者账号（密码至少 8 位）'
                : '输入注册邮箱，将收到重置链接（开发环境见后端控制台）'
          }}
        </p>

        <div v-if="mode !== 'reset'" class="login-modal__tabs">
          <button type="button" class="font-body" :class="{ 'is-active': mode === 'login' }" @click="switchMode('login')">
            登录
          </button>
          <button type="button" class="font-body" :class="{ 'is-active': mode === 'register' }" @click="switchMode('register')">
            注册
          </button>
        </div>

        <form class="login-form" @submit="onSubmit">
          <label v-if="mode === 'register'" class="field">
            <span class="font-body">昵称</span>
            <input v-model="form.displayName" type="text" autocomplete="nickname" placeholder="可选" class="font-body" />
          </label>
          <label class="field">
            <span class="font-body">邮箱</span>
            <input v-model="form.email" type="email" required autocomplete="email" placeholder="your@email.com" class="font-body" />
          </label>
          <label v-if="mode !== 'reset'" class="field">
            <span class="font-body">密码</span>
            <input
              v-model="form.password"
              type="password"
              required
              :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
              :placeholder="mode === 'register' ? '至少 8 位' : '输入密码'"
              class="font-body"
              :minlength="mode === 'register' ? 8 : undefined"
            />
          </label>

          <p v-if="error" class="login-form__error font-body">{{ error }}</p>
          <p v-if="resetMessage" class="login-form__ok font-body">{{ resetMessage }}</p>

          <button type="submit" class="login-form__submit font-body" :disabled="loading">
            <span v-if="loading" class="spinner" />
            {{
              loading
                ? mode === 'login'
                  ? '登录中…'
                  : mode === 'register'
                    ? '注册中…'
                    : '发送中…'
                : mode === 'login'
                  ? '登录'
                  : mode === 'register'
                    ? '注册'
                    : '发送重置链接'
            }}
          </button>
        </form>

        <p v-if="mode === 'login'" class="login-modal__hint font-body">
          <button type="button" class="login-modal__link" @click="switchMode('reset')">忘记密码？</button>
          · 演示账号：demo@example.com / demo1234
        </p>
        <p v-if="mode === 'reset'" class="login-modal__hint font-body">
          <button type="button" class="login-modal__link" @click="switchMode('login')">返回登录</button>
        </p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped lang="less">
.login-mask {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: var(--color-overlay);
}

.login-modal {
  position: relative;
  width: 100%;
  max-width: 26rem;
  padding: 2rem 1.75rem 1.75rem;
  border: 1px solid var(--color-border-strong);
  background: var(--color-modal-bg);
  box-shadow: var(--shadow-modal);
}

.login-modal__close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  color: var(--color-dim);
  transition: color 0.2s;

  &:hover {
    color: var(--color-fg);
  }
}

.login-modal__eyebrow {
  font-size: 0.7rem;
  letter-spacing: 0.3em;
  color: var(--color-secondary);
  opacity: 0.8;
  margin: 0 0 0.75rem;
}

.login-modal__title {
  font-size: 1.5rem;
  letter-spacing: 0.08em;
  color: var(--color-fg);
  margin: 0 0 0.5rem;
}

.login-modal__desc {
  font-size: 0.75rem;
  color: var(--color-dim);
  letter-spacing: 0.04em;
  margin: 0 0 1rem;
  font-weight: 300;
}

.login-modal__tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;

  button {
    flex: 1;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    padding: 0.45rem 0.75rem;
    border: 1px solid var(--color-border);
    color: var(--color-dim);
    transition: all 0.2s;

    &.is-active {
      color: var(--color-primary);
      border-color: rgba(245, 200, 66, 0.4);
      background: rgba(245, 200, 66, 0.08);
    }
  }
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.field {
  display: block;

  span {
    display: block;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: var(--color-dim);
    margin-bottom: 0.45rem;
  }

  input {
    width: 100%;
    background: var(--color-input-bg);
    border: 1px solid var(--color-border);
    color: var(--color-fg);
    font-size: 0.875rem;
    padding: 0.7rem 0.9rem;
    outline: none;
    font-weight: 300;
    transition: border-color 0.2s;

    &::placeholder {
      color: var(--color-faint);
    }

    &:focus {
      border-color: var(--color-border-focus);
    }
  }
}

.login-form__error {
  margin: 0;
  font-size: 0.75rem;
  color: #e57373;
  letter-spacing: 0.04em;
}

.login-form__ok {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-secondary);
  letter-spacing: 0.04em;
}

.login-form__submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  margin-top: 0.35rem;
  padding: 0.8rem 1.25rem;
  border: 1px solid rgba(245, 200, 66, 0.4);
  color: var(--color-primary);
  letter-spacing: 0.18em;
  font-size: 0.85rem;
  transition: all 0.25s;

  &:hover:not(:disabled) {
    background: rgba(245, 200, 66, 0.1);
    border-color: rgba(245, 200, 66, 0.65);
  }

  &:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }
}

.spinner {
  width: 0.75rem;
  height: 0.75rem;
  border: 1px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.login-modal__hint {
  margin: 1.25rem 0 0;
  font-size: 0.65rem;
  color: var(--color-faint);
  letter-spacing: 0.06em;
  text-align: center;
}

.login-modal__link {
  color: var(--color-secondary);
  text-decoration: underline;
  background: none;
  border: none;
  font: inherit;
  cursor: pointer;
}
</style>

