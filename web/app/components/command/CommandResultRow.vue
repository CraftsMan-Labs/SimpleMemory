<script setup lang="ts">
import { FileText, MapPinned, Layers, Files, Quote } from 'lucide-vue-next'
const props = defineProps<{ title: string; snippet?: string; kind: string; score?: number }>()
const emit = defineEmits<{ click: [] }>()
const iconFor = (k: string) => {
  if (k.startsWith('wiki')) return FileText
  if (k.startsWith('graph')) return MapPinned
  if (k === 'canvas') return Layers
  if (k === 'chunk' || k === 'fact') return Quote
  return Files
}
</script>

<template>
  <button
    class="w-full text-left flex items-start gap-3 px-4 py-3 hover:bg-surface transition-colors"
    @click="emit('click')"
  >
    <component :is="iconFor(kind)" :size="14" class="text-meta mt-0.5 shrink-0" />
    <div class="flex-1 min-w-0">
      <div class="text-sm text-fg truncate">{{ title }}</div>
      <div v-if="snippet" class="text-xs text-muted line-clamp-2 mt-0.5">{{ snippet }}</div>
    </div>
    <div class="flex flex-col items-end gap-1 shrink-0">
      <span class="text-[10px] font-mono uppercase tracking-widest text-meta">{{ kind.replace('_', ' ') }}</span>
      <span v-if="score != null" class="text-[10px] text-meta">{{ score.toFixed(2) }}</span>
    </div>
  </button>
</template>
