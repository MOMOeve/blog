<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { uploadAvatar } from '../api/auth'
import { useAuth } from '../composables/useAuth'
import { useRouter } from '../router'
import MediaCover from '../components/MediaCover.vue'

const { user, isLoggedIn, openLogin, saveProfile, updatePassword } = useAuth()
const { push, paths } = useRouter()

const profileForm = reactive({
  displayName: '',
  bio: '',
  avatar: '',
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const saving = ref(false)
const passwordSaving = ref(false)
const avatarUploading = ref(false)
const message = ref('')
const passwordMessage = ref('')
const error = ref('')
const passwordError = ref('')

onMounted(() => {
  if (!isLoggedIn.value) {
    openLogin()
    push(paths.home())
    return
  }
  profileForm.displayName = user.value?.displayName ?? ''
  profileForm.bio = user.value?.bio ?? ''
  profileForm.avatar = user.value?.avatar ?? ''
})

async function onAvatarChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  avatarUploading.value = true
  error.value = ''
  try {
    const result = await uploadAvatar(file)
    profileForm.avatar = result.path.startsWith('/') ? result.path : result.url
  } catch (err) {
    error.value = err instanceof Error ? err.message : '头像上传失败'
  } finally {
    avatarUploading.value = false
    input.value = ''
  }
}

async function saveProfileForm() {
  saving.value = true
  message.value = ''
  error.value = ''
  try {
    await saveProfile({
      displayName: profileForm.displayName.trim(),
      bio: profileForm.bio.trim(),
      avatar: profileForm.avatar.trim(),
    })
    message.value = '资料已保存'
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败'
  } finally {
    saving.value = false
  }
}

async function savePasswordForm() {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  passwordSaving.value = true
  passwordMessage.value = ''
  passwordError.value = ''
  try {
    const result = await updatePassword({
      currentPassword: passwordForm.currentPassword,
      newPassword: passwordForm.newPassword,
    })
    passwordMessage.value = result.detail
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (err) {
    passwordError.value = err instanceof Error ? err.message : '修改失败'
  } finally {
    passwordSaving.value = false
  }
}

const roleLabel = () => {
  const role = user.value?.role
  if (role === 'staff') return '管理员'
  if (role === 'author') return '作者'
  return '读者'
}
</script>

<template>
  <div class="page-shell profile">
    <div class="page-header">
      <div class="page-header__glow" />
      <div class="page-header__line" />
      <div class="page-header__inner">
        <p class="page-eyebrow animate-fade-up">✦ &nbsp; PROFILE</p>
        <h1 class="page-title animate-fade-up-delay-1">个人资料</h1>
        <p class="page-desc animate-fade-up-delay-2">管理头像、简介与账号安全</p>
      </div>
    </div>

    <div v-if="isLoggedIn" class="container profile__body">
      <section class="profile__card">
        <h2 class="profile__heading font-display">基本信息</h2>
        <p class="profile__meta font-body">
          角色：{{ roleLabel() }} · {{ user?.email }}
        </p>

        <div class="profile__avatar-row">
          <div class="profile__avatar">
            <MediaCover
              v-if="profileForm.avatar"
              :src="profileForm.avatar"
              alt="头像"
              label="头像"
            />
            <div v-else class="profile__avatar-ph font-display">
              {{ (profileForm.displayName || user?.displayName || '?').slice(0, 1) }}
            </div>
          </div>
          <label class="profile__upload font-body">
            <input type="file" accept="image/*" :disabled="avatarUploading" @change="onAvatarChange" />
            {{ avatarUploading ? '上传中…' : '更换头像' }}
          </label>
        </div>

        <form class="profile__form" @submit.prevent="saveProfileForm">
          <label class="field">
            <span class="font-body">昵称</span>
            <input v-model="profileForm.displayName" type="text" maxlength="64" class="font-body" />
          </label>
          <label class="field">
            <span class="font-body">简介</span>
            <textarea v-model="profileForm.bio" rows="4" maxlength="500" class="font-body" />
          </label>
          <p v-if="message" class="profile__ok font-body">{{ message }}</p>
          <p v-if="error" class="profile__err font-body">{{ error }}</p>
          <button type="submit" class="profile__btn font-body" :disabled="saving">
            {{ saving ? '保存中…' : '保存资料' }}
          </button>
        </form>
      </section>

      <section class="profile__card">
        <h2 class="profile__heading font-display">修改密码</h2>
        <form class="profile__form" @submit.prevent="savePasswordForm">
          <label class="field">
            <span class="font-body">当前密码</span>
            <input v-model="passwordForm.currentPassword" type="password" autocomplete="current-password" class="font-body" />
          </label>
          <label class="field">
            <span class="font-body">新密码</span>
            <input v-model="passwordForm.newPassword" type="password" autocomplete="new-password" minlength="8" class="font-body" />
          </label>
          <label class="field">
            <span class="font-body">确认新密码</span>
            <input v-model="passwordForm.confirmPassword" type="password" autocomplete="new-password" minlength="8" class="font-body" />
          </label>
          <p v-if="passwordMessage" class="profile__ok font-body">{{ passwordMessage }}</p>
          <p v-if="passwordError" class="profile__err font-body">{{ passwordError }}</p>
          <button type="submit" class="profile__btn font-body" :disabled="passwordSaving">
            {{ passwordSaving ? '提交中…' : '更新密码' }}
          </button>
        </form>
      </section>
    </div>
  </div>
</template>

<style scoped lang="less">
.profile__body {
  display: grid;
  gap: 2rem;
  padding-bottom: 4rem;

  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
}

.profile__card {
  padding: 1.75rem;
  border: 1px solid var(--color-border);
  background: rgba(126, 184, 247, 0.03);
}

.profile__heading {
  font-size: 1rem;
  letter-spacing: 0.12em;
  color: var(--color-fg);
  margin: 0 0 0.5rem;
}

.profile__meta {
  margin: 0 0 1.5rem;
  font-size: 0.75rem;
  color: var(--color-dim);
  letter-spacing: 0.05em;
}

.profile__avatar-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.profile__avatar {
  width: 5rem;
  height: 5rem;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid rgba(126, 184, 247, 0.2);
}

.profile__avatar-ph {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(245, 200, 66, 0.12);
  color: var(--color-primary);
  font-size: 1.5rem;
}

.profile__upload {
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  color: var(--color-secondary);
  cursor: pointer;

  input {
    display: none;
  }
}

.profile__form {
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

  input,
  textarea {
    width: 100%;
    background: var(--color-input-bg);
    border: 1px solid var(--color-border);
    color: var(--color-fg);
    font-size: 0.875rem;
    padding: 0.65rem 0.85rem;
    outline: none;
    resize: vertical;

    &:focus {
      border-color: var(--color-border-focus);
    }
  }
}

.profile__btn {
  align-self: flex-start;
  margin-top: 0.25rem;
  padding: 0.65rem 1.25rem;
  border: 1px solid rgba(245, 200, 66, 0.35);
  color: var(--color-primary);
  font-size: 0.75rem;
  letter-spacing: 0.14em;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    background: rgba(245, 200, 66, 0.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.profile__ok {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-secondary);
}

.profile__err {
  margin: 0;
  font-size: 0.75rem;
  color: #e57373;
}
</style>
