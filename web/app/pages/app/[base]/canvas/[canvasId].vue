<script setup lang="ts">
/**
 * Infinite canvas. Vue Flow root with custom node types per item_type.
 *  - AI organise triggers backend ai-organize then refetches; positions animate.
 *  - Toolbar buttons add a new wiki/source/concept/sticky-note item via /items POST.
 *  - Node-drag-stop autosaves the new (x,y) for that item by PATCHing the canvas
 *    layout blob with the latest positions (debounced 500ms).
 */
import { computed, ref, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import CanvasToolbar from '@/components/canvas/CanvasToolbar.vue'
import CanvasItemCard from '@/components/canvas/CanvasItemCard.vue'
import CanvasStickyNote from '@/components/canvas/CanvasStickyNote.vue'
import {
  useCanvas,
  useAiOrganize,
  useAddCanvasItems,
  useUpdateCanvas,
} from '@/composables/useCanvas'
import { useToast } from '@/composables/useToast'

definePageMeta({ layout: 'app' })

const VueFlow = defineAsyncComponent(() => import('@vue-flow/core').then((m) => m.VueFlow))
const Background = defineAsyncComponent(() => import('@vue-flow/background').then((m) => m.Background))
const Controls = defineAsyncComponent(() => import('@vue-flow/controls').then((m) => m.Controls))
const MiniMap = defineAsyncComponent(() => import('@vue-flow/minimap').then((m) => m.MiniMap))

const route = useRoute()
const canvasId = computed(() => route.params.canvasId as string)
const { data, refetch } = useCanvas(canvasId)

const aiOrganize = useAiOrganize(canvasId.value)
const addItems = useAddCanvasItems(canvasId.value)
const updateCanvas = useUpdateCanvas(canvasId.value)
const { push } = useToast()

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const nodeTypes: Record<string, any> = { item: CanvasItemCard, sticky: CanvasStickyNote }

const positions = ref<Record<string, { x: number; y: number }>>({})
watch(
  data,
  (d) => {
    if (!d) return
    positions.value = Object.fromEntries(d.items.map((i) => [i.id, { x: i.x, y: i.y }]))
  },
  { immediate: true },
)

const nodes = computed(() => {
  const items = data.value?.items ?? []
  return items.map((it) => {
    const p = positions.value[it.id] ?? { x: it.x, y: it.y }
    return {
      id: it.id,
      type: it.item_type === 'sticky_note' ? 'sticky' : 'item',
      position: p,
      data: {
        label: (it.style?.label as string) || it.item_type,
        type: it.item_type,
        summary: it.style?.summary as string | undefined,
      },
      style: { width: it.width, height: it.height },
    }
  })
})

const edges = computed(() =>
  (data.value?.edges ?? []).map((e) => ({
    id: e.id,
    source: e.from_item_id,
    target: e.to_item_id,
    label: e.label ?? undefined,
    type: 'smoothstep',
    style: { stroke: 'var(--accent)' },
  })),
)

const persistLayout = useDebounceFn(() => {
  updateCanvas.mutate({ layout: { items: positions.value } })
}, 500)

const onNodeDragStop = (e: { node: { id: string; position: { x: number; y: number } } }) => {
  positions.value[e.node.id] = e.node.position
  persistLayout()
}

const organize = async () => {
  const res = await aiOrganize.mutateAsync()
  push({
    title: 'Reorganised',
    message: `${res.items_moved} items into ${res.groups.length} clusters`,
    tone: 'accent',
  })
  refetch()
}

const addItem = (item_type: string, label: string) => {
  const x = 100 + Math.random() * 200
  const y = 100 + Math.random() * 200
  addItems.mutate(
    [{ item_type, x, y, width: 220, height: 140, style: { label } }],
    {
      onSuccess: () => push({ title: `Added ${item_type}`, tone: 'accent' }),
    },
  )
}
</script>

<template>
  <div class="relative h-[calc(100vh-2.25rem)] w-full bg-bg">
    <ClientOnly>
      <VueFlow
        :nodes="nodes"
        :edges="edges"
        :node-types="nodeTypes"
        fit-view
        class="canvas-root"
        @node-drag-stop="onNodeDragStop"
      >
        <Background pattern-color="var(--border-soft)" :gap="24" />
        <Controls />
        <MiniMap pannable zoomable mask-color="rgba(0,0,0,0.6)" />
      </VueFlow>
    </ClientOnly>
    <CanvasToolbar
      :organizing="aiOrganize.isPending.value"
      @ai-organize="organize"
      @add-wiki="() => addItem('wiki_page', 'Wiki card')"
      @add-node="() => addItem('graph_node', 'Concept')"
      @add-source="() => addItem('source', 'Source')"
      @add-sticky="() => addItem('sticky_note', 'Note')"
    />
  </div>
</template>

<style scoped>
.canvas-root :deep(.vue-flow__node) {
  transition: transform 600ms cubic-bezier(0.2, 0.9, 0.3, 1);
}
</style>
