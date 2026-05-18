<script setup lang="ts">
/**
 * "Related" uses semantic search seeded by the page's title to surface neighbours.
 * Hits POST /v1/search via the proxy. Falls back to the search composable shape.
 */
import { ref, watchEffect } from 'vue'
import { Compass } from 'lucide-vue-next'
import { useSearch } from '@/composables/useSearch'
import { useWikiPageBySlug } from '@/composables/useWikiPage'
import { useRoute } from 'vue-router'

const props = defineProps<{ pageId: string }>()
const route = useRoute()
const { data: page } = useWikiPageBySlug(() => route.params.slug as string)

const search = useSearch()
const ran = ref(false)

watchEffect(() => {
  if (!ran.value && page.value?.title) {
    ran.value = true
    search.mutate({ query: page.value.title, scope: 'current_project', limit: 6, record_types: ['wiki_page', 'graph_node'] })
  }
})

void props.pageId
</script>

<template>
  <section>
    <h3 class="text-xs font-mono uppercase tracking-widest text-meta mb-2 flex items-center gap-1.5">
      <Compass :size="11" /> Related
    </h3>
    <ul v-if="(search.data.value?.results.length ?? 0) > 0" class="space-y-2">
      <li v-for="r in search.data.value?.results" :key="r.id" class="text-sm">
        <p class="text-fg-2 hover:text-fg cursor-pointer truncate">{{ r.title ?? r.id }}</p>
        <p v-if="r.snippet" class="text-xs text-muted line-clamp-2">{{ r.snippet }}</p>
      </li>
    </ul>
    <p v-else class="text-xs text-meta italic">No related results.</p>
  </section>
</template>
