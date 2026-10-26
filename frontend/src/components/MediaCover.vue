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
  ['#211316', '#4b2728', '#9a6d50'],
  ['#281714', '#5a3323', '#ae8655'],
  ['#1e171c', '#44303e', '#987b82'],
  ['#24161d', '#4a2938', '#95606b'],
  ['#19171a', '#343039', '#806c67'],
  ['#21191a', '#493337', '#a18478'],
  ['#291816', '#633c2d', '#b18c5d'],
  ['#1c151b', '#3d2835', '#866b76'],
  ['#21181a', '#4a302b', '#a0785d'],
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
    background: rgba(244, 220, 188, 0.09);
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
  color: rgba(247, 232, 220, 0.76);
  line-height: 1.4;
}
</style>
