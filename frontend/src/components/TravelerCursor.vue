<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const x = ref(-80)
const y = ref(-80)
const visible = ref(false)
const active = ref(false)

function move(event: MouseEvent) {
  x.value = event.clientX
  y.value = event.clientY
  visible.value = true
  const target = event.target as HTMLElement | null
  active.value = Boolean(target?.closest('a, button, [role="button"], input, textarea, select'))
}

function leave() {
  visible.value = false
}

onMounted(() => {
  window.addEventListener('mousemove', move, { passive: true })
  document.documentElement.addEventListener('mouseleave', leave)
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', move)
  document.documentElement.removeEventListener('mouseleave', leave)
})
</script>

<template>
  <div
    class="traveler-cursor"
    :class="{ 'is-visible': visible, 'is-active': active }"
    :style="{ transform: `translate3d(${x}px, ${y}px, 0)` }"
    aria-hidden="true"
  >
    <span class="traveler-cursor__halo" />
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
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.traveler-cursor__figure {
  position: absolute;
  top: 0.35rem;
  left: 0.3rem;
  width: 1.1rem;
  height: 1.45rem;
  filter: drop-shadow(0 0.18rem 0.25rem rgba(30, 12, 14, 0.32));
  transform: rotate(-8deg);
  transition: transform 0.25s ease;
}

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

@media (hover: none), (pointer: coarse), (prefers-reduced-motion: reduce) {
  .traveler-cursor { display: none; }
}
</style>
