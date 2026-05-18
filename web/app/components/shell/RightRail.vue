<script setup lang="ts">
/**
 * Tabbed right-rail host. Pages teleport their contextual content into the
 * `#kmg-right-rail` target, so any route can populate the rail without
 * coupling layout markup.
 */
import { ref, provide } from 'vue'
import Tabs from '@/components/ui/Tabs.vue'

const active = ref('panels')
const items = [{ value: 'panels', label: 'Panels' }]
provide('rightRailActive', active)
</script>

<template>
  <div class="flex flex-col h-full w-full">
    <header class="border-b border-border p-3">
      <Tabs v-model="active" :items="items" class="w-full" />
    </header>
    <div id="kmg-right-rail" class="flex-1 overflow-y-auto p-3 space-y-6" />
  </div>
</template>
