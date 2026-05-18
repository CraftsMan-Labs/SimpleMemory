<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
import { FileText } from 'lucide-vue-next'
defineProps<{ data: { label: string; freshness?: string; slug?: string } }>()
</script>

<template>
  <div class="kmg-node kmg-node-wiki">
    <Handle :position="Position.Left" type="target" />
    <FileText :size="12" />
    <span class="truncate">{{ data.label }}</span>
    <Handle :position="Position.Right" type="source" />
  </div>
</template>

<style scoped>
.kmg-node {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--fg);
  font-size: 11px;
  max-width: 200px;
}
.kmg-node-wiki { border-color: color-mix(in oklab, var(--accent), transparent 50%); }
</style>
