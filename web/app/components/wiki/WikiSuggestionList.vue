<script setup lang="ts">
/** Floating list shown by the Tiptap Suggestion plugin during [[autocomplete. */
import { ref, watch } from 'vue'

const props = defineProps<{
  items: Array<{ title: string; slug: string }>
  command: (item: { title: string; slug: string }) => void
}>()

const selected = ref(0)

watch(() => props.items, () => { selected.value = 0 })

const onSelect = (idx: number) => {
  const item = props.items[idx]
  if (item) props.command(item)
}

// Expose handler for Tiptap onKeyDown
defineExpose({
  onKeyDown: ({ event }: { event: KeyboardEvent }) => {
    if (event.key === 'ArrowDown') {
      selected.value = (selected.value + 1) % Math.max(props.items.length, 1)
      return true
    }
    if (event.key === 'ArrowUp') {
      selected.value = (selected.value - 1 + props.items.length) % Math.max(props.items.length, 1)
      return true
    }
    if (event.key === 'Enter') {
      onSelect(selected.value)
      return true
    }
    return false
  },
})
</script>

<template>
  <div class="surface-raised border border-border min-w-[16rem] max-w-sm p-1 text-sm">
    <p class="px-2 py-1 text-[10px] uppercase tracking-widest text-meta font-mono">Insert link</p>
    <button
      v-for="(item, i) in items"
      :key="item.slug"
      :class="[
        'flex flex-col items-start w-full text-left px-2 py-1.5 rounded',
        i === selected ? 'bg-surface text-fg' : 'text-fg-2 hover:bg-surface',
      ]"
      @click="onSelect(i)"
    >
      <span class="truncate">{{ item.title }}</span>
      <span class="text-[10px] text-meta font-mono truncate">{{ item.slug }}</span>
    </button>
    <p v-if="!items.length" class="px-2 py-1.5 text-xs text-meta italic">No matches — press Enter to create</p>
  </div>
</template>
