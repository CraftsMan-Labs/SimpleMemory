<script setup lang="ts">
/**
 * Mini local graph rendered around the page's owning graph node. Uses Vue Flow
 * with custom node types + a subtle idle drift on the connected nodes so the
 * panel feels alive when the user isn't interacting.
 */
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { MapPinned } from 'lucide-vue-next'
import { useGraphExplore } from '@/composables/useGraphExplore'
import WikiPageNode from '@/components/graph/nodes/WikiPageNode.vue'
import GraphConceptNode from '@/components/graph/nodes/GraphConceptNode.vue'

const props = defineProps<{ nodeId?: string }>()
const enabled = computed(() => !!props.nodeId)
const { data, isLoading } = useGraphExplore(() => props.nodeId ?? '', 1)

const VueFlow = defineAsyncComponent(() => import('@vue-flow/core').then((m) => m.VueFlow))

const driftPhase = ref(0)
let rafId: number | null = null
const tick = () => {
  driftPhase.value = (driftPhase.value + 0.003) % (Math.PI * 2)
  rafId = requestAnimationFrame(tick)
}

watch(
  enabled,
  (on) => {
    if (on && rafId == null) rafId = requestAnimationFrame(tick)
    if (!on && rafId != null) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  if (rafId != null) cancelAnimationFrame(rafId)
})

const inferNodeKind = (type: string) =>
  type === 'wiki_page' ? 'wiki' : 'concept'

const elements = computed(() => {
  if (!data.value) return { nodes: [], edges: [] }
  const cx = 0, cy = 0
  const connected = data.value.connected_nodes ?? []
  const r = 80
  const phase = driftPhase.value
  const nodes = [
    {
      id: data.value.center_node.id,
      type: inferNodeKind(data.value.center_node.node_type),
      position: { x: cx, y: cy },
      data: { label: data.value.center_node.canonical_name },
    },
    ...connected.map((n, i) => {
      const a = (i / Math.max(connected.length, 1)) * Math.PI * 2 + phase
      return {
        id: n.id,
        type: inferNodeKind(n.node_type),
        position: { x: Math.cos(a) * r, y: Math.sin(a) * r },
        data: { label: n.canonical_name },
      }
    }),
  ]
  const edges = (data.value.edges ?? []).map((e, i) => ({
    id: `e-${i}`,
    source: e.subject_id,
    target: e.object_id,
    label: e.predicate,
  }))
  return { nodes, edges }
})

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const nodeTypes: Record<string, any> = { wiki: WikiPageNode, concept: GraphConceptNode }
</script>

<template>
  <section>
    <h3 class="text-xs font-mono uppercase tracking-widest text-meta mb-2 flex items-center gap-1.5">
      <MapPinned :size="11" /> Local graph
    </h3>
    <div v-if="!enabled" class="text-xs text-meta italic">Not mapped to a graph node yet.</div>
    <div v-else-if="isLoading" class="text-xs text-meta">Loading graph…</div>
    <div v-else class="h-48 surface-card overflow-hidden">
      <ClientOnly>
        <VueFlow
          :nodes="elements.nodes"
          :edges="elements.edges"
          :node-types="nodeTypes"
          :pan-on-drag="false"
          :zoom-on-scroll="false"
          :nodes-draggable="false"
          fit-view
          class="text-xs"
        />
      </ClientOnly>
    </div>
  </section>
</template>
