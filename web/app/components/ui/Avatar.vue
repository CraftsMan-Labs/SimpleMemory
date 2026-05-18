<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'
const props = defineProps<{ name?: string; src?: string; class?: string; size?: 'sm' | 'md' | 'lg' }>()
const initials = computed(() => {
  if (!props.name) return '?'
  return props.name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join('')
})
const sizes = { sm: 'h-6 w-6 text-[10px]', md: 'h-8 w-8 text-xs', lg: 'h-10 w-10 text-sm' }
</script>

<template>
  <span
    :class="cn(
      'inline-flex items-center justify-center rounded-pill bg-surface text-fg font-mono uppercase border border-border',
      sizes[size ?? 'md'],
      $props.class,
    )"
  >
    <img v-if="src" :src="src" :alt="name ?? ''" class="h-full w-full object-cover rounded-pill" />
    <span v-else>{{ initials }}</span>
  </span>
</template>
