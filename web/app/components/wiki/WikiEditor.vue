<script setup lang="ts">
/**
 * Real Tiptap v3 markdown editor with [[wikilink]] autocomplete + suggestion popover.
 * Markdown is the source of truth on the backend; tiptap-markdown handles round-trip.
 * Suggestion popover renders WikiSuggestionList; selections call WikiLink.insertWikiLink.
 */
import { onBeforeUnmount, onMounted, ref, watch, h, render, type Ref } from 'vue'
import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { Markdown } from 'tiptap-markdown'
import { WikiLink } from './WikiLinkExtension'
import WikiSuggestionList from './WikiSuggestionList.vue'
import { apiClient } from '@/lib/api'
import type { WikiPageListResponse } from '@@/types/api'

interface MarkdownStorage { getMarkdown: () => string }
const getMarkdown = (ed: Editor): string => {
  const store = ed.storage as unknown as { markdown?: MarkdownStorage }
  return store.markdown?.getMarkdown() ?? ed.getHTML()
}

const model = defineModel<string>({ required: true })
const root = ref<HTMLElement | null>(null)
const editor = ref<Editor | null>(null) as Ref<Editor | null>

const fetchPages = async (q: string) => {
  if (!q.trim()) return []
  const res = await apiClient<WikiPageListResponse>('/wiki/pages', { query: { q, limit: 8 } })
  return res.pages
}

const mountSuggestion = () => {
  let host: HTMLElement | null = null
  let exposed: { onKeyDown?: (k: { event: KeyboardEvent }) => boolean } = {}

  const teardown = () => {
    if (host) {
      render(null, host)
      host.remove()
      host = null
    }
  }

  const renderList = (props: { clientRect?: () => DOMRect | null; items: unknown[]; command: (item: unknown) => void }) => {
    if (!host) return
    const rect = props.clientRect?.()
    if (rect) {
      host.style.left = `${rect.left + window.scrollX}px`
      host.style.top = `${rect.bottom + window.scrollY + 4}px`
    }
    const vNode = h(WikiSuggestionList, {
      items: props.items as { title: string; slug: string }[],
      command: props.command as (item: { title: string; slug: string }) => void,
      ref: (el: unknown) => {
        if (el) exposed = el as { onKeyDown?: (k: { event: KeyboardEvent }) => boolean }
      },
    })
    render(vNode, host)
  }

  return {
    onStart: (props: { clientRect?: () => DOMRect | null; items: unknown[]; command: (item: unknown) => void }) => {
      host = document.createElement('div')
      host.style.position = 'absolute'
      host.style.zIndex = '1000'
      document.body.appendChild(host)
      renderList(props)
    },
    onUpdate: renderList,
    onKeyDown: ({ event }: { event: KeyboardEvent }) => exposed.onKeyDown?.({ event }) ?? false,
    onExit: teardown,
  }
}

onMounted(() => {
  editor.value = new Editor({
    element: root.value!,
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: '# Page title\n\nWrite markdown. Type [[ to link another page.',
      }),
      Markdown.configure({ html: false, linkify: true, breaks: true }),
      // Cast to any: Tiptap's SuggestionProps generic over our shape is structurally
      // compatible but the strict generic check rejects it.
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (WikiLink as any).configure({
        fetchPages,
        suggestionRender: mountSuggestion,
        onClick: () => {},
      }),
    ],
    content: model.value,
    onUpdate: ({ editor: ed }) => {
      const md = getMarkdown(ed)
      if (md !== model.value) model.value = md
    },
    editorProps: {
      attributes: {
        class: 'tiptap focus:outline-none min-h-[60vh]',
      },
    },
  })
})

watch(model, (next) => {
  const ed = editor.value
  if (!ed) return
  const current = getMarkdown(ed)
  if (next !== current) ed.commands.setContent(next, { emitUpdate: false })
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<template>
  <div
    ref="root"
    class="tiptap-host bg-surface text-fg rounded-md p-6 border border-border focus-within:border-accent"
  />
</template>

<style scoped>
.tiptap-host :deep(.tiptap) {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--leading-body);
  color: var(--fg-2);
}
.tiptap-host :deep(.tiptap h1) { font-size: var(--text-3xl); color: var(--fg); margin-bottom: var(--space-4); }
.tiptap-host :deep(.tiptap h2) { font-size: var(--text-2xl); color: var(--fg); margin-top: var(--space-6); margin-bottom: var(--space-3); }
.tiptap-host :deep(.tiptap h3) { font-size: var(--text-xl); color: var(--fg); margin-top: var(--space-5); margin-bottom: var(--space-2); }
.tiptap-host :deep(.tiptap p)  { margin-bottom: var(--space-4); }
.tiptap-host :deep(.tiptap ul) { padding-left: var(--space-5); margin-bottom: var(--space-4); list-style: disc; }
.tiptap-host :deep(.tiptap ol) { padding-left: var(--space-5); margin-bottom: var(--space-4); list-style: decimal; }
.tiptap-host :deep(.tiptap code) {
  font-family: var(--font-mono);
  background: var(--surface-warm);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: 0.9em;
}
.tiptap-host :deep(.tiptap pre) {
  font-family: var(--font-mono);
  background: var(--surface-warm);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin-bottom: var(--space-4);
}
.tiptap-host :deep(.tiptap a.wikilink) {
  color: var(--fg);
  border-bottom: 1px solid var(--accent);
  text-decoration: none;
  padding-bottom: 1px;
  transition: color 150ms;
}
.tiptap-host :deep(.tiptap a.wikilink:hover) { color: var(--accent); }
.tiptap-host :deep(.tiptap .is-editor-empty:first-child::before) {
  color: var(--meta);
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
</style>
