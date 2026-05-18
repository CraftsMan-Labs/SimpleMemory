<script setup lang="ts">
import Toast from '@/components/ui/Toast.vue'
</script>

<template>
  <div data-skin="framer" class="min-h-screen bg-bg text-fg">
    <slot />
    <Toast />
  </div>
</template>
