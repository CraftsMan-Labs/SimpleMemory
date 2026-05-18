<script setup lang="ts">
/**
 * Visualises the ingestion state machine from the v3 PDF §9.
 * Stages light up as the job progresses; the active stage pulses.
 */
import { computed } from 'vue'
import type { JobStatus } from '@@/types/api'

const props = defineProps<{ jobs: JobStatus[] }>()

const STAGES: Array<{ key: string; label: string }> = [
  { key: 'parsing', label: 'Parse' },
  { key: 'chunking', label: 'Chunk' },
  { key: 'chunk_embedding', label: 'Embed' },
  { key: 'wiki_generation', label: 'Wiki' },
  { key: 'wiki_internal_linking', label: 'Link' },
  { key: 'graph_node_creation', label: 'Graph' },
  { key: 'vector_sync', label: 'Sync' },
  { key: 'completed', label: 'Done' },
]

const latest = computed(() => props.jobs[0])
const stageIdx = computed(() => {
  const s = latest.value?.stage ?? ''
  const idx = STAGES.findIndex((x) => x.key === s)
  return idx === -1 ? (latest.value?.status === 'completed' ? STAGES.length - 1 : 0) : idx
})
</script>

<template>
  <div v-if="latest" class="surface-card p-4">
    <div class="flex items-center justify-between mb-3">
      <span class="text-xs font-mono uppercase tracking-widest text-meta">Ingestion</span>
      <span class="text-xs text-fg-2">{{ latest.status }}</span>
    </div>
    <ol class="flex items-center gap-2 overflow-x-auto">
      <li
        v-for="(s, i) in STAGES"
        :key="s.key"
        class="flex items-center gap-2 shrink-0"
      >
        <span
          :class="[
            'h-2 w-2 rounded-pill',
            i < stageIdx ? 'bg-accent'
              : i === stageIdx ? 'bg-accent animate-pulse'
              : 'bg-border',
          ]"
        />
        <span :class="['text-xs', i <= stageIdx ? 'text-fg' : 'text-meta']">{{ s.label }}</span>
        <span v-if="i < STAGES.length - 1" class="text-meta">·</span>
      </li>
    </ol>
    <div v-if="latest.error" class="mt-3 text-xs text-[var(--danger)]">{{ latest.error }}</div>
  </div>
</template>
