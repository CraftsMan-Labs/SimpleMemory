<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
import { Files } from 'lucide-vue-next'
defineProps<{ data: { label: string } }>()
</script>

<template>
  <div class="kmg-node kmg-node-source">
    <Handle :position="Position.Left" type="target" />
    <Files :size="12" />
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
  border-radius: var(--radius-sm);
  border: 1px dashed var(--border);
  background: var(--surface);
  color: var(--fg-2);
  font-size: 11px;
  max-width: 200px;
}
</style>
