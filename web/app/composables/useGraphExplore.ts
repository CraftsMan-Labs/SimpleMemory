/**
 * Local + full graph exploration. Backend returns center node + edges + connected nodes.
 */
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiClient } from '@/lib/api'
import type { GraphExploreResponse, GraphNodeListResponse } from '@@/types/api'

export function useGraphExplore(nodeId: MaybeRefOrGetter<string>, depth: MaybeRefOrGetter<number> = 1) {
  const id = computed(() => toValue(nodeId))
  const d = computed(() => toValue(depth))
  return useQuery({
    queryKey: ['graph', 'explore', id, d],
    enabled: () => !!id.value,
    queryFn: () =>
      apiClient<GraphExploreResponse>(`/graph/nodes/${id.value}/explore`, {
        query: { depth: d.value },
      }),
  })
}

export function useGraphNodes(filter?: { node_type?: string; limit?: number }) {
  return useQuery({
    queryKey: ['graph', 'nodes', filter],
    queryFn: () => apiClient<GraphNodeListResponse>('/graph/nodes', { query: filter }),
  })
}
