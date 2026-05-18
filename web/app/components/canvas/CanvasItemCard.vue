<script setup lang="ts">
/** Custom Vue Flow node component. */
import { FileText, MapPinned, Files, StickyNote, Quote } from 'lucide-vue-next'
defineProps<{ data: { label: string; type: string; summary?: string } }>()
const icon = (t: string) =>
  t === 'wiki_page' ? FileText :
  t === 'graph_node' ? MapPinned :
  t === 'source' ? Files :
  t === 'sticky_note' ? StickyNote : Quote
</script>

<template>
  <div class="surface-raised border border-border p-3 min-w-[180px] max-w-[260px]">
    <div class="flex items-center gap-1.5 mb-2 text-[10px] font-mono uppercase tracking-widest text-meta">
      <component :is="icon(data.type)" :size="11" />
      {{ data.type.replace('_', ' ') }}
    </div>
    <div class="text-sm text-fg font-medium truncate">{{ data.label }}</div>
    <p v-if="data.summary" class="text-xs text-muted mt-1 line-clamp-3">{{ data.summary }}</p>
  </div>
</template>
