/**
 * Active project-base context. Reads the route param `[base]` and reflects it
 * into the Pinia store + sessionStorage so the API client picks up the workspace header.
 */
import { computed, watch, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectBaseStore } from '@/stores/projectBase'
import { useWorkspaceList } from './useWorkspaceApi'
import { setActiveWorkspaceId } from '@/lib/api'

export function useProjectBase() {
  const route = useRoute()
  const store = useProjectBaseStore()
  const { data, isLoading, refetch } = useWorkspaceList()

  watchEffect(() => {
    const slug = route.params.base as string | undefined
    if (slug && slug !== store.currentSlug) store.selectBySlug(slug)
  })

  const current = computed(() => store.current)
  const list = computed(() => store.workspaces)

  watch(
    () => current.value?.id,
    (id) => setActiveWorkspaceId(id ?? ''),
    { immediate: true },
  )

  return { current, list, isLoading, refetch, data, selectBySlug: store.selectBySlug }
}
