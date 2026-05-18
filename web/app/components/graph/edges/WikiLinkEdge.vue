<script setup lang="ts">
import { BaseEdge, getBezierPath, type EdgeProps } from '@vue-flow/core'
import { computed } from 'vue'

const props = defineProps<EdgeProps>()

const path = computed(() => {
  const [p] = getBezierPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    sourcePosition: props.sourcePosition,
    targetX: props.targetX,
    targetY: props.targetY,
    targetPosition: props.targetPosition,
  })
  return p
})
</script>

<template>
  <BaseEdge :id="id" :path="path" :style="{ stroke: 'var(--accent)', strokeDasharray: '4 4', opacity: 0.6 }" />
</template>
