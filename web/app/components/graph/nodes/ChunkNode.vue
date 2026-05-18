<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
import { Quote } from 'lucide-vue-next'
defineProps<{ data: { label: string } }>()
</script>

<template>
  <div class="kmg-node kmg-node-chunk">
    <Handle :position="Position.Left" type="target" />
    <Quote :size="11" />
    <span class="truncate">{{ data.label }}</span>
    <Handle :position="Position.Right" type="source" />
  </div>
</template>

<style scoped>
.kmg-node {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  background: transparent;
  border: 1px solid var(--border-soft);
  color: var(--muted);
  font-size: 10px;
  font-family: var(--font-mono);
  max-width: 180px;
}
</style>
