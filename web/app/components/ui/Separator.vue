<script setup lang="ts">
import { cn } from '@/lib/utils'
defineProps<{ class?: string; orientation?: 'horizontal' | 'vertical' }>()
</script>

<template>
  <div
    :class="cn(
      orientation === 'vertical' ? 'w-px h-full' : 'h-px w-full',
      'bg-border',
      $props.class,
    )"
    role="separator"
  />
</template>
