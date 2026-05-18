<script setup lang="ts">
import { useProjectBase } from '@/composables/useProjectBase'
import { ChevronsUpDown, Plus, Check } from 'lucide-vue-next'
import Popover from '@/components/ui/Popover.vue'

const { current, list } = useProjectBase()
const router = useRouter()
</script>

<template>
  <Popover class="left-0 w-[15rem]">
    <template #trigger="{ toggle }">
      <button
        class="flex items-center justify-between w-full px-3 py-2 rounded-md hover:bg-surface transition-colors text-left"
        @click="toggle"
      >
        <div class="min-w-0">
          <div class="text-[10px] tracking-widest text-meta font-mono uppercase">Project Base</div>
          <div class="truncate text-sm font-medium text-fg">{{ current?.name ?? 'Select a base…' }}</div>
        </div>
        <ChevronsUpDown :size="14" class="text-meta shrink-0" />
      </button>
    </template>

    <template #default="{ close }">
      <div class="flex flex-col gap-1">
        <button
          v-for="w in list"
          :key="w.id"
          class="flex items-center justify-between px-2 py-1.5 rounded text-left hover:bg-surface text-sm"
          @click="() => { router.push(`/app/${w.slug}`); close() }"
        >
          <span class="truncate">{{ w.name }}</span>
          <Check v-if="current?.id === w.id" :size="14" class="text-accent" />
        </button>
        <hr class="border-border my-1" />
        <button
          class="flex items-center gap-2 px-2 py-1.5 rounded text-left hover:bg-surface text-sm text-accent"
          @click="() => { router.push('/app'); close() }"
        >
          <Plus :size="14" /> New Project Base
        </button>
      </div>
    </template>
  </Popover>
</template>
