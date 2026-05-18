<script setup lang="ts">
/**
 * Minimal Reka-style modal. Uses <Teleport> to body + focus trap via tabindex.
 * For v1 the focus-trap is naive (autofocus first focusable on open).
 */
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { cn } from '@/lib/utils'
const props = defineProps<{ modelValue: boolean; size?: 'sm' | 'md' | 'lg' | 'xl'; class?: string }>()
const emit = defineEmits<{ 'update:modelValue': [v: boolean] }>()

const panel = ref<HTMLElement | null>(null)
const close = () => emit('update:modelValue', false)

const onKey = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.modelValue) close()
}

onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))

watch(() => props.modelValue, async (v) => {
  if (!v) return
  await nextTick()
  const first = panel.value?.querySelector<HTMLElement>('[autofocus],input,button,[tabindex]:not([tabindex="-1"])')
  first?.focus()
})

const sizes = { sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-2xl', xl: 'max-w-4xl' }
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-start justify-center p-4 sm:p-8">
        <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="close" />
        <div
          ref="panel"
          role="dialog"
          aria-modal="true"
          :class="cn(
            'relative z-10 mt-[10vh] w-full surface-raised border border-border',
            sizes[size ?? 'md'],
            $props.class,
          )"
        >
          <slot :close="close" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-enter-active, .dialog-leave-active { transition: opacity 150ms cubic-bezier(0.2,0,0,1); }
.dialog-enter-from, .dialog-leave-to { opacity: 0; }
</style>
