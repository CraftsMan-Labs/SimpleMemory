import { describe, expect, it } from 'vitest'
import { useCommandPalette } from '@/composables/useCommandPalette'

describe('useCommandPalette', () => {
  it('toggles open state', () => {
    const p = useCommandPalette()
    p.hide()
    p.toggle()
    expect(p.open.value).toBe(true)
    p.toggle()
    expect(p.open.value).toBe(false)
  })

  it('changes mode via show()', () => {
    const p = useCommandPalette()
    p.show('ask')
    expect(p.mode.value).toBe('ask')
    expect(p.open.value).toBe(true)
    p.hide()
  })
})
