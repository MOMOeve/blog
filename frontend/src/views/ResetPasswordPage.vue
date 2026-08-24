<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { confirmPasswordReset } from '../api/auth'
import { useRouter } from '../router'

const { push, paths } = useRouter()

const form = reactive({
  newPassword: '',
  confirmPassword: '',
})

const token = ref('')
const loading = ref(false)
const message = ref('')
const error = ref('')

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  token.value = params.get('token') ?? ''
  if (!token.value) {
    error.value = '链接无效，请重新申请重置密码'
  }
})

async function onSubmit() {
  if (!token.value) return
  if (form.newPassword !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }
  loading.value = true
  message.value = ''
  error.value = ''
  try {
    const result = await confirmPasswordReset(token.value, form.newPassword)
    message.value = result.detail
    setTimeout(() => push(paths.home()), 2000)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '重置失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page-shell reset">
    <div class="page-header">
      <div class="page-header__glow" />
      <div class="page-header__line" />
      <div class="page-header__inner">
        <p class="page-eyebrow animate-fade-up">✦ &nbsp; RESET</p>
        <h1 class="page-title animate-fade-up-delay-1">重置密码</h1>
        <p class="page-desc animate-fade-up-delay-2">设置新密码后即可登录</p>
      </div>
    </div>

    <div class="container reset__body">
      <form class="reset__card" @submit.prevent="onSubmit">
        <label class="field">
          <span class="font-body">新密码</span>
          <input v-model="form.newPassword" type="password" minlength="8" required autocomplete="new-password" class="font-body" />
        </label>
        <label class="field">
          <span class="font-body">确认新密码</span>
          <input v-model="form.confirmPassword" type="password" minlength="8" required autocomplete="new-password" class="font-body" />
        </label>
        <p v-if="message" class="reset__ok font-body">{{ message }}</p>
        <p v-if="error" class="reset__err font-body">{{ error }}</p>
        <button type="submit" class="reset__btn font-body" :disabled="loading || !token">
          {{ loading ? '提交中…' : '确认重置' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped lang="less">
.reset__body {
  padding-bottom: 4rem;
  max-width: 28rem;
}

.reset__card {
  padding: 1.75rem;
  border: 1px solid var(--color-border);
  background: rgba(126, 184, 247, 0.03);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: block;

  span {
    display: block;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    color: var(--color-dim);
    margin-bottom: 0.4rem;
  }

  input {
    width: 100%;
    background: var(--color-input-bg);
    border: 1px solid var(--color-border);
    color: var(--color-fg);
    font-size: 0.875rem;
    padding: 0.65rem 0.85rem;
    outline: none;

    &:focus {
      border-color: var(--color-border-focus);
    }
  }
}

.reset__btn {
  margin-top: 0.25rem;
  padding: 0.65rem 1.25rem;
  border: 1px solid rgba(245, 200, 66, 0.35);
  color: var(--color-primary);
  font-size: 0.75rem;
  letter-spacing: 0.14em;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.reset__ok {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-secondary);
}

.reset__err {
  margin: 0;
  font-size: 0.75rem;
  color: #e57373;
}
</style>
