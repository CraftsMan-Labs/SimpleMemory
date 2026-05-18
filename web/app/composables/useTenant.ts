/**
 * Auth + tenant context.
 *
 * In dev the FastAPI accepts an `X-Tenant-ID` header bypass (non-prod only).
 * In prod, callers must send `Authorization: Bearer ...`. The Nuxt server
 * proxy reads the server-side `KMG_API_KEY` and attaches it; the browser only
 * needs to know which tenant + workspace headers to send.
 *
 * `useTenant` persists the tenant id locally so the proxy can inject it for
 * every request. The login page sets it; logout clears it.
 */
import { computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'

const STORAGE_KEY = 'kmg.tenant_id'

export function useTenant() {
  const tenantId = useLocalStorage<string>(STORAGE_KEY, '')
  const isAuthed = computed(() => !!tenantId.value)
  const login = (id: string) => { tenantId.value = id }
  const logout = () => { tenantId.value = '' }
  return { tenantId, isAuthed, login, logout }
}
