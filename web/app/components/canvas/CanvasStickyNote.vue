<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'
defineProps<{ data: { label: string; color?: string } }>()
const model = defineModel<string>('text', { default: '' })
</script>

<template>
  <div class="sticky-note">
    <Handle :position="Position.Top" type="target" />
    <textarea
      v-model="model"
      class="bg-transparent outline-none resize-none w-full h-full text-sm leading-snug"
      :placeholder="data.label || 'Note…'"
    />
    <Handle :position="Position.Bottom" type="source" />
  </div>
</template>

<style scoped>
.sticky-note {
  width: 180px;
  height: 140px;
  padding: 10px;
  background: color-mix(in oklab, var(--warn), white 70%);
  color: #111;
  border-radius: var(--radius-sm);
  box-shadow: var(--elev-raised);
  font-family: var(--font-body);
  transform: rotate(-1deg);
}
</style>
