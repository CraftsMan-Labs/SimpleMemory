<script setup lang="ts">
import { ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { cn } from '@/lib/utils'
defineProps<{ class?: string; align?: 'start' | 'end' }>()
const open = ref(false)
const root = ref<HTMLElement | null>(null)
onClickOutside(root, () => (open.value = false))
</script>

<template>
  <div ref="root" class="relative inline-block">
    <slot name="trigger" :open="open" :toggle="() => (open = !open)" />
    <Transition name="dd">
      <div
        v-if="open"
        :class="cn(
          'absolute z-40 mt-2 min-w-[12rem] surface-raised border border-border p-1 text-sm',
          align === 'end' ? 'right-0' : 'left-0',
          $props.class,
        )"
      >
        <slot :close="() => (open = false)" />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.dd-enter-active, .dd-leave-active { transition: opacity 120ms, transform 120ms cubic-bezier(0.2,0,0,1); }
.dd-enter-from, .dd-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
