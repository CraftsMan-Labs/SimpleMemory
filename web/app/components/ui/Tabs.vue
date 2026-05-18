<script setup lang="ts">
import { cn } from '@/lib/utils'
const props = defineProps<{ modelValue: string; items: Array<{ value: string; label: string }>; class?: string }>()
const emit = defineEmits<{ 'update:modelValue': [v: string] }>()
const select = (v: string) => emit('update:modelValue', v)
</script>

<template>
  <div :class="cn('inline-flex items-center gap-1 p-1 border border-border rounded-pill bg-surface', $props.class)">
    <button
      v-for="item in items"
      :key="item.value"
      type="button"
      :class="cn(
        'h-8 px-3 rounded-pill text-xs font-medium transition-colors',
        item.value === modelValue ? 'bg-fg text-bg' : 'text-muted hover:text-fg',
      )"
      @click="select(item.value)"
    >
      {{ item.label }}
    </button>
  </div>
</template>
