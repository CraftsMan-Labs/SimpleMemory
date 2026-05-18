import { describe, expect, it, beforeEach } from 'vitest'
import { useTheme } from '@/composables/useTheme'

describe('useTheme', () => {
  beforeEach(() => localStorage.clear())

  it('defaults to framer', () => {
    const { skin } = useTheme()
    expect(skin.value).toBe('framer')
  })

  it('toggles between framer and mintlify', () => {
    const { skin, toggle } = useTheme()
    toggle()
    expect(skin.value).toBe('mintlify')
    toggle()
    expect(skin.value).toBe('framer')
  })
})
