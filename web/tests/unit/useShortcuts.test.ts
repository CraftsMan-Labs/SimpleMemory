import { describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { useShortcuts } from '@/composables/useShortcuts'

const Host = defineComponent({
  props: ['handlers'],
  setup(props) {
    useShortcuts(props.handlers)
    return () => h('div')
  },
})

const press = (key: string, opts: KeyboardEventInit = {}) => {
  document.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true, ...opts }))
}

describe('useShortcuts', () => {
  it('fires ⌘K palette handler', () => {
    const onCommandPalette = vi.fn()
    mount(Host, { props: { handlers: { onCommandPalette } } })
    press('k', { metaKey: true })
    expect(onCommandPalette).toHaveBeenCalled()
  })

  it('triggers g g chord for graph', () => {
    const onGoGraph = vi.fn()
    mount(Host, { props: { handlers: { onGoGraph } } })
    press('g')
    press('g')
    expect(onGoGraph).toHaveBeenCalled()
  })

  it('ignores chords when typing into an input', () => {
    const onGoGraph = vi.fn()
    mount(Host, { props: { handlers: { onGoGraph } } })
    const input = document.createElement('input')
    document.body.appendChild(input)
    input.focus()
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'g', bubbles: true }))
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'g', bubbles: true }))
    expect(onGoGraph).not.toHaveBeenCalled()
  })
})
