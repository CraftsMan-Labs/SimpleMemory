import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { effectScope, ref, nextTick } from 'vue'
import { useJobStream } from '@/composables/useJobStream'
import { apiClient } from '@/lib/api'

vi.mock('@/lib/api', () => ({
  apiClient: vi.fn(),
}))

const mocked = apiClient as unknown as ReturnType<typeof vi.fn>

describe('useJobStream', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    mocked.mockReset()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('fetches on first id, then stops on completed status', async () => {
    mocked
      .mockResolvedValueOnce({ id: 'j1', status: 'running', stage: 'parsing', progress: 0.1, error: null, created_at: '', updated_at: '' })
      .mockResolvedValueOnce({ id: 'j1', status: 'completed', stage: 'completed', progress: 1, error: null, created_at: '', updated_at: '' })

    const scope = effectScope()
    let s: ReturnType<typeof useJobStream> | null = null
    scope.run(() => {
      const id = ref<string | null>('j1')
      s = useJobStream(id)
    })
    await Promise.resolve()
    await Promise.resolve()
    expect(mocked).toHaveBeenCalledTimes(1)

    // advance timer to trigger the next poll
    await vi.advanceTimersByTimeAsync(1500)
    expect(mocked).toHaveBeenCalledTimes(2)
    expect(s!.status.value?.status).toBe('completed')

    // no further calls after completion
    await vi.advanceTimersByTimeAsync(3000)
    expect(mocked).toHaveBeenCalledTimes(2)

    scope.stop()
  })

  it('does nothing when id is null', async () => {
    const scope = effectScope()
    scope.run(() => {
      const id = ref<string | null>(null)
      useJobStream(id)
    })
    await nextTick()
    expect(mocked).not.toHaveBeenCalled()
    scope.stop()
  })
})
