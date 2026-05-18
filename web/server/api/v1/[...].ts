/**
 * Catch-all proxy to FastAPI. Forwards path + method + body, injects auth + tenant
 * headers from runtime config (server-only, never exposed to the browser).
 *
 * Routes hit: /api/v1/workspaces, /api/v1/sources, /api/v1/wiki/*, /api/v1/graph/*,
 * /api/v1/search, /api/v1/chat, /api/v1/canvases/*.
 */
import { defineEventHandler, getRequestHeaders, readRawBody, setResponseHeaders, getRouterParam, getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.apiBaseUrl
  const apiKey = config.apiKey

  const pathSegments = (getRouterParam(event, '_') ?? '').split('/').filter(Boolean)
  const upstreamPath = `/v1/${pathSegments.join('/')}`
  const query = getQuery(event)
  const qs = new URLSearchParams()
  for (const [k, v] of Object.entries(query)) {
    if (v === undefined || v === null) continue
    if (Array.isArray(v)) v.forEach((x) => qs.append(k, String(x)))
    else qs.append(k, String(v))
  }
  const url = `${apiBase}${upstreamPath}${qs.toString() ? `?${qs}` : ''}`

  const incoming = getRequestHeaders(event)
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: incoming['accept'] ?? 'application/json',
  }
  if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`
  if (incoming['x-tenant-id']) headers['X-Tenant-Id'] = incoming['x-tenant-id'] as string
  if (incoming['x-workspace-id']) headers['X-Workspace-Id'] = incoming['x-workspace-id'] as string
  if (incoming['x-request-id']) headers['X-Request-Id'] = incoming['x-request-id'] as string

  const method = event.method ?? 'GET'
  const init: RequestInit = { method, headers }
  if (method !== 'GET' && method !== 'HEAD') {
    const body = await readRawBody(event)
    if (body) init.body = body
  }

  const res = await fetch(url, init)
  const contentType = res.headers.get('content-type') ?? ''
  setResponseHeaders(event, {
    'content-type': contentType,
    'cache-control': res.headers.get('cache-control') ?? 'no-store',
  })
  event.node.res.statusCode = res.status
  // Stream-friendly: pass body straight through (SSE, JSON, anything)
  return res.body
})
