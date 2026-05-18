<script setup lang="ts">
import Popover from '@/components/ui/Popover.vue'
import { Globe2, FolderTree, Users } from 'lucide-vue-next'
import type { SearchScope } from '@@/types/api'

const model = defineModel<SearchScope>({ required: true })

const options: Array<{ value: SearchScope; label: string; icon: any }> = [
  { value: 'current_project', label: 'Current base', icon: FolderTree },
  { value: 'all_projects', label: 'All my bases', icon: Globe2 },
  { value: 'shared_projects', label: 'Shared', icon: Users },
]

const current = () => options.find((o) => o.value === model.value) ?? options[0]!
</script>

<template>
  <Popover>
    <template #trigger="{ toggle }">
      <button
        class="flex items-center gap-1.5 px-2.5 py-1 rounded-pill border border-border text-xs text-fg-2 hover:text-fg hover:border-accent transition-colors"
        @click="toggle"
      >
        <component :is="current().icon" :size="11" />
        {{ current().label }}
      </button>
    </template>
    <template #default="{ close }">
      <button
        v-for="opt in options"
        :key="opt.value"
        class="flex items-center gap-2 w-full px-2 py-1.5 rounded text-left hover:bg-surface text-sm"
        @click="() => { model = opt.value; close() }"
      >
        <component :is="opt.icon" :size="12" />
        {{ opt.label }}
      </button>
    </template>
  </Popover>
</template>
