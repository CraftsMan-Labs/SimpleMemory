<script setup lang="ts">
import { useWikiBacklinks } from '@/composables/useWikiPage'
import { Link2 } from 'lucide-vue-next'
const props = defineProps<{ pageId: string }>()
const { data, isLoading } = useWikiBacklinks(() => props.pageId)
</script>

<template>
  <section>
    <h3 class="text-xs font-mono uppercase tracking-widest text-meta mb-2 flex items-center gap-1.5">
      <Link2 :size="11" /> Backlinks
    </h3>
    <div v-if="isLoading" class="text-xs text-meta">…</div>
    <ul v-else-if="data?.length" class="space-y-2">
      <li v-for="b in data" :key="b.id" class="text-sm">
        <p class="text-fg-2 hover:text-fg cursor-pointer">{{ b.context_snippet || 'Untitled context' }}</p>
      </li>
    </ul>
    <p v-else class="text-xs text-meta italic">No pages link here yet.</p>
  </section>
</template>
