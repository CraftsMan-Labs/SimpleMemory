<script setup lang="ts">
import type { Source } from '@@/types/api'
import { Files, FileText } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'

defineProps<{ source: Source; href: string }>()
</script>

<template>
  <NuxtLink
    :to="href"
    class="flex items-center gap-3 px-4 py-3 hover:bg-surface transition-colors border-b border-border-soft"
  >
    <component :is="source.source_type === 'pdf' ? FileText : Files" :size="14" class="text-meta shrink-0" />
    <div class="flex-1 min-w-0">
      <div class="text-sm text-fg truncate">{{ source.title }}</div>
      <div class="text-xs text-meta font-mono uppercase tracking-widest">{{ source.source_type }}</div>
    </div>
    <Badge
      :variant="source.status === 'completed' ? 'success' : source.status === 'failed' ? 'danger' : 'default'"
    >
      <span v-if="source.status === 'running' || source.status === 'pending'" class="pulse-dot" />
      {{ source.status }}
    </Badge>
  </NuxtLink>
</template>
