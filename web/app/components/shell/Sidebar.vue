<script setup lang="ts">
import SidebarBaseSwitcher from './SidebarBaseSwitcher.vue'
import SidebarTree from './SidebarTree.vue'
import SidebarSection from './SidebarSection.vue'
import { useWikiList } from '@/composables/useWikiList'
import { useSourceList } from '@/composables/useSourceIngest'
import { useCanvasList } from '@/composables/useCanvas'
import { useProjectBase } from '@/composables/useProjectBase'
import { Files, FileText, BookOpen, MapPinned, Layers, Settings, Search } from 'lucide-vue-next'
import { computed } from 'vue'

const { current } = useProjectBase()
const slug = computed(() => current.value?.slug ?? '')

const { data: wikiData } = useWikiList({ sort: 'updated' })
const { data: sourcesData } = useSourceList()
const { data: canvasesData } = useCanvasList()
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="p-4 border-b border-border">
      <SidebarBaseSwitcher />
    </div>

    <nav class="px-2 py-3 border-b border-border space-y-0.5">
      <NuxtLink :to="`/app/${slug}`" class="sidebar-link"><BookOpen :size="14" /> Home</NuxtLink>
      <NuxtLink :to="`/app/${slug}/search`" class="sidebar-link"><Search :size="14" /> Search & Chat</NuxtLink>
      <NuxtLink :to="`/app/${slug}/graph`" class="sidebar-link"><MapPinned :size="14" /> Graph</NuxtLink>
      <NuxtLink :to="`/app/${slug}/canvas`" class="sidebar-link"><Layers :size="14" /> Canvases</NuxtLink>
      <NuxtLink :to="`/app/${slug}/sources`" class="sidebar-link"><Files :size="14" /> Sources</NuxtLink>
      <NuxtLink :to="`/app/${slug}/settings`" class="sidebar-link"><Settings :size="14" /> Settings</NuxtLink>
    </nav>

    <div class="flex-1 overflow-y-auto px-2 py-3 space-y-2">
      <SidebarSection title="Wiki Pages" :count="wikiData?.total">
        <SidebarTree
          :items="(wikiData?.pages ?? []).map((p) => ({
            id: p.id,
            label: p.title,
            href: `/app/${slug}/wiki/${p.slug}`,
            icon: 'FileText',
            freshness: p.freshness_status,
          }))"
        />
      </SidebarSection>

      <SidebarSection title="Sources" :count="sourcesData?.total">
        <SidebarTree
          :items="(sourcesData?.sources ?? []).map((s) => ({
            id: s.id,
            label: s.title,
            href: `/app/${slug}/sources/${s.id}`,
            icon: 'Files',
            status: s.status,
          }))"
        />
      </SidebarSection>

      <SidebarSection title="Canvases" :count="canvasesData?.total">
        <SidebarTree
          :items="(canvasesData?.canvases ?? []).map((c) => ({
            id: c.id,
            label: c.title,
            href: `/app/${slug}/canvas/${c.id}`,
            icon: 'Layers',
          }))"
        />
      </SidebarSection>
    </div>
  </div>
</template>

<style scoped>
.sidebar-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 6px 12px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  color: var(--fg-2);
  text-decoration: none;
  transition: background 150ms, color 150ms;
}
.sidebar-link:hover { background: var(--surface); color: var(--fg); }
.sidebar-link.router-link-active { background: var(--surface); color: var(--fg); }
</style>
