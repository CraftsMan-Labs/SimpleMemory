<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
import { Sparkles, Plus, FileText, MapPinned, Files, StickyNote } from 'lucide-vue-next'
const emit = defineEmits<{ aiOrganize: []; addWiki: []; addNode: []; addSource: []; addSticky: [] }>()
defineProps<{ organizing?: boolean }>()
</script>

<template>
  <div class="absolute top-4 right-4 z-10 flex items-center gap-2">
    <Button variant="outline" size="sm" @click="emit('addWiki')"><FileText :size="12" /></Button>
    <Button variant="outline" size="sm" @click="emit('addNode')"><MapPinned :size="12" /></Button>
    <Button variant="outline" size="sm" @click="emit('addSource')"><Files :size="12" /></Button>
    <Button variant="outline" size="sm" @click="emit('addSticky')"><StickyNote :size="12" /></Button>
    <Button variant="accent" size="md" :disabled="organizing" @click="emit('aiOrganize')">
      <Sparkles :size="14" />
      {{ organizing ? 'Organising…' : 'AI organise' }}
    </Button>
  </div>
</template>
