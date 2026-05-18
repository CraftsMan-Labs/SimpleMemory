/**
 * Centralised state for the ⌘K command palette. Mode = find | ask | jump.
 */
import { ref } from 'vue'

export type PaletteMode = 'find' | 'ask' | 'jump'

const open = ref(false)
const mode = ref<PaletteMode>('find')
const query = ref('')

export function useCommandPalette() {
  const show = (m: PaletteMode = 'find') => {
    mode.value = m
    open.value = true
  }
  const hide = () => {
    open.value = false
    query.value = ''
  }
  const toggle = () => (open.value ? hide() : show())
  return { open, mode, query, show, hide, toggle, setMode: (m: PaletteMode) => (mode.value = m) }
}
