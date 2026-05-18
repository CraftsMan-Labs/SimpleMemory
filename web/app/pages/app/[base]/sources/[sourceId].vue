<script setup lang="ts">
import { computed } from 'vue'
import Card from '@/components/ui/Card.vue'
import SourceJobTimeline from '@/components/sources/SourceJobTimeline.vue'
import { useSource, useSourceVersions, useSourceJobs } from '@/composables/useSourceIngest'

definePageMeta({ layout: 'app' })

const route = useRoute()
const sourceId = computed(() => route.params.sourceId as string)

const { data: src } = useSource(sourceId.value)
const { data: versions } = useSourceVersions(sourceId.value)
const { data: jobs } = useSourceJobs(sourceId.value)
</script>

<template>
  <div class="max-w-3xl mx-auto px-8 py-12 pb-24">
    <header class="mb-8">
      <p class="font-mono text-xs uppercase tracking-widest text-meta mb-2">Source · {{ src?.source_type }}</p>
      <h1 class="text-2xl text-fg">{{ src?.title }}</h1>
    </header>

    <SourceJobTimeline v-if="jobs?.length" :jobs="jobs" class="mb-8" />

    <h2 class="text-fg text-lg mb-3">Versions</h2>
    <Card padded class="p-0">
      <ul>
        <li v-for="v in versions ?? []" :key="v.id" class="px-4 py-3 border-b border-border-soft last:border-b-0">
          <div class="flex items-center justify-between text-sm">
            <span class="text-fg">{{ v.parser_version ?? 'unparsed' }}</span>
            <span class="text-meta text-xs">{{ new Date(v.created_at).toLocaleString() }}</span>
          </div>
          <p class="text-xs font-mono text-meta mt-1 truncate">{{ v.raw_object_key }}</p>
        </li>
      </ul>
    </Card>
  </div>
</template>
