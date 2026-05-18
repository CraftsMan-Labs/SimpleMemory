<script setup lang="ts">
import { cn } from '@/lib/utils'
defineProps<{ class?: string; padded?: boolean; raised?: boolean }>()
</script>

<template>
  <div
    :class="cn(
      'bg-surface border border-border rounded-md',
      raised && 'shadow-[var(--elev-raised)]',
      padded && 'p-6',
      $props.class,
    )"
  >
    <slot />
  </div>
</template>
