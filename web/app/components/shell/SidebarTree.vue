<script setup lang="ts">
/**
 * Flat list rendering for sidebar sections. Renders freshness badges + status indicators inline.
 */
import { FileText, Files, Layers } from 'lucide-vue-next'

defineProps<{
  items: Array<{
    id: string
    label: string
    href: string
    icon?: 'FileText' | 'Files' | 'Layers'
    freshness?: string
    status?: string
  }>
}>()

const iconMap = { FileText, Files, Layers }
</script>

<template>
  <ul class="space-y-px">
    <li v-for="item in items" :key="item.id">
      <NuxtLink
        :to="item.href"
        :class="[
          'group flex items-center gap-2 pl-3 pr-2 py-1 text-sm rounded-md text-fg-2 hover:bg-surface hover:text-fg transition-colors',
          item.freshness === 'stale' || item.freshness === 'outdated' ? 'border-l-2 border-l-[color-mix(in_oklab,var(--warn),transparent_60%)]' : '',
        ]"
      >
        <component :is="iconMap[item.icon ?? 'FileText']" :size="12" class="text-meta shrink-0" />
        <span class="truncate flex-1">{{ item.label }}</span>
        <span v-if="item.status === 'pending' || item.status === 'running'" class="pulse-dot" />
      </NuxtLink>
    </li>
    <li v-if="!items.length" class="px-3 py-1 text-xs text-meta italic">empty</li>
  </ul>
</template>
