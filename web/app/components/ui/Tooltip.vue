<script setup lang="ts">
/**
 * Minimal tooltip — wraps a single child slot; shows on mouseenter after 250ms.
 * Uses <Teleport> so the tip never gets clipped by overflow:hidden parents.
 */
import { ref, onBeforeUnmount } from 'vue'
import { cn } from '@/lib/utils'
defineProps<{ content: string; class?: string; side?: 'top' | 'bottom' | 'left' | 'right' }>()

const open = ref(false)
const pos = ref({ x: 0, y: 0 })
const anchorEl = ref<HTMLElement | null>(null)
let timer: number | null = null

const onEnter = () => {
  if (!anchorEl.value) return
  const rect = anchorEl.value.getBoundingClientRect()
  pos.value = { x: rect.left + rect.width / 2, y: rect.top - 6 }
  timer = window.setTimeout(() => (open.value = true), 250)
}

const onLeave = () => {
  if (timer != null) window.clearTimeout(timer)
  open.value = false
}

onBeforeUnmount(() => {
  if (timer != null) window.clearTimeout(timer)
})
</script>

<template>
  <span ref="anchorEl" class="inline-block" @mouseenter="onEnter" @mouseleave="onLeave" @focus="onEnter" @blur="onLeave">
    <slot />
  </span>
  <Teleport to="body">
    <Transition name="tip">
      <div
        v-if="open"
        :class="cn(
          'fixed z-50 px-2 py-1 text-[10px] uppercase tracking-widest font-mono rounded border border-border bg-surface text-fg-2 pointer-events-none',
          $props.class,
        )"
        :style="{ left: `${pos.x}px`, top: `${pos.y}px`, transform: 'translate(-50%, -100%)' }"
      >{{ content }}</div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.tip-enter-active, .tip-leave-active { transition: opacity 150ms; }
.tip-enter-from, .tip-leave-to { opacity: 0; }
</style>
