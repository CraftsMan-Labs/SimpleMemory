<script setup lang="ts">
/** Lightweight toaster — no external dep. Subscribe via useToast(). */
import { computed } from 'vue'
import { useToast } from '@/composables/useToast'
import { cn } from '@/lib/utils'
const { toasts, dismiss } = useToast()
const list = computed(() => toasts.value)
</script>

<template>
  <Teleport to="body">
    <div class="fixed bottom-6 right-6 z-[60] flex flex-col gap-2 max-w-sm">
      <TransitionGroup name="toast">
        <div
          v-for="t in list"
          :key="t.id"
          :class="cn(
            'surface-raised border border-border px-4 py-3 text-sm flex items-start gap-3',
            t.tone === 'accent' && 'border-l-2 border-l-accent',
            t.tone === 'warn' && 'border-l-2 border-l-[var(--warn)]',
            t.tone === 'danger' && 'border-l-2 border-l-[var(--danger)]',
          )"
        >
          <div class="flex-1">
            <div v-if="t.title" class="font-medium text-fg">{{ t.title }}</div>
            <div v-if="t.message" class="text-muted">{{ t.message }}</div>
          </div>
          <button class="text-meta hover:text-fg" @click="dismiss(t.id)">×</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 200ms cubic-bezier(0.2,0,0,1); }
.toast-enter-from { opacity: 0; transform: translateX(20px); }
.toast-leave-to { opacity: 0; transform: translateX(20px); }
</style>
