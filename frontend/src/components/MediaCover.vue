<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    src?: string | null
    alt?: string
    /** 占位时显示的短标题 */
    label?: string
    /** 用于稳定取色，缺省用 label/alt */
    seed?: string | number
  }>(),
  {
    src: '',
    alt: '',
    label: '',
  },
)

const failed = ref(false)

watch(
  () => props.src,
  () => {
    failed.value = false
  },
)

const showImage = computed(() => Boolean(props.src?.trim()) && !failed.value)

const PALETTE = [
  ['#0a1628', '#1a3a5c', '#7eb8f7'],
  ['#1a0f08', '#8b4513', '#f5c842'],
  ['#12101a', '#3d2a4a', '#c4a0d8'],
  ['#0d0818', '#2a1840', '#ff6b9d'],
  ['#060a14', '#1a2840', '#4a90d9'],
  ['#101820', '#3a4a58', '#a8b8c8'],
  ['#1a0a08', '#c45c20', '#f5c842'],
  ['#080610', '#1a0a28', '#00e5ff'],
  ['#0a1520', '#2a4a6a', '#e8f0f8'],
] as const

function hashSeed(value: string): number {
  let h = 0
  for (let i = 0; i < value.length; i += 1) {
    h = (h * 31 + value.charCodeAt(i)) >>> 0
  }
  return h
}

const colors = computed(() => {
  const key = String(props.seed ?? props.label ?? props.alt ?? 'cover')
  return PALETTE[hashSeed(key) % PALETTE.length]
})

const placeholderStyle = computed(() => {
  const [c0, c1, c2] = colors.value
  return {
    background: `linear-gradient(135deg, ${c0} 0%, ${c1} 55%, ${c2} 100%)`,
  }
})

const displayLabel = computed(() => (props.label || props.alt || '').slice(0, 16))

function onError() {
  failed.value = true
}
</script>

<template>
  <div class="media-cover">
    <img v-if="showImage" :src="src!" :alt="alt" class="media-cover__img" @error="onError" />
    <div v-else class="media-cover__ph" :style="placeholderStyle" role="img" :aria-label="alt || label || '图片占位'">
      <span v-if="displayLabel" class="media-cover__label font-display">{{ displayLabel }}</span>
    </div>
  </div>
</template>

<style scoped lang="less">
.media-cover {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.media-cover__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.media-cover__ph {
  width: 100%;
  height: 100%;
  min-height: 6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    width: 28%;
    aspect-ratio: 1;
    border-radius: 50%;
    right: 12%;
    top: 14%;
    background: rgba(240, 244, 255, 0.18);
    pointer-events: none;
  }
}

.media-cover__label {
  position: relative;
  z-index: 1;
  max-width: 80%;
  text-align: center;
  font-size: clamp(0.85rem, 2.2vw, 1.15rem);
  letter-spacing: 0.12em;
  color: rgba(240, 244, 255, 0.92);
  line-height: 1.4;
}
</style>
