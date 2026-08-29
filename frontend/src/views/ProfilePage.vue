<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import {
  fetchSiteAbout,
  updateSiteAbout,
  uploadAvatar,
  type AboutInfluence,
  type AboutStackItem,
  type AboutStat,
  type AboutTimelineItem,
} from '../api/auth'
import { useAuth } from '../composables/useAuth'
import { useRouter } from '../router'
import MediaCover from '../components/MediaCover.vue'

const { user, isLoggedIn, isStaff, openLogin, saveProfile, updatePassword } = useAuth()
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

const aboutForm = reactive({
  tagline: '',
  quote: '',
  body: '',
  focusTags: '',
  timelineSubtitle: '',
  stackNote: '',
  stats: [] as AboutStat[],
  timeline: [] as AboutTimelineItem[],
  influences: [] as AboutInfluence[],
  techStack: [] as AboutStackItem[],
})

const saving = ref(false)
const aboutSaving = ref(false)
const passwordSaving = ref(false)
const avatarUploading = ref(false)
const message = ref('')
const aboutMessage = ref('')
const passwordMessage = ref('')
const error = ref('')
const aboutError = ref('')
const passwordError = ref('')

function loadAboutIntoForm(data: Awaited<ReturnType<typeof fetchSiteAbout>>) {
  aboutForm.tagline = data.tagline || ''
  aboutForm.quote = data.quote || ''
  aboutForm.body = data.body || ''
  aboutForm.focusTags = (data.focusTags || []).join(', ')
  aboutForm.timelineSubtitle = data.timelineSubtitle || ''
  aboutForm.stackNote = data.stackNote || ''
  aboutForm.stats = (data.stats || []).map((s) => ({ ...s }))
  aboutForm.timeline = (data.timeline || []).map((t) => ({ ...t }))
  aboutForm.influences = (data.influences || []).map((i) => ({ ...i }))
  aboutForm.techStack = (data.techStack || []).map((s) => ({ ...s }))
}

function addStat() {
  aboutForm.stats.push({ value: '', label: '', sub: '' })
}
function removeStat(i: number) {
  aboutForm.stats.splice(i, 1)
}
function addTimeline() {
  aboutForm.timeline.push({ year: '', title: '', desc: '' })
}
function removeTimeline(i: number) {
  aboutForm.timeline.splice(i, 1)
}
function addInfluence() {
  aboutForm.influences.push({ name: '', field: '', quote: '' })
}
function removeInfluence(i: number) {
  aboutForm.influences.splice(i, 1)
}
function addStack() {
  aboutForm.techStack.push({ name: '', type: '' })
}
function removeStack(i: number) {
  aboutForm.techStack.splice(i, 1)
}

onMounted(async () => {
  if (!isLoggedIn.value) {
    openLogin()
    push(paths.home())
    return
  }
  profileForm.displayName = user.value?.displayName ?? ''
  profileForm.bio = user.value?.bio ?? ''
  profileForm.avatar = user.value?.avatar ?? ''
  if (isStaff.value) {
    try {
      loadAboutIntoForm(await fetchSiteAbout())
    } catch {
      /* ignore */
    }
  }
})

async function onAvatarChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  avatarUploading.value = true
  error.value = ''
  message.value = ''
  try {
    const result = await uploadAvatar(file)
    profileForm.avatar = result.path.startsWith('/') ? result.path : result.url
    await saveProfile({
      displayName: profileForm.displayName.trim(),
      bio: profileForm.bio.trim(),
      avatar: profileForm.avatar.trim(),
    })
    message.value = '头像已更新'
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

async function saveAboutForm() {
  aboutSaving.value = true
  aboutMessage.value = ''
  aboutError.value = ''
  try {
    const data = await updateSiteAbout({
      tagline: aboutForm.tagline.trim(),
      quote: aboutForm.quote.trim(),
      body: aboutForm.body.trim(),
      focusTags: aboutForm.focusTags
        .split(/[,，]/)
        .map((t) => t.trim())
        .filter(Boolean),
      timelineSubtitle: aboutForm.timelineSubtitle.trim(),
      stackNote: aboutForm.stackNote.trim(),
      stats: aboutForm.stats
        .map((s) => ({
          value: s.value.trim(),
          label: s.label.trim(),
          sub: s.sub.trim(),
        }))
        .filter((s) => s.value || s.label),
      timeline: aboutForm.timeline
        .map((t) => ({
          year: t.year.trim(),
          title: t.title.trim(),
          desc: t.desc.trim(),
        }))
        .filter((t) => t.year || t.title),
      influences: aboutForm.influences
        .map((i) => ({
          name: i.name.trim(),
          field: i.field.trim(),
          quote: i.quote.trim(),
        }))
        .filter((i) => i.name),
      techStack: aboutForm.techStack
        .map((s) => ({
          name: s.name.trim(),
          type: s.type.trim(),
        }))
        .filter((s) => s.name),
    })
    loadAboutIntoForm(data)
    aboutMessage.value = '关于页已保存'
  } catch (err) {
    aboutError.value = err instanceof Error ? err.message : '保存失败'
  } finally {
    aboutSaving.value = false
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
        <p class="page-desc animate-fade-up-delay-2">
          {{ isStaff ? '管理头像、简介、关于页展示与账号安全' : '管理头像、简介与账号安全' }}
        </p>
      </div>
    </div>

    <div v-if="isLoggedIn" class="container profile__body">
      <section class="profile__card">
        <h2 class="profile__heading font-display">基本信息</h2>
        <p class="profile__meta font-body">角色：{{ roleLabel() }} · {{ user?.email }}</p>

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
            <span class="font-body">侧栏短简介</span>
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
            <input
              v-model="passwordForm.currentPassword"
              type="password"
              autocomplete="current-password"
              class="font-body"
            />
          </label>
          <label class="field">
            <span class="font-body">新密码</span>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              autocomplete="new-password"
              minlength="8"
              class="font-body"
            />
          </label>
          <label class="field">
            <span class="font-body">确认新密码</span>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              autocomplete="new-password"
              minlength="8"
              class="font-body"
            />
          </label>
          <p v-if="passwordMessage" class="profile__ok font-body">{{ passwordMessage }}</p>
          <p v-if="passwordError" class="profile__err font-body">{{ passwordError }}</p>
          <button type="submit" class="profile__btn font-body" :disabled="passwordSaving">
            {{ passwordSaving ? '提交中…' : '更新密码' }}
          </button>
        </form>
      </section>

      <section v-if="isStaff" class="profile__card profile__card--wide">
        <div class="about-edit__head">
          <div>
            <h2 class="profile__heading font-display">关于页展示</h2>
            <p class="profile__meta font-body">按关于页区块填写，空项不会显示在前台。</p>
          </div>
          <button type="button" class="profile__link font-body" @click="push(paths.about())">
            预览关于页 →
          </button>
        </div>

        <form class="about-edit" @submit.prevent="saveAboutForm">
          <div class="about-edit__section">
            <h3 class="about-edit__title font-display">
              <span class="bar" />
              个人简介区
            </h3>
            <div class="about-edit__grid">
              <label class="field">
                <span class="font-body">头衔</span>
                <input
                  v-model="aboutForm.tagline"
                  type="text"
                  maxlength="128"
                  placeholder="Frontend Dev · 语言学习者"
                  class="font-body"
                />
              </label>
              <label class="field">
                <span class="font-body">关注标签</span>
                <input
                  v-model="aboutForm.focusTags"
                  type="text"
                  placeholder="用逗号分隔，如 React, TypeScript"
                  class="font-body"
                />
              </label>
              <label class="field field--full">
                <span class="font-body">引言</span>
                <textarea
                  v-model="aboutForm.quote"
                  rows="3"
                  placeholder="关于页大引号文案，可换行"
                  class="font-body"
                />
              </label>
              <label class="field field--full">
                <span class="font-body">正文</span>
                <textarea
                  v-model="aboutForm.body"
                  rows="7"
                  placeholder="多段内容用空行分隔"
                  class="font-body"
                />
              </label>
            </div>
          </div>

          <div class="about-edit__section">
            <div class="about-edit__title-row">
              <h3 class="about-edit__title font-display">
                <span class="bar" />
                数据卡片
              </h3>
              <button type="button" class="about-edit__add font-body" @click="addStat">+ 添加</button>
            </div>
            <p v-if="!aboutForm.stats.length" class="about-edit__hint font-body">暂无卡片，点击添加</p>
            <div v-for="(s, i) in aboutForm.stats" :key="`stat-${i}`" class="about-edit__row about-edit__row--3">
              <input v-model="s.value" type="text" placeholder="数值" class="font-body" />
              <input v-model="s.label" type="text" placeholder="标签" class="font-body" />
              <input v-model="s.sub" type="text" placeholder="补充" class="font-body" />
              <button type="button" class="about-edit__remove" aria-label="删除" @click="removeStat(i)">×</button>
            </div>
          </div>

          <div class="about-edit__section">
            <div class="about-edit__title-row">
              <h3 class="about-edit__title font-display">
                <span class="bar" />
                学习时间线
              </h3>
              <button type="button" class="about-edit__add font-body" @click="addTimeline">+ 添加</button>
            </div>
            <label class="field about-edit__subtitle">
              <span class="font-body">副标题</span>
              <input
                v-model="aboutForm.timelineSubtitle"
                type="text"
                placeholder="从第一行代码到现在"
                class="font-body"
              />
            </label>
            <p v-if="!aboutForm.timeline.length" class="about-edit__hint font-body">暂无条目，点击添加</p>
            <div
              v-for="(t, i) in aboutForm.timeline"
              :key="`tl-${i}`"
              class="about-edit__block"
            >
              <div class="about-edit__row about-edit__row--2">
                <input v-model="t.year" type="text" placeholder="年份" class="font-body" />
                <input v-model="t.title" type="text" placeholder="标题" class="font-body" />
                <button type="button" class="about-edit__remove" aria-label="删除" @click="removeTimeline(i)">×</button>
              </div>
              <textarea v-model="t.desc" rows="2" placeholder="描述" class="font-body" />
            </div>
          </div>

          <div class="about-edit__cols">
            <div class="about-edit__section">
              <div class="about-edit__title-row">
                <h3 class="about-edit__title font-display">
                  <span class="bar" />
                  影响与资源
                </h3>
                <button type="button" class="about-edit__add font-body" @click="addInfluence">+ 添加</button>
              </div>
              <p v-if="!aboutForm.influences.length" class="about-edit__hint font-body">暂无条目</p>
              <div
                v-for="(inf, i) in aboutForm.influences"
                :key="`inf-${i}`"
                class="about-edit__block"
              >
                <div class="about-edit__row about-edit__row--2">
                  <input v-model="inf.name" type="text" placeholder="名字" class="font-body" />
                  <input v-model="inf.field" type="text" placeholder="领域" class="font-body" />
                  <button type="button" class="about-edit__remove" aria-label="删除" @click="removeInfluence(i)">×</button>
                </div>
                <input v-model="inf.quote" type="text" placeholder="引言" class="font-body" />
              </div>
            </div>

            <div class="about-edit__section">
              <div class="about-edit__title-row">
                <h3 class="about-edit__title font-display">
                  <span class="bar" />
                  工具与技术栈
                </h3>
                <button type="button" class="about-edit__add font-body" @click="addStack">+ 添加</button>
              </div>
              <p v-if="!aboutForm.techStack.length" class="about-edit__hint font-body">暂无条目</p>
              <div
                v-for="(item, i) in aboutForm.techStack"
                :key="`stack-${i}`"
                class="about-edit__row about-edit__row--2"
              >
                <input v-model="item.name" type="text" placeholder="名称" class="font-body" />
                <input v-model="item.type" type="text" placeholder="类型" class="font-body" />
                <button type="button" class="about-edit__remove" aria-label="删除" @click="removeStack(i)">×</button>
              </div>
              <label class="field about-edit__subtitle">
                <span class="font-body">备注</span>
                <textarea v-model="aboutForm.stackNote" rows="3" placeholder="技术栈底部说明" class="font-body" />
              </label>
            </div>
          </div>

          <div class="about-edit__footer">
            <p v-if="aboutMessage" class="profile__ok font-body">{{ aboutMessage }}</p>
            <p v-if="aboutError" class="profile__err font-body">{{ aboutError }}</p>
            <button type="submit" class="profile__btn font-body" :disabled="aboutSaving">
              {{ aboutSaving ? '保存中…' : '保存关于页' }}
            </button>
          </div>
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
  background: var(--color-card);
  box-shadow: var(--shadow-card);
}

.profile__card--wide {
  @media (min-width: 768px) {
    grid-column: 1 / -1;
  }
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

.profile__link {
  flex-shrink: 0;
  padding: 0;
  border: none;
  background: none;
  color: var(--color-secondary);
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  cursor: pointer;

  &:hover {
    color: var(--color-primary);
  }
}

.field {
  display: block;

  > span {
    display: block;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    color: var(--color-dim);
    margin-bottom: 0.4rem;
  }

  input,
  textarea {
    width: 100%;
    box-sizing: border-box;
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

.field--full {
  grid-column: 1 / -1;
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

.about-edit__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;

  .profile__meta {
    margin-bottom: 0;
  }
}

.about-edit {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-top: 1.25rem;
}

.about-edit__section {
  padding-top: 1.5rem;
  border-top: 1px solid rgba(126, 184, 247, 0.1);
}

.about-edit__title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.about-edit__title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1rem;
  font-size: 0.875rem;
  letter-spacing: 0.1em;
  color: var(--color-fg);

  .bar {
    width: 1.25rem;
    height: 1px;
    background: var(--color-secondary);
    opacity: 0.6;
  }
}

.about-edit__title-row .about-edit__title {
  margin-bottom: 0;
}

.about-edit__add {
  padding: 0.35rem 0.75rem;
  border: 1px solid rgba(126, 184, 247, 0.25);
  background: transparent;
  color: var(--color-secondary);
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  cursor: pointer;

  &:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
  }
}

.about-edit__hint {
  margin: 0 0 0.75rem;
  font-size: 0.75rem;
  color: var(--color-quiet);
}

.about-edit__grid {
  display: grid;
  gap: 1rem;

  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
  }
}

.about-edit__cols {
  display: grid;
  gap: 2rem;

  @media (min-width: 900px) {
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }

  .about-edit__section {
    margin: 0;
    padding: 1.25rem;
    border: 1px solid rgba(126, 184, 247, 0.1);
    border-top: 1px solid rgba(126, 184, 247, 0.1);
    background: var(--color-surface-ink);
  }
}

.about-edit__subtitle {
  margin-bottom: 1rem;
}

.about-edit__row {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
  align-items: center;

  input {
    width: 100%;
    box-sizing: border-box;
    background: var(--color-input-bg);
    border: 1px solid var(--color-border);
    color: var(--color-fg);
    font-size: 0.875rem;
    padding: 0.55rem 0.75rem;
    outline: none;

    &:focus {
      border-color: var(--color-border-focus);
    }
  }
}

.about-edit__row--3 {
  grid-template-columns: 1fr 1fr 1fr auto;
}

.about-edit__row--2 {
  grid-template-columns: 1fr 1fr auto;
}

.about-edit__block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.85rem;
  padding: 0.85rem;
  border: 1px solid rgba(126, 184, 247, 0.08);
  background: var(--color-surface-deep);

  .about-edit__row {
    margin-bottom: 0;
  }

  textarea,
  > input {
    width: 100%;
    box-sizing: border-box;
    background: var(--color-input-bg);
    border: 1px solid var(--color-border);
    color: var(--color-fg);
    font-size: 0.875rem;
    padding: 0.55rem 0.75rem;
    outline: none;
    resize: vertical;

    &:focus {
      border-color: var(--color-border-focus);
    }
  }
}

.about-edit__remove {
  width: 2rem;
  height: 2rem;
  border: 1px solid rgba(229, 115, 115, 0.25);
  background: transparent;
  color: #e57373;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;

  &:hover {
    background: rgba(229, 115, 115, 0.1);
  }
}

.about-edit__footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(126, 184, 247, 0.1);
}

@media (max-width: 640px) {
  .about-edit__row--3,
  .about-edit__row--2 {
    grid-template-columns: 1fr;
  }

  .about-edit__remove {
    justify-self: end;
  }
}
</style>
