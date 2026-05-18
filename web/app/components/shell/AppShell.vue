<script setup lang="ts">
/**
 * Workspace shell. Three-pane grid that collapses by container width:
 *   ≥1280px  sidebar | main | right rail
 *   1024-1279 sidebar | main (right rail collapses to overlay sheet)
 *   <1024     icon strip | main (sidebar opens as sheet)
 *
 * Provides #default, #right, #status slots. Sidebar is hosted internally.
 */
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import RightRail from './RightRail.vue'
import StatusRail from './StatusRail.vue'
import CommandPalette from '@/components/command/CommandPalette.vue'
import Toast from '@/components/ui/Toast.vue'
import { useShortcuts } from '@/composables/useShortcuts'
import { useCommandPalette } from '@/composables/useCommandPalette'
import { useProjectBase } from '@/composables/useProjectBase'

const palette = useCommandPalette()
const projectBase = useProjectBase()
const router = useRouter()

const sidebarOpen = ref(false)

const baseSlug = () => (projectBase.current.value?.slug ?? '')
const goto = (path: string) => {
  const slug = baseSlug()
  if (!slug) return
  router.push(`/app/${slug}${path}`)
}

useShortcuts({
  onCommandPalette: () => palette.toggle(),
  onGoHome: () => goto(''),
  onGoWiki: () => goto('/wiki'),
  onGoGraph: () => goto('/graph'),
  onGoCanvas: () => goto('/canvas'),
  onGoSearch: () => goto('/search'),
})
</script>

<template>
  <div data-skin="framer" class="cq-shell min-h-screen bg-bg text-fg">
    <div class="grid h-screen grid-cols-1 lg:grid-cols-[260px_1fr] xl:grid-cols-[260px_1fr_320px]">
      <!-- Sidebar (collapses to sheet under 1024px) -->
      <aside
        class="hidden lg:flex h-full border-r border-border bg-bg flex-col overflow-hidden"
        aria-label="Project Base navigation"
      >
        <Sidebar />
      </aside>

      <!-- Sidebar mobile sheet -->
      <Transition name="sheet">
        <div v-if="sidebarOpen" class="fixed inset-0 z-40 lg:hidden">
          <div class="absolute inset-0 bg-black/70" @click="sidebarOpen = false" />
          <aside class="absolute left-0 top-0 h-full w-72 bg-bg border-r border-border flex flex-col">
            <Sidebar />
          </aside>
        </div>
      </Transition>

      <!-- Main pane -->
      <main class="relative h-full overflow-y-auto">
        <slot />
      </main>

      <!-- Right rail (xl up) — pages teleport into #kmg-right-rail -->
      <aside
        class="hidden xl:flex h-full border-l border-border bg-bg overflow-hidden"
        aria-label="Contextual panels"
      >
        <RightRail />
      </aside>
    </div>

    <StatusRail />

    <CommandPalette />
    <Toast />
  </div>
</template>

<style scoped>
.sheet-enter-active, .sheet-leave-active { transition: opacity 200ms; }
.sheet-enter-from, .sheet-leave-to { opacity: 0; }
</style>
