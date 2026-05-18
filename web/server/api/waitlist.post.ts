/**
 * Stub waitlist endpoint. Logs to stdout in dev; integrate with the FastAPI
 * service or your CRM in production.
 */
import { defineEventHandler, readBody, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const body = await readBody<{ email?: string; role?: string }>(event)
  if (!body?.email) {
    throw createError({ statusCode: 400, statusMessage: 'email required' })
  }
  console.info('[waitlist]', body.email, body.role ?? '')
  return { ok: true }
})
