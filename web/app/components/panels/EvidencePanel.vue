<script setup lang="ts">
/**
 * Evidence panel. Lists every WikiEvidence for the page; each row reveals the
 * grounding chunk on click (fetched from /v1/chunks/{id}).
 * The wiki reader emits open-evidence with a 1-based index; we honour it by
 * selecting the matching row.
 */
import { computed, ref, watch } from 'vue'
import { Quote, ChevronRight, ChevronDown } from 'lucide-vue-next'
import { useWikiEvidence, useChunk } from '@/composables/useEvidence'

const props = defineProps<{ pageId: string; openIndex?: number | null }>()

const { data, isLoading } = useWikiEvidence(() => props.pageId)
const expandedId = ref<string | null>(null)

const chunkId = computed(() => {
  const e = data.value?.find((x) => x.id === expandedId.value)
  return e?.chunk_id ?? null
})
const { data: chunk } = useChunk(chunkId)

watch(
  () => props.openIndex,
  (idx) => {
    if (idx == null) return
    const row = data.value?.[idx - 1]
    if (row) expandedId.value = row.id
  },
)

const toggle = (id: string) => {
  expandedId.value = expandedId.value === id ? null : id
}
</script>

<template>
  <section>
    <h3 class="text-xs font-mono uppercase tracking-widest text-meta mb-2 flex items-center gap-1.5">
      <Quote :size="11" /> Evidence
    </h3>
    <div v-if="isLoading" class="text-xs text-meta">Loading…</div>
    <ul v-else-if="data?.length" class="space-y-1">
      <li v-for="(e, idx) in data" :key="e.id" class="text-sm">
        <button
          class="flex items-start gap-2 w-full text-left p-2 rounded hover:bg-surface transition-colors"
          @click="toggle(e.id)"
        >
          <component
            :is="expandedId === e.id ? ChevronDown : ChevronRight"
            :size="12"
            class="text-meta mt-0.5 shrink-0"
          />
          <span class="text-[10px] font-mono text-meta mt-0.5">[{{ idx + 1 }}]</span>
          <div class="flex-1 min-w-0">
            <p class="text-fg-2 line-clamp-2">{{ e.quote || 'Untitled evidence' }}</p>
            <p class="text-[10px] text-meta font-mono mt-0.5">
              {{ e.evidence_role }} · conf {{ e.confidence.toFixed(2) }}
            </p>
          </div>
        </button>
        <div v-if="expandedId === e.id && chunk" class="mt-1 ml-6 p-3 surface-card text-xs">
          <p class="text-[10px] font-mono uppercase tracking-widest text-meta mb-1">
            chunk · #{{ chunk.chunk_index }}
          </p>
          <p class="text-fg-2 whitespace-pre-wrap leading-relaxed">{{ chunk.text }}</p>
        </div>
      </li>
    </ul>
    <p v-else class="text-xs text-meta italic">No evidence yet for this page.</p>
  </section>
</template>
