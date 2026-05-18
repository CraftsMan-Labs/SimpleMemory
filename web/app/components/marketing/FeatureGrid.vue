<script setup lang="ts">
import Card from '@/components/ui/Card.vue'
import { FileText, Sparkles, MapPinned, Layers, Quote, Search } from 'lucide-vue-next'

const items = [
  { icon: FileText, title: 'AI-generated wiki', body: 'Sources become readable wiki pages with [[backlinks]] and citations grounded in your evidence.' },
  { icon: MapPinned, title: 'Two graphs, one truth', body: 'Wiki link graph for navigation, semantic graph for reasoning — connected via wiki-graph links.' },
  { icon: Layers, title: 'Infinite canvas', body: 'Drag pages, sources, concepts into freeform layouts. AI organises clusters on demand.' },
  { icon: Search, title: '⌘K everywhere', body: 'One omnibox: search, ask, jump. Cite-grounded answers, never hallucinated.' },
  { icon: Quote, title: 'Evidence-first', body: 'Every claim links back to a chunk and the original source page.' },
  { icon: Sparkles, title: 'Freshness as garden', body: 'Pages age. KMG flags what needs reading or regenerating.' },
]
</script>

<template>
  <section class="max-w-[var(--container-max)] mx-auto px-6 py-24">
    <h2 class="text-3xl text-fg mb-12 text-display">Built for dwelling, not visiting.</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <Card v-for="item in items" :key="item.title" padded class="hover:border-accent transition-colors">
        <component :is="item.icon" :size="20" class="text-accent mb-4" />
        <h3 class="text-fg text-lg font-medium mb-2">{{ item.title }}</h3>
        <p class="text-muted text-sm leading-relaxed">{{ item.body }}</p>
      </Card>
    </div>
  </section>
</template>
