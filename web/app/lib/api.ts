/**
 * Browser-side fetch client. Hits the Nuxt proxy at /api/v1/* so credentials stay server-side.
 * Tenant id is pulled directly from localStorage (set by the login page) so the
 * client works before the workspaces list has loaded. Workspace id comes from
 * the Pinia store once a Project Base is selected.
 */
import { ofetch, type FetchOptions } from 'ofetch'

const TENANT_KEY = 'kmg.tenant_id'

function getTenantId(): string {
  if (typeof window === 'undefined') return ''
  return window.localStorage.getItem(TENANT_KEY) ?? ''
}

function getWorkspaceId(): string {
  if (typeof window === 'undefined') return ''
  // Pinia stores aren't safe to import here (circular) — read the active slug
  // from the path and let the proxy filter; or peek a session-cached id.
  return window.sessionStorage.getItem('kmg.workspace_id') ?? ''
}

export const apiClient = ofetch.create({
  baseURL: '/api/v1',
  retry: 1,
  retryDelay: 300,
  onRequest({ options }) {
    if (import.meta.client) {
      const headers = new Headers(options.headers as HeadersInit | undefined)
      const tenant = getTenantId()
      const workspace = getWorkspaceId()
      if (tenant) headers.set('X-Tenant-Id', tenant)
      if (workspace) headers.set('X-Workspace-Id', workspace)
      options.headers = headers
    }
  },
})

export type ApiRequest<T = unknown> = FetchOptions<'json'> & { body?: T }

export function setActiveWorkspaceId(id: string) {
  if (typeof window === 'undefined') return
  if (id) window.sessionStorage.setItem('kmg.workspace_id', id)
  else window.sessionStorage.removeItem('kmg.workspace_id')
}
