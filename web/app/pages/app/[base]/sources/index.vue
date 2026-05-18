<script setup lang="ts">
import { ref } from 'vue'
import SourceDropZone from '@/components/sources/SourceDropZone.vue'
import SourceRow from '@/components/sources/SourceRow.vue'
import Card from '@/components/ui/Card.vue'
import { useSourceList } from '@/composables/useSourceIngest'
import { useProjectBase } from '@/composables/useProjectBase'

definePageMeta({ layout: 'app' })

const { data, isLoading } = useSourceList()
const { current } = useProjectBase()
const lastJobId = ref<string | null>(null)
</script>

<template>
  <div class="max-w-3xl mx-auto px-8 py-12 pb-24">
    <header class="mb-8">
      <p class="font-mono text-xs uppercase tracking-widest text-accent mb-2">Sources</p>
      <h1 class="text-display text-fg text-3xl">What is your vault built from.</h1>
      <p class="text-muted mt-2">Drop a file or paste a URL — KMG parses, chunks, embeds, and generates wiki pages automatically.</p>
    </header>

    <SourceDropZone class="mb-12" @ingested="(id) => (lastJobId = id)" />

    <Card padded class="overflow-hidden p-0">
      <div v-if="isLoading" class="p-6 text-meta">Loading…</div>
      <div v-else-if="!data?.sources.length" class="p-12 text-center text-muted text-sm">
        No sources yet.
      </div>
      <div v-else>
        <SourceRow
          v-for="s in data.sources"
          :key="s.id"
          :source="s"
          :href="`/app/${current?.slug}/sources/${s.id}`"
        />
      </div>
    </Card>
  </div>
</template>
