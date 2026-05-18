<script setup lang="ts">
/**
 * Renders markdown in the Mintlify light skin.
 *  - [[Wiki Link]] → router anchor + hover popover (250ms)
 *  - [^n] inline footnotes → clickable citation chips → emits open-evidence
 *  - Heading anchors so WikiTOC can observe.
 * Markdown is rendered directly; the worker emits a careful subset, so we don't
 * pull in markdown-it for v1.
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useProjectBase } from '@/composables/useProjectBase'
import WikiLinkPopover from './WikiLinkPopover.vue'

const props = defineProps<{ markdown: string }>()
const emit = defineEmits<{ openEvidence: [index: number]; rootReady: [el: HTMLElement] }>()

const { current } = useProjectBase()

const escape = (s: string) =>
  s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!))

const slugify = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')

const rendered = computed(() => {
  const baseSlug = current.value?.slug ?? ''
  let md = escape(props.markdown)

  md = md.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, target: string, alias?: string) => {
    const slug = slugify(target.trim())
    const label = (alias ?? target).trim()
    return `<a class="wikilink" data-wikilink="${slug}" href="/app/${baseSlug}/wiki/${slug}">${label}</a>`
  })

  md = md.replace(/\[\^([^\]]+)\]/g, (_, ref: string) => {
    return `<span class="citation-anchor" data-citation="${escape(ref)}"></span>`
  })

  md = md.replace(/^### (.*)$/gm, (_, t: string) => `<h3 id="${slugify(t)}">${t}</h3>`)
  md = md.replace(/^## (.*)$/gm, (_, t: string) => `<h2 id="${slugify(t)}">${t}</h2>`)
  md = md.replace(/^# (.*)$/gm, (_, t: string) => `<h1 id="${slugify(t)}">${t}</h1>`)

  md = md.replace(/(?:^- (.*)(?:\n|$))+?/gm, (match) => {
    const items = match.trim().split(/\n- /).map((x) => x.replace(/^- /, '').trim())
    return '<ul>' + items.map((i) => `<li>${i}</li>`).join('') + '</ul>'
  })

  md = md
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')

  md = md
    .split(/\n{2,}/)
    .map((p) => {
      if (/^<(h1|h2|h3|ul|ol|pre|blockquote)/.test(p.trim())) return p
      return `<p>${p.replace(/\n/g, '<br />')}</p>`
    })
    .join('\n')

  return md
})

const root = ref<HTMLElement | null>(null)
const linkAnchors = ref<HTMLElement[]>([])
const linkSlugs = ref<string[]>([])

const wireDom = () => {
  if (!root.value) return
  linkAnchors.value = Array.from(root.value.querySelectorAll<HTMLElement>('a.wikilink'))
  linkSlugs.value = linkAnchors.value.map((a) => a.getAttribute('data-wikilink') ?? '')

  const anchors = root.value.querySelectorAll<HTMLElement>('span.citation-anchor')
  anchors.forEach((el, i) => {
    el.classList.add('inline-citation')
    el.dataset.idx = String(i + 1)
  })
  emit('rootReady', root.value)
}

const onClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  const citation = target.closest<HTMLElement>('span.citation-anchor')
  if (citation) {
    e.preventDefault()
    const idx = Number(citation.dataset.idx ?? '0')
    emit('openEvidence', idx)
  }
}

onMounted(wireDom)
watch(rendered, () => requestAnimationFrame(wireDom))
onBeforeUnmount(() => {})
</script>

<template>
  <div data-skin="mintlify" class="bg-bg text-fg p-12 rounded-lg">
    <div ref="root" class="wiki-prose" v-html="rendered" @click="onClick" />
    <WikiLinkPopover
      v-for="(anchor, i) in linkAnchors"
      :key="i"
      :slug="linkSlugs[i] ?? ''"
      :anchor="anchor"
    />
  </div>
</template>

<style scoped>
.wiki-prose :deep(h1) { font-size: var(--text-3xl); margin-bottom: var(--space-4); scroll-margin-top: 4rem; }
.wiki-prose :deep(h2) { font-size: var(--text-2xl); margin-top: var(--space-8); margin-bottom: var(--space-3); scroll-margin-top: 4rem; }
.wiki-prose :deep(h3) { font-size: var(--text-xl); margin-top: var(--space-6); margin-bottom: var(--space-2); scroll-margin-top: 4rem; }
.wiki-prose :deep(p)  { font-size: var(--text-base); line-height: var(--leading-body); color: var(--fg-2); margin-bottom: var(--space-4); }
.wiki-prose :deep(ul) { padding-left: var(--space-5); margin-bottom: var(--space-4); list-style: disc; color: var(--fg-2); }
.wiki-prose :deep(li) { margin-bottom: var(--space-1); }
.wiki-prose :deep(code) {
  font-family: var(--font-mono);
  background: var(--surface-warm);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: 0.9em;
}
.wiki-prose :deep(.wikilink) {
  color: var(--fg);
  border-bottom: 1px solid var(--accent);
  text-decoration: none;
  padding-bottom: 1px;
  transition: color 150ms;
  cursor: pointer;
}
.wiki-prose :deep(.wikilink:hover) { color: var(--accent-hover); }
.wiki-prose :deep(strong) { color: var(--fg); }
.wiki-prose :deep(.inline-citation) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: super;
  height: 16px;
  min-width: 16px;
  padding: 0 4px;
  font-size: 10px;
  font-family: var(--font-mono);
  border-radius: 4px;
  border: 1px solid var(--border);
  color: var(--meta);
  cursor: pointer;
  margin: 0 2px;
  transition: color 150ms, border-color 150ms;
}
.wiki-prose :deep(.inline-citation::before) { content: '[' attr(data-idx) ']'; }
.wiki-prose :deep(.inline-citation:hover) { color: var(--accent); border-color: var(--accent); }
</style>
