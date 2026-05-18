<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { cn } from '@/lib/utils'
const props = defineProps<{ modelValue: boolean; side?: 'left' | 'right' | 'bottom'; class?: string }>()
const emit = defineEmits<{ 'update:modelValue': [v: boolean] }>()

const close = () => emit('update:modelValue', false)
const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape' && props.modelValue) close() }
onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))

const sideClass = () => {
  switch (props.side) {
    case 'right': return 'right-0 top-0 h-full w-80 sheet-from-right'
    case 'bottom': return 'left-0 bottom-0 w-full max-h-[80vh] sheet-from-bottom'
    default: return 'left-0 top-0 h-full w-80 sheet-from-left'
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="modelValue" class="fixed inset-0 z-40">
        <div class="absolute inset-0 bg-black/70" @click="close" />
        <aside
          :class="cn(
            'absolute bg-bg border-border overflow-y-auto',
            sideClass(),
            $props.class,
          )"
          role="dialog"
          aria-modal="true"
        >
          <slot :close="close" />
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.overlay-enter-active, .overlay-leave-active { transition: opacity 200ms; }
.overlay-enter-from, .overlay-leave-to { opacity: 0; }
.sheet-from-left { border-right: 1px solid var(--border); }
.sheet-from-right { border-left: 1px solid var(--border); }
.sheet-from-bottom { border-top: 1px solid var(--border); border-radius: var(--radius-lg) var(--radius-lg) 0 0; }
</style>
