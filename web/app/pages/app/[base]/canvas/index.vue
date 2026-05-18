<script setup lang="ts">
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import { useCanvasList, useCreateCanvas } from '@/composables/useCanvas'
import { useProjectBase } from '@/composables/useProjectBase'
import { Plus, Layers } from 'lucide-vue-next'

definePageMeta({ layout: 'app' })

const { data } = useCanvasList()
const { current } = useProjectBase()
const create = useCreateCanvas()
const router = useRouter()

const newCanvas = async () => {
  const c = await create.mutateAsync({ title: 'Untitled canvas' })
  router.push(`/app/${current.value?.slug}/canvas/${c.id}`)
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-8 py-12 pb-24">
    <div class="flex items-end justify-between mb-8">
      <div>
        <p class="font-mono text-xs uppercase tracking-widest text-accent mb-2">Canvases</p>
        <h1 class="text-display text-fg text-3xl">Your spatial workshop.</h1>
      </div>
      <Button variant="accent" @click="newCanvas"><Plus :size="14" /> New canvas</Button>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      <NuxtLink v-for="c in data?.canvases ?? []" :key="c.id" :to="`/app/${current?.slug}/canvas/${c.id}`">
        <Card padded class="hover:border-accent transition-colors h-full">
          <Layers :size="14" class="text-meta mb-3" />
          <h3 class="text-fg truncate">{{ c.title }}</h3>
          <p class="text-[10px] text-meta font-mono mt-2">{{ new Date(c.updated_at).toLocaleDateString() }}</p>
        </Card>
      </NuxtLink>
    </div>
  </div>
</template>
