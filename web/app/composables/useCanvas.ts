/**
 * Canvas CRUD + AI organize.
 */
import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { apiClient } from '@/lib/api'
import type {
  AiOrganizeResponse,
  Canvas,
  CanvasDetailResponse,
  CanvasEdgeRequest,
  CanvasItemRequest,
  CanvasListResponse,
  CreateCanvasRequest,
  UpdateCanvasRequest,
} from '@@/types/api'

export function useCanvasList() {
  return useQuery({
    queryKey: ['canvases'],
    queryFn: () => apiClient<CanvasListResponse>('/canvases'),
  })
}

export function useCanvas(id: MaybeRefOrGetter<string>) {
  const idRef = computed(() => toValue(id))
  return useQuery({
    queryKey: ['canvas', idRef],
    enabled: () => !!idRef.value,
    queryFn: () => apiClient<CanvasDetailResponse>(`/canvases/${idRef.value}`),
  })
}

export function useCreateCanvas() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: CreateCanvasRequest) =>
      apiClient<Canvas>('/canvases', { method: 'POST', body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['canvases'] }),
  })
}

export function useUpdateCanvas(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: UpdateCanvasRequest) =>
      apiClient<Canvas>(`/canvases/${id}`, { method: 'PATCH', body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['canvas', id] }),
  })
}

export function useAddCanvasItems(canvasId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (items: CanvasItemRequest[]) =>
      apiClient(`/canvases/${canvasId}/items`, { method: 'POST', body: items }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['canvas', canvasId] }),
  })
}

export function useAddCanvasEdges(canvasId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (edges: CanvasEdgeRequest[]) =>
      apiClient(`/canvases/${canvasId}/edges`, { method: 'POST', body: edges }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['canvas', canvasId] }),
  })
}

export function useAiOrganize(canvasId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () =>
      apiClient<AiOrganizeResponse>(`/canvases/${canvasId}/ai-organize`, { method: 'POST' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['canvas', canvasId] }),
  })
}
