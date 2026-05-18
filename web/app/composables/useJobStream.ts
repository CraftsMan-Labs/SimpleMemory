/**
 * Polls a job's status. We use polling (not SSE) for v1 — the FastAPI endpoint
 * returns the current job state, and the worker writes stage transitions to Postgres.
 * Polling every 1500ms keeps the timeline alive without coupling to streaming infra.
 */
import { ref, onScopeDispose, watch, type Ref } from 'vue'
import { apiClient } from '@/lib/api'
import type { JobStatus } from '@@/types/api'

const ACTIVE = new Set(['pending', 'running'])

export function useJobStream(jobId: Ref<string | null>) {
  const status = ref<JobStatus | null>(null)
  const error = ref<string | null>(null)
  let timer: number | null = null

  const stop = () => {
    if (timer != null) {
      window.clearTimeout(timer)
      timer = null
    }
  }

  const tick = async (id: string) => {
    try {
      const job = await apiClient<JobStatus>(`/jobs/${id}`)
      status.value = job
      if (ACTIVE.has(job.status)) {
        timer = window.setTimeout(() => tick(id), 1500)
      }
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : String(e)
    }
  }

  watch(
    jobId,
    (id) => {
      stop()
      status.value = null
      if (id) tick(id)
    },
    { immediate: true },
  )

  onScopeDispose(stop)
  return { status, error, stop }
}
