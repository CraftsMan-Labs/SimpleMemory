<script setup lang="ts">
/** Project Base home — stats, recents, stale alert, canvas thumbnails. */
import { computed } from 'vue'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import { useProjectBase } from '@/composables/useProjectBase'
import { useWikiList } from '@/composables/useWikiList'
import { useCanvasList, useCreateCanvas } from '@/composables/useCanvas'
import { useSourceList } from '@/composables/useSourceIngest'
import { useGraphNodes } from '@/composables/useGraphExplore'
import { FileText, Files, MapPinned, Layers, Sparkles, Plus, Quote } from 'lucide-vue-next'

definePageMeta({ layout: 'app' })

const { current } = useProjectBase()
const { data: wiki } = useWikiList({ sort: 'updated' })
const { data: sources } = useSourceList()
const { data: canvases } = useCanvasList()
const { data: nodes } = useGraphNodes()

const recent = computed(() => (wiki.value?.pages ?? []).slice(0, 6))
const stale = computed(() =>
  (wiki.value?.pages ?? []).filter((p) => p.freshness_status === 'stale' || p.freshness_status === 'outdated'),
)

const createCanvas = useCreateCanvas()
const router = useRouter()
const onNewCanvas = async () => {
  const c = await createCanvas.mutateAsync({ title: 'Untitled canvas' })
  router.push(`/app/${current.value?.slug}/canvas/${c.id}`)
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-8 py-12 pb-24">
    <header class="mb-12">
      <p class="font-mono text-xs uppercase tracking-widest text-accent mb-2">Project Base</p>
      <h1 class="text-display text-fg" style="font-size: clamp(2rem, 5vw, 3.5rem);">
        {{ current?.name ?? 'Project Base' }}
      </h1>
      <p v-if="current" class="text-muted mt-2 font-mono text-xs">/{{ current.slug }}</p>
    </header>

    <section class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-12">
      <Card padded>
        <Files :size="16" class="text-accent mb-3" />
        <div class="text-2xl text-fg text-display">{{ sources?.total ?? 0 }}</div>
        <div class="text-xs text-muted mt-1">Sources</div>
      </Card>
      <Card padded>
        <FileText :size="16" class="text-accent mb-3" />
        <div class="text-2xl text-fg text-display">{{ wiki?.total ?? 0 }}</div>
        <div class="text-xs text-muted mt-1">Wiki pages</div>
      </Card>
      <Card padded>
        <MapPinned :size="16" class="text-accent mb-3" />
        <div class="text-2xl text-fg text-display">{{ nodes?.total ?? 0 }}</div>
        <div class="text-xs text-muted mt-1">Graph nodes</div>
      </Card>
      <Card padded>
        <Layers :size="16" class="text-accent mb-3" />
        <div class="text-2xl text-fg text-display">{{ canvases?.total ?? 0 }}</div>
        <div class="text-xs text-muted mt-1">Canvases</div>
      </Card>
    </section>

    <section v-if="stale.length" class="mb-12">
      <Card padded class="border-l-2 border-l-[var(--warn)]">
        <div class="flex items-center gap-2 mb-2">
          <Sparkles :size="14" class="text-[var(--warn)]" />
          <h3 class="text-fg">{{ stale.length }} page{{ stale.length > 1 ? 's' : '' }} need tending.</h3>
        </div>
        <p class="text-muted text-sm mb-4">These pages are stale relative to their evidence. Regenerate or review.</p>
        <ul class="space-y-1">
          <li v-for="p in stale.slice(0, 4)" :key="p.id">
            <NuxtLink :to="`/app/${current?.slug}/wiki/${p.slug}`" class="text-sm text-fg-2 hover:text-accent">
              {{ p.title }}
              <Badge variant="warn" class="ml-2">{{ p.freshness_status }}</Badge>
            </NuxtLink>
          </li>
        </ul>
      </Card>
    </section>

    <section class="mb-12">
      <h2 class="text-fg text-xl mb-4">Recently edited</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <NuxtLink v-for="p in recent" :key="p.id" :to="`/app/${current?.slug}/wiki/${p.slug}`">
          <Card padded class="hover:border-accent transition-colors h-full">
            <FileText :size="14" class="text-meta mb-2" />
            <h3 class="text-fg mb-2 truncate">{{ p.title }}</h3>
            <p v-if="p.summary" class="text-xs text-muted line-clamp-3">{{ p.summary }}</p>
            <div class="mt-3 flex items-center gap-2">
              <Badge :variant="p.freshness_status === 'fresh' ? 'success' : 'warn'">{{ p.freshness_status }}</Badge>
              <span class="text-[10px] text-meta font-mono">{{ p.chunk_count }} chunks</span>
            </div>
          </Card>
        </NuxtLink>
        <Card v-if="!recent.length" padded class="text-center text-muted text-sm">
          <Quote :size="20" class="text-meta mx-auto mb-3" />
          No wiki pages yet. Drop a source to get started.
        </Card>
      </div>
    </section>

    <section>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-fg text-xl">Canvases</h2>
        <Button variant="outline" size="sm" @click="onNewCanvas"><Plus :size="12" /> New canvas</Button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <NuxtLink v-for="c in canvases?.canvases ?? []" :key="c.id" :to="`/app/${current?.slug}/canvas/${c.id}`">
          <Card padded class="hover:border-accent transition-colors h-full">
            <Layers :size="14" class="text-meta mb-2" />
            <h3 class="text-fg truncate">{{ c.title }}</h3>
            <p class="text-[10px] text-meta font-mono mt-2">{{ new Date(c.updated_at).toLocaleDateString() }}</p>
          </Card>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>
