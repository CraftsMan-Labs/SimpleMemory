/**
 * Listing + autocomplete search for [[wikilinks]].
 */
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { apiClient } from '@/lib/api'
import type { WikiPageListResponse } from '@@/types/api'

export function useWikiList(opts?: { sort?: 'updated' | 'title'; freshness?: string }) {
  return useQuery({
    queryKey: ['wiki', 'list', opts],
    queryFn: () =>
      apiClient<WikiPageListResponse>('/wiki/pages', {
        query: { sort: opts?.sort, freshness: opts?.freshness },
      }),
  })
}

export function useWikiAutocomplete(query: MaybeRefOrGetter<string>) {
  const q = computed(() => toValue(query).trim())
  return useQuery({
    queryKey: ['wiki', 'autocomplete', q],
    enabled: () => q.value.length >= 1,
    staleTime: 10_000,
    queryFn: () =>
      apiClient<WikiPageListResponse>('/wiki/pages', { query: { q: q.value, limit: 8 } }),
  })
}
