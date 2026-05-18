<script setup lang="ts">
import { BaseEdge, getBezierPath, EdgeLabelRenderer, type EdgeProps } from '@vue-flow/core'
import { computed } from 'vue'

const props = defineProps<EdgeProps>()

const path = computed(() => {
  const [p, lx, ly] = getBezierPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    sourcePosition: props.sourcePosition,
    targetX: props.targetX,
    targetY: props.targetY,
    targetPosition: props.targetPosition,
  })
  return { d: p, lx, ly }
})
</script>

<template>
  <BaseEdge :id="id" :path="path.d" :style="{ stroke: 'var(--border)', strokeWidth: 1 }" />
  <EdgeLabelRenderer v-if="label">
    <div
      class="nodrag nopan"
      :style="{
        position: 'absolute',
        transform: `translate(-50%, -50%) translate(${path.lx}px, ${path.ly}px)`,
        background: 'var(--surface)',
        padding: '2px 6px',
        borderRadius: '4px',
        fontSize: '10px',
        color: 'var(--meta)',
        fontFamily: 'var(--font-mono)',
        pointerEvents: 'all',
      }"
    >{{ label }}</div>
  </EdgeLabelRenderer>
</template>
