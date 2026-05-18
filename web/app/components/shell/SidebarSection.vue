<script setup lang="ts">
import { ref } from 'vue'
import { ChevronDown, ChevronRight } from 'lucide-vue-next'
defineProps<{ title: string; count?: number }>()
const open = ref(true)
</script>

<template>
  <section>
    <button
      class="flex items-center gap-1.5 w-full px-2 py-1 text-[10px] tracking-widest text-meta font-mono uppercase hover:text-fg-2"
      @click="open = !open"
    >
      <component :is="open ? ChevronDown : ChevronRight" :size="11" />
      <span class="flex-1 text-left">{{ title }}</span>
      <span v-if="count != null">{{ count }}</span>
    </button>
    <div v-if="open" class="mt-0.5">
      <slot />
    </div>
  </section>
</template>
