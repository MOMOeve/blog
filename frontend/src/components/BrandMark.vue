<script setup lang="ts">
withDefaults(
  defineProps<{
    size?: number
  }>(),
  { size: 28 },
)
</script>

<template>
  <img
    class="brand-mark"
    src="/img/log.png"
    alt=""
    :width="size"
    :height="size"
    decoding="async"
  />
</template>

<style scoped>
.brand-mark {
  display: block;
  flex-shrink: 0;
  width: v-bind('size + "px"');
  height: v-bind('size + "px"');
  object-fit: cover;
  border-radius: 4px;
}
</style>
