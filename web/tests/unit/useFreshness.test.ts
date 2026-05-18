import { describe, expect, it } from 'vitest'
import { useFreshness } from '@/composables/useFreshness'

describe('useFreshness.view', () => {
  const { view } = useFreshness()

  it('returns success variant for fresh', () => {
    const v = view('fresh')
    expect(v.variant).toBe('success')
    expect(v.needsTending).toBe(false)
  })

  it('returns warn variant for stale', () => {
    const v = view('stale')
    expect(v.variant).toBe('warn')
    expect(v.needsTending).toBe(true)
  })

  it('returns danger variant for outdated', () => {
    const v = view('outdated')
    expect(v.variant).toBe('danger')
    expect(v.needsTending).toBe(true)
  })

  it('defaults gracefully on unknown', () => {
    const v = view('mystery')
    expect(v.variant).toBe('default')
  })
})
