<script setup lang="ts">
/**
 * ⌘K omnibox. Three modes (find · ask · jump). Visible state is shared via useCommandPalette().
 * - find: vector + keyword search across record types.
 * - ask:  chat thread w/ citations.
 * - jump: client-side fuzzy across loaded workspaces/wiki/canvases.
 */
import { computed, ref, watch } from 'vue'
import Dialog from '@/components/ui/Dialog.vue'
import Tabs from '@/components/ui/Tabs.vue'
import Input from '@/components/ui/Input.vue'
import Kbd from '@/components/ui/Kbd.vue'
import CommandResultRow from './CommandResultRow.vue'
import CommandScopeChip from './CommandScopeChip.vue'
import { useCommandPalette } from '@/composables/useCommandPalette'
import { useSearch, useChat } from '@/composables/useSearch'
import { useWikiList } from '@/composables/useWikiList'
import { useCanvasList } from '@/composables/useCanvas'
import { useProjectBase } from '@/composables/useProjectBase'
import { refDebounced } from '@vueuse/core'
import { Search, MessageSquare, Move } from 'lucide-vue-next'
import type { SearchScope } from '@@/types/api'

const palette = useCommandPalette()
const { current } = useProjectBase()

const tabs = [
  { value: 'find', label: 'Find' },
  { value: 'ask', label: 'Ask' },
  { value: 'jump', label: 'Jump' },
]

const scope = ref<SearchScope>('current_project')
const inputEl = ref<HTMLInputElement | null>(null)
const debouncedQuery = refDebounced(palette.query, 200)

const search = useSearch()
const chat = useChat()
const { data: wikiList } = useWikiList()
const { data: canvasList } = useCanvasList()
const router = useRouter()

// Run "find" whenever query changes
watch([debouncedQuery, () => palette.mode.value, () => palette.open.value], () => {
  if (!palette.open.value) return
  if (palette.mode.value === 'find' && debouncedQuery.value.trim()) {
    search.mutate({ query: debouncedQuery.value, scope: scope.value, limit: 12 })
  }
})

const jumpResults = computed(() => {
  const q = debouncedQuery.value.toLowerCase().trim()
  const wiki = (wikiList.value?.pages ?? []).map((p) => ({
    id: p.id, kind: 'wiki', title: p.title, slug: p.slug, snippet: p.summary ?? '',
  }))
  const canvases = (canvasList.value?.canvases ?? []).map((c) => ({
    id: c.id, kind: 'canvas', title: c.title, slug: c.id, snippet: '',
  }))
  const all = [...wiki, ...canvases]
  if (!q) return all.slice(0, 16)
  return all.filter((x) => x.title.toLowerCase().includes(q)).slice(0, 16)
})

const onSubmit = async () => {
  const q = palette.query.value.trim()
  if (!q) return
  if (palette.mode.value === 'ask') {
    await chat.ask(q, scope.value)
    palette.query.value = ''
  }
}

watch(() => palette.open.value, (open) => {
  if (open) setTimeout(() => inputEl.value?.focus(), 30)
})

const navigate = (href: string) => {
  router.push(href)
  palette.hide()
}
</script>

<template>
  <Dialog :model-value="palette.open.value" size="xl" @update:model-value="(v) => v ? palette.show(palette.mode.value) : palette.hide()">
    <div class="flex flex-col max-h-[70vh]">
      <header class="flex items-center gap-3 p-4 border-b border-border">
        <component :is="palette.mode.value === 'ask' ? MessageSquare : palette.mode.value === 'jump' ? Move : Search" :size="18" class="text-accent" />
        <input
          ref="inputEl"
          v-model="palette.query.value"
          :placeholder="palette.mode.value === 'ask' ? 'Ask anything…' : palette.mode.value === 'jump' ? 'Jump to page or canvas…' : 'Search wiki, graph, chunks…'"
          class="flex-1 bg-transparent text-base outline-none placeholder:text-meta"
          @keydown.enter="onSubmit"
        />
        <CommandScopeChip v-model="scope" />
        <Kbd>Esc</Kbd>
      </header>

      <div class="px-4 py-2 border-b border-border">
        <Tabs :model-value="palette.mode.value" :items="tabs" @update:model-value="(v) => palette.setMode(v as any)" />
      </div>

      <div class="flex-1 overflow-y-auto">
        <!-- FIND -->
        <div v-if="palette.mode.value === 'find'" class="divide-y divide-border-soft">
          <div v-if="search.isPending.value" class="p-4 text-sm text-meta">Searching…</div>
          <CommandResultRow
            v-for="r in search.data.value?.results ?? []"
            :key="r.id"
            :title="r.title ?? r.id"
            :snippet="r.snippet ?? ''"
            :kind="r.record_type"
            :score="r.score"
            @click="navigate(r.slug && r.record_type === 'wiki_page' ? `/app/${current?.slug}/wiki/${r.slug}` : '#')"
          />
          <div v-if="!search.isPending.value && !(search.data.value?.results ?? []).length && palette.query.value" class="p-6 text-center text-sm text-meta">
            No results. Try Ask mode for a synthesized answer.
          </div>
        </div>

        <!-- ASK -->
        <div v-else-if="palette.mode.value === 'ask'" class="p-4 space-y-3">
          <div v-for="(m, i) in chat.messages.value" :key="i" class="text-sm">
            <div class="text-[10px] tracking-widest uppercase text-meta font-mono mb-1">{{ m.role }}</div>
            <div :class="m.role === 'user' ? 'text-fg' : 'text-fg-2 whitespace-pre-wrap'">{{ m.text }}</div>
            <div v-if="m.citations?.length" class="mt-1 flex flex-wrap gap-1.5">
              <span v-for="(_c, ci) in m.citations" :key="ci" class="text-[10px] px-1.5 py-0.5 rounded border border-border text-meta">
                [{{ ci + 1 }}]
              </span>
            </div>
          </div>
          <div v-if="chat.pending.value" class="text-sm text-meta italic">Thinking…</div>
          <div v-if="!chat.messages.value.length" class="text-sm text-meta">
            Ask a question grounded in your sources. Press <Kbd>Enter</Kbd> to send.
          </div>
        </div>

        <!-- JUMP -->
        <div v-else class="divide-y divide-border-soft">
          <CommandResultRow
            v-for="r in jumpResults"
            :key="r.id"
            :title="r.title"
            :snippet="r.snippet"
            :kind="r.kind"
            @click="navigate(r.kind === 'wiki' ? `/app/${current?.slug}/wiki/${r.slug}` : `/app/${current?.slug}/canvas/${r.slug}`)"
          />
        </div>
      </div>

      <footer class="border-t border-border p-2 flex items-center justify-between text-[11px] text-meta">
        <div class="flex items-center gap-2">
          <Kbd>↑</Kbd><Kbd>↓</Kbd> navigate · <Kbd>Enter</Kbd> open
        </div>
        <div class="flex items-center gap-2">
          Switch mode <Kbd>Tab</Kbd>
        </div>
      </footer>
    </div>
  </Dialog>
</template>
