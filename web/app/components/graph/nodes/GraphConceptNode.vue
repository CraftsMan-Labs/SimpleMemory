<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
import { Sparkles } from 'lucide-vue-next'
defineProps<{ data: { label: string; type?: string } }>()
</script>

<template>
  <div class="kmg-node kmg-node-concept">
    <Handle :position="Position.Left" type="target" />
    <Sparkles :size="12" />
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
  background: var(--accent);
  color: var(--accent-on);
  font-size: 11px;
  max-width: 200px;
}
</style>
