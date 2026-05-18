<script setup lang="ts">
/**
 * Hover-preview popover for wiki links. Mounts at the cursor anchor, fetches the
 * target page summary, and shows freshness + title + summary. 250ms open delay.
 */
import { ref, watch, onBeforeUnmount } from 'vue'
import { apiClient } from '@/lib/api'
import type { WikiPage } from '@@/types/api'
import WikiFreshnessBadge from './WikiFreshnessBadge.vue'

const props = defineProps<{ slug: string; anchor: HTMLElement | null }>()

const open = ref(false)
const page = ref<WikiPage | null>(null)
const pos = ref({ x: 0, y: 0 })
let openTimer: number | null = null
let closeTimer: number | null = null

const fetchPage = async () => {
  if (!props.slug || page.value?.slug === props.slug) return
  try {
    page.value = await apiClient<WikiPage>(`/wiki/pages/by-slug/${props.slug}`)
  } catch {
    page.value = null
  }
}

const onEnter = () => {
  if (closeTimer != null) window.clearTimeout(closeTimer)
  if (!props.anchor) return
  const rect = props.anchor.getBoundingClientRect()
  pos.value = { x: rect.left, y: rect.bottom + 6 }
  openTimer = window.setTimeout(() => {
    open.value = true
    fetchPage()
  }, 250)
}

const onLeave = () => {
  if (openTimer != null) window.clearTimeout(openTimer)
  closeTimer = window.setTimeout(() => (open.value = false), 150)
}

watch(
  () => props.anchor,
  (el, _, onCleanup) => {
    if (!el) return
    el.addEventListener('mouseenter', onEnter)
    el.addEventListener('mouseleave', onLeave)
    onCleanup(() => {
      el.removeEventListener('mouseenter', onEnter)
      el.removeEventListener('mouseleave', onLeave)
    })
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  if (openTimer != null) window.clearTimeout(openTimer)
  if (closeTimer != null) window.clearTimeout(closeTimer)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="pop">
      <div
        v-if="open && page"
        class="fixed z-50 w-80 surface-raised border border-border p-4 text-sm"
        :style="{ left: `${pos.x}px`, top: `${pos.y}px` }"
        @mouseenter="onEnter"
        @mouseleave="onLeave"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="font-mono text-[10px] uppercase tracking-widest text-meta">{{ page.page_type }}</span>
          <WikiFreshnessBadge :status="page.freshness_status" />
        </div>
        <h4 class="text-fg mb-1">{{ page.title }}</h4>
        <p v-if="page.summary" class="text-muted text-xs line-clamp-3">{{ page.summary }}</p>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.pop-enter-active, .pop-leave-active { transition: opacity 150ms, transform 150ms; }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
