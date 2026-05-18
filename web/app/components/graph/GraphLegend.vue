<script setup lang="ts">
import Card from '@/components/ui/Card.vue'
import { FileText, Sparkles, Files, Quote } from 'lucide-vue-next'

const items = [
  { icon: FileText, label: 'Wiki page', tone: 'accent-outline' },
  { icon: Sparkles, label: 'Concept', tone: 'accent-fill' },
  { icon: Files, label: 'Source', tone: 'dashed' },
  { icon: Quote, label: 'Chunk', tone: 'muted' },
]
</script>

<template>
  <Card padded class="absolute bottom-12 left-4 w-48 z-10 text-xs">
    <p class="font-mono text-[10px] uppercase tracking-widest text-meta mb-2">Legend</p>
    <ul class="space-y-1.5">
      <li v-for="item in items" :key="item.label" class="flex items-center gap-2">
        <component :is="item.icon" :size="11" :class="item.tone === 'accent-fill' ? 'text-accent' : 'text-fg-2'" />
        <span class="text-fg-2">{{ item.label }}</span>
      </li>
    </ul>
  </Card>
</template>
