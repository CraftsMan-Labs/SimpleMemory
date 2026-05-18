<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'
const props = defineProps<{ variant?: 'default' | 'accent' | 'warn' | 'danger' | 'success'; class?: string }>()
const variantClass = computed(() => {
  switch (props.variant) {
    case 'accent': return 'bg-accent text-accent-on'
    case 'warn': return 'border border-[var(--warn)] text-[var(--warn)]'
    case 'danger': return 'border border-[var(--danger)] text-[var(--danger)]'
    case 'success': return 'border border-[var(--success)] text-[var(--success)]'
    default: return 'border border-border text-fg-2'
  }
})
</script>

<template>
  <span :class="cn('inline-flex items-center gap-1 rounded-pill px-2.5 py-0.5 text-xs font-medium', variantClass, $props.class)">
    <slot />
  </span>
</template>
