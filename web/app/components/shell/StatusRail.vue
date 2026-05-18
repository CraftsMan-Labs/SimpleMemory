<script setup lang="ts">
import { Activity, Cloud, Sparkles } from 'lucide-vue-next'
import Kbd from '@/components/ui/Kbd.vue'
import { useCommandPalette } from '@/composables/useCommandPalette'
import { useSourceList } from '@/composables/useSourceIngest'
import { computed } from 'vue'

const palette = useCommandPalette()
const { data } = useSourceList()
const active = computed(() =>
  (data.value?.sources ?? []).filter((s) => s.status === 'pending' || s.status === 'running'),
)
</script>

<template>
  <footer
    class="fixed bottom-0 inset-x-0 z-30 h-9 border-t border-border bg-bg/90 backdrop-blur flex items-center justify-between px-4 text-xs text-meta"
  >
    <div class="flex items-center gap-4">
      <button
        class="flex items-center gap-2 hover:text-fg-2 transition-colors"
        @click="palette.show('find')"
      >
        <Sparkles :size="12" class="text-accent" />
        <span>Search & ask anything</span>
        <Kbd>⌘K</Kbd>
      </button>
      <div v-if="active.length" class="flex items-center gap-2">
        <span class="pulse-dot" />
        <span>{{ active.length }} ingesting</span>
      </div>
    </div>
    <div class="flex items-center gap-3">
      <slot />
      <span class="flex items-center gap-1.5"><Cloud :size="11" /> synced</span>
      <span class="flex items-center gap-1.5"><Activity :size="11" /> v3</span>
    </div>
  </footer>
</template>
