/**
 * Single wiki page + backlinks + revisions. Optimistic update on save.
 */
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { apiClient } from '@/lib/api'
import type {
  UpdateWikiPageRequest,
  WikiBacklink,
  WikiPage,
  WikiRevision,
} from '@@/types/api'

export function useWikiPageBySlug(slug: MaybeRefOrGetter<string>) {
  const slugRef = computed(() => toValue(slug))
  return useQuery({
    queryKey: ['wiki', 'page', slugRef],
    enabled: () => !!slugRef.value,
    queryFn: () => apiClient<WikiPage>(`/wiki/pages/by-slug/${slugRef.value}`),
  })
}

export function useWikiBacklinks(pageId: MaybeRefOrGetter<string>) {
  const idRef = computed(() => toValue(pageId))
  return useQuery({
    queryKey: ['wiki', 'backlinks', idRef],
    enabled: () => !!idRef.value,
    queryFn: () => apiClient<WikiBacklink[]>(`/wiki/pages/${idRef.value}/backlinks`),
  })
}

export function useWikiRevisions(pageId: MaybeRefOrGetter<string>) {
  const idRef = computed(() => toValue(pageId))
  return useQuery({
    queryKey: ['wiki', 'revisions', idRef],
    enabled: () => !!idRef.value,
    queryFn: () => apiClient<WikiRevision[]>(`/wiki/pages/${idRef.value}/revisions`),
  })
}

export function useUpdateWikiPage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateWikiPageRequest }) =>
      apiClient<WikiPage>(`/wiki/pages/${id}`, { method: 'PATCH', body }),
    onSuccess: (page) => {
      qc.setQueryData(['wiki', 'page', page.slug], page)
      qc.invalidateQueries({ queryKey: ['wiki', 'list'] })
    },
  })
}
