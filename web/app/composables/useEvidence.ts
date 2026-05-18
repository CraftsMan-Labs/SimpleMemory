/**
 * Evidence for a wiki page + lazy chunk lookup for citation drill-down.
 */
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiClient } from '@/lib/api'
import type { Chunk, WikiEvidence } from '@@/types/api'

export function useWikiEvidence(pageId: MaybeRefOrGetter<string>) {
  const id = computed(() => toValue(pageId))
  return useQuery({
    queryKey: ['wiki', 'evidence', id],
    enabled: () => !!id.value,
    queryFn: () => apiClient<WikiEvidence[]>(`/wiki/pages/${id.value}/evidence`),
  })
}

export function useChunk(chunkId: MaybeRefOrGetter<string | null>) {
  const id = computed(() => toValue(chunkId))
  return useQuery({
    queryKey: ['chunk', id],
    enabled: () => !!id.value,
    queryFn: () => apiClient<Chunk>(`/chunks/${id.value}`),
  })
}
