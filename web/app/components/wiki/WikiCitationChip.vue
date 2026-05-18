<script setup lang="ts">
/**
 * Inline [¹] citation chip. Emits its evidence id when clicked so the
 * EvidencePanel can open the matching chunk.
 */
defineProps<{ index: number; evidenceId?: string }>()
const emit = defineEmits<{ open: [evidenceId?: string] }>()
</script>

<template>
  <button
    type="button"
    class="inline-flex items-center justify-center align-super h-4 min-w-4 px-1 text-[10px] font-mono rounded border border-border text-meta hover:text-accent hover:border-accent transition-colors"
    @click="emit('open', evidenceId)"
  >[{{ index }}]</button>
</template>
