/**
 * Global keyboard shortcuts. Uses VueUse magic-keys with a tiny chord layer
 * (`g g` → home, `g w` → wiki, `g g` → graph, `g c` → canvas).
 * Components opt in by mounting once at the app shell level.
 */
import { onScopeDispose } from 'vue'
import { useEventListener, useMagicKeys } from '@vueuse/core'

export interface ShortcutHandlers {
  onCommandPalette?: () => void
  onGoHome?: () => void
  onGoWiki?: () => void
  onGoGraph?: () => void
  onGoCanvas?: () => void
  onGoSearch?: () => void
  onToggleEdit?: () => void
}

export function useShortcuts(h: ShortcutHandlers) {
  const keys = useMagicKeys({
    passive: false,
    onEventFired(e) {
      // ⌘K / Ctrl+K
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k' && e.type === 'keydown') {
        e.preventDefault()
        h.onCommandPalette?.()
      }
    },
  })

  // Chord buffer: pressing "g" then a letter within 800ms
  let chord: { ts: number; key: string } | null = null
  const stop = useEventListener('keydown', (e: KeyboardEvent) => {
    const target = e.target as HTMLElement | null
    if (target && /input|textarea/i.test(target.tagName)) return
    if (target?.isContentEditable) return

    if (chord && Date.now() - chord.ts < 800) {
      if (e.key === 'h') h.onGoHome?.()
      else if (e.key === 'w') h.onGoWiki?.()
      else if (e.key === 'g') h.onGoGraph?.()
      else if (e.key === 'c') h.onGoCanvas?.()
      else if (e.key === 's') h.onGoSearch?.()
      chord = null
      return
    }
    if (e.key === 'g') chord = { ts: Date.now(), key: 'g' }
    else if (e.key === 'e') h.onToggleEdit?.()
  })

  onScopeDispose(() => {
    stop()
    void keys
  })
}
