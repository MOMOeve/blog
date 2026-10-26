<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const x = ref(-80)
const y = ref(-80)
const visible = ref(false)
const active = ref(false)
const moving = ref(false)
const tilt = ref(-8)
const artworkReady = ref(false)
const artworkSrc = '/img/cursor-character.png'
let targetX = -80
let targetY = -80
let frame = 0
let idleTimer: number | undefined

function move(event: MouseEvent) {
  const dx = event.clientX - targetX
  targetX = event.clientX
  targetY = event.clientY
  if (Math.abs(dx) > 1) tilt.value = Math.max(-16, Math.min(16, dx * 0.45))
  visible.value = true
  moving.value = true
  if (idleTimer) window.clearTimeout(idleTimer)
  idleTimer = window.setTimeout(() => { moving.value = false }, 140)
  const target = event.target as HTMLElement | null
  active.value = Boolean(target?.closest('a, button, [role="button"], input, textarea, select'))
}

function leave() {
  visible.value = false
  moving.value = false
}

function animate() {
  x.value += (targetX - x.value) * 0.22
  y.value += (targetY - y.value) * 0.22
  frame = window.requestAnimationFrame(animate)
}

onMounted(() => {
  const artwork = new Image()
  artwork.onload = () => { artworkReady.value = true }
  artwork.src = artworkSrc
  window.addEventListener('mousemove', move, { passive: true })
  document.documentElement.addEventListener('mouseleave', leave)
  frame = window.requestAnimationFrame(animate)
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', move)
  document.documentElement.removeEventListener('mouseleave', leave)
  window.cancelAnimationFrame(frame)
  if (idleTimer) window.clearTimeout(idleTimer)
})
</script>

<template>
  <div
    class="traveler-cursor"
    :class="{ 'is-visible': visible, 'is-active': active, 'is-moving': moving }"
    :style="{ transform: `translate3d(${x}px, ${y}px, 0)`, '--cursor-tilt': `${tilt}deg` }"
    aria-hidden="true"
  >
    <span class="traveler-cursor__halo" />
    <img v-if="artworkReady" class="traveler-cursor__artwork" :src="artworkSrc" alt="" />
    <span class="traveler-cursor__figure">
      <span class="traveler-cursor__ear traveler-cursor__ear--left" />
      <span class="traveler-cursor__ear traveler-cursor__ear--right" />
      <span class="traveler-cursor__face"><i /><i /></span>
      <span class="traveler-cursor__cloak" />
      <span class="traveler-cursor__tail" />
    </span>
  </div>
</template>

<style scoped lang="less">
.traveler-cursor {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
  width: 1px;
  height: 1px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.traveler-cursor.is-visible { opacity: 1; }

.traveler-cursor__halo {
  position: absolute;
  top: -1rem;
  left: -1rem;
  width: 2rem;
  height: 2rem;
  border: 1px solid color-mix(in srgb, var(--color-secondary) 55%, transparent);
  border-radius: 50%;
  opacity: 0.5;
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
  animation: cursorHalo 3.2s ease-in-out infinite;
}

.traveler-cursor__figure {
  position: absolute;
  top: 0.35rem;
  left: 0.3rem;
  width: 1.1rem;
  height: 1.45rem;
  filter: drop-shadow(0 0.18rem 0.25rem rgba(30, 12, 14, 0.32));
  transform: rotate(var(--cursor-tilt, -8deg));
  transform-origin: 50% 90%;
  transition: transform 0.2s ease-out;
  animation: cursorBob 2.2s ease-in-out infinite;
}

.traveler-cursor__artwork {
  position: absolute;
  top: 0.1rem;
  left: 0.1rem;
  width: 2.25rem;
  height: 2.25rem;
  max-width: none;
  display: block;
  object-fit: contain;
  transform: translate(-0.12rem, -0.12rem) rotate(var(--cursor-tilt, 0deg));
  filter: drop-shadow(0 0.18rem 0.25rem rgba(30, 12, 14, 0.32));
  transform-origin: 50% 90%;
  animation: cursorBob 2.2s ease-in-out infinite;
}

.traveler-cursor:has(.traveler-cursor__artwork) .traveler-cursor__figure { display: none; }

.traveler-cursor__ear {
  position: absolute;
  top: -0.25rem;
  width: 0.42rem;
  height: 0.55rem;
  background: var(--color-secondary);
  clip-path: polygon(50% 0, 100% 100%, 0 100%);
}

.traveler-cursor__ear--left { left: 0.12rem; transform: rotate(-16deg); }
.traveler-cursor__ear--right { right: 0.12rem; transform: rotate(16deg); }

.traveler-cursor__face {
  position: absolute;
  top: 0;
  left: 0.2rem;
  width: 0.7rem;
  height: 0.7rem;
  border-radius: 50%;
  background: #e4b18a;

  i {
    position: absolute;
    top: 0.31rem;
    width: 0.08rem;
    height: 0.08rem;
    border-radius: 50%;
    background: #3a1a1a;
  }

  i:first-child { left: 0.18rem; }
  i:last-child { right: 0.18rem; }
}

.traveler-cursor__cloak {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 1.1rem;
  height: 0.85rem;
  background: var(--color-primary);
  clip-path: polygon(22% 0, 78% 0, 100% 100%, 0 100%);
}

.traveler-cursor__tail {
  position: absolute;
  right: -0.34rem;
  bottom: 0.12rem;
  width: 0.55rem;
  height: 0.42rem;
  border-radius: 50% 60% 45% 55%;
  background: var(--color-secondary);
  transform: rotate(-28deg);
}

.traveler-cursor.is-active .traveler-cursor__halo {
  opacity: 0.9;
  transform: scale(1.35);
}

.traveler-cursor.is-active .traveler-cursor__figure { transform: rotate(4deg) scale(1.08); }

.traveler-cursor.is-active .traveler-cursor__artwork {
  filter: drop-shadow(0 0.2rem 0.3rem rgba(30, 12, 14, 0.4));
  animation-duration: 1.25s;
}

.traveler-cursor.is-moving .traveler-cursor__artwork,
.traveler-cursor.is-moving .traveler-cursor__figure {
  animation-duration: 0.72s;
}

@keyframes cursorBob {
  0%, 100% { translate: 0 0; }
  50% { translate: 0 -0.12rem; }
}

@keyframes cursorHalo {
  0%, 100% { scale: 0.94; opacity: 0.38; }
  50% { scale: 1.04; opacity: 0.58; }
}

@media (hover: none), (pointer: coarse), (prefers-reduced-motion: reduce) {
  .traveler-cursor { display: none; }
}
</style>
