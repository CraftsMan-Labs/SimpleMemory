/**
 * Workspaces (Project Bases) — list + create + update.
 * Hydrates the Pinia store on first load so the proxy can inject tenant headers.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { apiClient } from '@/lib/api'
import { useProjectBaseStore } from '@/stores/projectBase'
import type {
  CreateWorkspaceRequest,
  UpdateWorkspaceRequest,
  Workspace,
  WorkspaceListResponse,
} from '@@/types/api'

export function useWorkspaceList() {
  const store = useProjectBaseStore()
  return useQuery({
    queryKey: ['workspaces'],
    queryFn: async () => {
      const res = await apiClient<WorkspaceListResponse>('/workspaces')
      store.setWorkspaces(res.workspaces)
      return res
    },
  })
}

export function useWorkspace(id: () => string) {
  return useQuery({
    queryKey: ['workspace', id],
    enabled: () => !!id(),
    queryFn: () => apiClient<Workspace>(`/workspaces/${id()}`),
  })
}

export function useCreateWorkspace() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: CreateWorkspaceRequest) =>
      apiClient<Workspace>('/workspaces', { method: 'POST', body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['workspaces'] }),
  })
}

export function useUpdateWorkspace() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateWorkspaceRequest }) =>
      apiClient<Workspace>(`/workspaces/${id}`, { method: 'PATCH', body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['workspaces'] }),
  })
}
