<script setup lang="ts">
/**
 * Full graph explorer. Uses Vue Flow with custom node + edge SFCs per record_type.
 * Loads up to 300 nodes + 500 edges; provides layer/confidence filters; lays out
 * nodes deterministically by ring so layout is stable across re-renders.
 */
import { computed, ref, watch } from 'vue'
import GraphFilters from '@/components/graph/GraphFilters.vue'
import GraphLegend from '@/components/graph/GraphLegend.vue'
import WikiPageNode from '@/components/graph/nodes/WikiPageNode.vue'
import GraphConceptNode from '@/components/graph/nodes/GraphConceptNode.vue'
import SourceNode from '@/components/graph/nodes/SourceNode.vue'
import ChunkNode from '@/components/graph/nodes/ChunkNode.vue'
import WikiLinkEdge from '@/components/graph/edges/WikiLinkEdge.vue'
import SemanticEdge from '@/components/graph/edges/SemanticEdge.vue'
import { useGraphNodes } from '@/composables/useGraphExplore'
import { apiClient } from '@/lib/api'
import { useAsyncState } from '@vueuse/core'
import type { GraphEdgeListResponse } from '@@/types/api'

definePageMeta({ layout: 'app' })

const VueFlow = defineAsyncComponent(() => import('@vue-flow/core').then((m) => m.VueFlow))
const Background = defineAsyncComponent(() => import('@vue-flow/background').then((m) => m.Background))
const Controls = defineAsyncComponent(() => import('@vue-flow/controls').then((m) => m.Controls))
const MiniMap = defineAsyncComponent(() => import('@vue-flow/minimap').then((m) => m.MiniMap))

const layer = ref<'wiki' | 'semantic' | 'unified'>('unified')
const minConfidence = ref(0)

const { data: nodesData } = useGraphNodes({ limit: 300 })
const edgesState = useAsyncState(
  () => apiClient<GraphEdgeListResponse>('/graph/edges', { query: { limit: 500, min_confidence: minConfidence.value } }),
  null,
  { resetOnExecute: false },
)

// Refetch edges when confidence floor changes
watch(minConfidence, () => edgesState.execute())

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const nodeTypes: Record<string, any> = {
  wiki: WikiPageNode,
  concept: GraphConceptNode,
  source: SourceNode,
  chunk: ChunkNode,
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const edgeTypes: Record<string, any> = {
  wikilink: WikiLinkEdge,
  semantic: SemanticEdge,
}

const inferNodeKind = (type: string): keyof typeof nodeTypes => {
  if (type === 'wiki_page') return 'wiki'
  if (type === 'source') return 'source'
  if (type === 'chunk') return 'chunk'
  return 'concept'
}

const elements = computed(() => {
  const all = nodesData.value?.nodes ?? []
  const nodes = all.map((n, i) => {
    const ring = i < 12 ? 0 : i < 36 ? 1 : i < 80 ? 2 : 3
    const r = 140 + ring * 200
    const a = (i / Math.max(all.length, 1)) * Math.PI * 2
    return {
      id: n.id,
      type: inferNodeKind(n.node_type),
      position: { x: Math.cos(a) * r, y: Math.sin(a) * r },
      data: { label: n.canonical_name, type: n.node_type },
    }
  })
  const edges = (edgesState.state.value?.edges ?? [])
    .filter((e) => e.confidence >= minConfidence.value)
    .filter((e) => {
      const isWiki = e.predicate.includes('link')
      if (layer.value === 'wiki') return isWiki
      if (layer.value === 'semantic') return !isWiki
      return true
    })
    .map((e) => ({
      id: e.id,
      source: e.subject_id,
      target: e.object_id,
      type: e.predicate.includes('link') ? 'wikilink' : 'semantic',
      label: e.predicate,
    }))
  return { nodes, edges }
})
</script>

<template>
  <div class="relative h-[calc(100vh-2.25rem)] w-full bg-bg">
    <ClientOnly>
      <VueFlow
        :nodes="elements.nodes"
        :edges="elements.edges"
        :node-types="nodeTypes"
        :edge-types="edgeTypes"
        fit-view
        :default-zoom="0.6"
        class="text-xs"
      >
        <Background pattern-color="var(--border-soft)" :gap="16" />
        <Controls />
        <MiniMap pannable zoomable mask-color="rgba(0,0,0,0.6)" />
      </VueFlow>
    </ClientOnly>
    <GraphFilters v-model:layer="layer" v-model:min-confidence="minConfidence" />
    <GraphLegend />
  </div>
</template>
