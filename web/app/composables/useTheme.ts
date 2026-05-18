/**
 * Skin toggle for the dual design-system strategy.
 * - `framer` drives the workspace shell, graph, canvas, marketing (dark).
 * - `mintlify` drives the wiki reader pane (light).
 *
 * The skin is applied via [data-skin="..."] on the closest scoped wrapper.
 * `app.vue` sets the root skin; local panes can override by wrapping their subtree.
 */
import { useLocalStorage } from '@vueuse/core'

export type Skin = 'framer' | 'mintlify'

const STORAGE_KEY = 'kmg.skin'

export function useTheme() {
  const skin = useLocalStorage<Skin>(STORAGE_KEY, 'framer')
  const setSkin = (next: Skin) => { skin.value = next }
  const toggle = () => setSkin(skin.value === 'framer' ? 'mintlify' : 'framer')
  return { skin, setSkin, toggle }
}
