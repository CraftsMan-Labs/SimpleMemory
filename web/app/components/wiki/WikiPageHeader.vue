<script setup lang="ts">
import WikiFreshnessBadge from './WikiFreshnessBadge.vue'
import Button from '@/components/ui/Button.vue'
import Tabs from '@/components/ui/Tabs.vue'
import type { WikiPage } from '@@/types/api'
import { Sparkles } from 'lucide-vue-next'

defineProps<{ page: WikiPage; mode: 'read' | 'edit' }>()
const emit = defineEmits<{ 'update:mode': [m: 'read' | 'edit']; regenerate: [] }>()
</script>

<template>
  <header class="mb-8 pb-6 border-b border-border">
    <div class="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-meta mb-3">
      <span>{{ page.page_type }}</span>
      <span>·</span>
      <span>{{ page.source_count }} sources</span>
      <span>·</span>
      <span>{{ page.chunk_count }} chunks</span>
      <span>·</span>
      <span>{{ page.graph_node_count }} nodes</span>
      <WikiFreshnessBadge :status="page.freshness_status" class="ml-2" />
    </div>
    <div class="flex items-start justify-between gap-4">
      <h1 class="text-display text-fg" style="font-size: clamp(2rem, 4vw, 3rem); line-height: 1.05;">
        {{ page.title }}
      </h1>
      <div class="flex items-center gap-2 shrink-0">
        <Tabs
          :model-value="mode"
          :items="[{ value: 'read', label: 'Read' }, { value: 'edit', label: 'Edit' }]"
          @update:model-value="(v) => emit('update:mode', v as any)"
        />
        <Button
          v-if="page.freshness_status !== 'fresh'"
          variant="outline"
          size="sm"
          @click="emit('regenerate')"
        >
          <Sparkles :size="12" /> Regenerate
        </Button>
      </div>
    </div>
  </header>
</template>
