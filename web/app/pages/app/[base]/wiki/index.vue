<script setup lang="ts">
import { computed } from 'vue'
import Card from '@/components/ui/Card.vue'
import WikiFreshnessBadge from '@/components/wiki/WikiFreshnessBadge.vue'
import { useWikiList } from '@/composables/useWikiList'
import { useProjectBase } from '@/composables/useProjectBase'

definePageMeta({ layout: 'app' })

const { current } = useProjectBase()
const { data } = useWikiList()
const pages = computed(() => data.value?.pages ?? [])
</script>

<template>
  <div class="max-w-4xl mx-auto px-8 py-12 pb-24">
    <header class="mb-8">
      <p class="font-mono text-xs uppercase tracking-widest text-accent mb-2">Wiki</p>
      <h1 class="text-display text-fg text-3xl">{{ data?.total ?? 0 }} pages.</h1>
    </header>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <NuxtLink v-for="p in pages" :key="p.id" :to="`/app/${current?.slug}/wiki/${p.slug}`">
        <Card padded class="hover:border-accent transition-colors h-full">
          <div class="flex items-center justify-between mb-2">
            <span class="font-mono text-[10px] uppercase tracking-widest text-meta">{{ p.page_type }}</span>
            <WikiFreshnessBadge :status="p.freshness_status" />
          </div>
          <h3 class="text-fg mb-2">{{ p.title }}</h3>
          <p v-if="p.summary" class="text-xs text-muted line-clamp-3">{{ p.summary }}</p>
        </Card>
      </NuxtLink>
    </div>
  </div>
</template>
