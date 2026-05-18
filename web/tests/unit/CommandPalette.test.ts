import { describe, expect, it } from 'vitest'
import { useCommandPalette } from '@/composables/useCommandPalette'

describe('useCommandPalette modes', () => {
  it('show with default mode', () => {
    const p = useCommandPalette()
    p.hide()
    p.show()
    expect(p.open.value).toBe(true)
    expect(p.mode.value).toBe('find')
    p.hide()
  })

  it('switches mode without closing', () => {
    const p = useCommandPalette()
    p.show('find')
    p.setMode('jump')
    expect(p.mode.value).toBe('jump')
    expect(p.open.value).toBe(true)
    p.hide()
  })

  it('hide() clears query', () => {
    const p = useCommandPalette()
    p.show('find')
    p.query.value = 'something'
    p.hide()
    expect(p.query.value).toBe('')
  })
})
