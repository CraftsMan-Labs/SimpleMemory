/**
 * Global middleware. Routes under /app/* require a tenant id set in localStorage.
 * If missing, redirect to /auth/login (preserving target).
 */
export default defineNuxtRouteMiddleware((to) => {
  if (!to.path.startsWith('/app')) return
  if (import.meta.server) return // tenant lives in localStorage; check on the client
  const tenant = window.localStorage.getItem('kmg.tenant_id') ?? ''
  if (!tenant) {
    return navigateTo({ path: '/auth/login', query: { next: to.fullPath } })
  }
})
