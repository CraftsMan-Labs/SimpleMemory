<script setup lang="ts">
import Card from '@/components/ui/Card.vue'
import { Filter } from 'lucide-vue-next'

const layer = defineModel<'wiki' | 'semantic' | 'unified'>('layer', { default: 'unified' })
const minConfidence = defineModel<number>('minConfidence', { default: 0 })
</script>

<template>
  <Card padded class="absolute top-4 left-4 w-64 z-10">
    <div class="flex items-center gap-2 mb-3 text-xs font-mono uppercase tracking-widest text-meta">
      <Filter :size="11" /> Filters
    </div>
    <div class="space-y-3">
      <div>
        <label class="block text-[10px] font-mono uppercase text-meta mb-1.5">Layer</label>
        <div class="flex gap-1">
          <button
            v-for="opt in ['wiki', 'semantic', 'unified']"
            :key="opt"
            :class="[
              'flex-1 h-7 rounded-pill text-[10px] font-medium border transition-colors',
              layer === opt ? 'bg-accent text-accent-on border-accent' : 'border-border text-fg-2 hover:text-fg',
            ]"
            @click="layer = opt as any"
          >{{ opt }}</button>
        </div>
      </div>
      <div>
        <label class="block text-[10px] font-mono uppercase text-meta mb-1.5">
          Min confidence · {{ minConfidence.toFixed(2) }}
        </label>
        <input v-model.number="minConfidence" type="range" min="0" max="1" step="0.05" class="w-full accent-[var(--accent)]" />
      </div>
    </div>
  </Card>
</template>
