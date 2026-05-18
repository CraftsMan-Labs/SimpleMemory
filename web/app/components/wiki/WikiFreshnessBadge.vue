<script setup lang="ts">
import Badge from '@/components/ui/Badge.vue'
import type { FreshnessStatus } from '@@/types/api'
const props = defineProps<{ status: FreshnessStatus }>()
const variant = () => {
  if (props.status === 'fresh') return 'success'
  if (props.status === 'stale' || props.status === 'outdated') return 'warn'
  return 'default'
}
</script>

<template>
  <Badge :variant="variant()">{{ status }}</Badge>
</template>
