<script setup lang="ts">
import { cn } from '@/lib/utils'
defineProps<{ class?: string }>()
const model = defineModel<string>()
</script>

<template>
  <input
    v-model="model"
    v-bind="$attrs"
    :class="cn(
      'h-10 w-full bg-surface text-fg placeholder:text-meta border border-border rounded-pill px-4 text-sm transition-shadow',
      'focus:outline-none focus:border-accent',
      $props.class,
    )"
  />
</template>
