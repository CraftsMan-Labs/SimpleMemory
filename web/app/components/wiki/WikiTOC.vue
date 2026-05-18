<script setup lang="ts">
/**
 * Docs-page sticky table of contents. Derives headings from the rendered markdown HTML.
 * Highlights the closest section via IntersectionObserver.
 */
import { computed, ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps<{ markdown: string; rootEl?: HTMLElement | null }>()

interface Heading { id: string; level: number; text: string }

const headings = computed<Heading[]>(() => {
  const out: Heading[] = []
  for (const line of props.markdown.split('\n')) {
    const m = /^(#{1,3})\s+(.+)$/.exec(line)
    if (!m || !m[1] || !m[2]) continue
    const text = m[2].trim()
    const id = text.toLowerCase().replace(/[^a-z0-9]+/g, '-')
    out.push({ id, level: m[1].length, text })
  }
  return out
})

const active = ref<string | null>(null)
let observer: IntersectionObserver | null = null

const wireObserver = () => {
  observer?.disconnect()
  if (!props.rootEl) return
  const targets = Array.from(props.rootEl.querySelectorAll<HTMLElement>('h1[id], h2[id], h3[id]'))
  if (!targets.length) return
  observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
      if (visible[0]) active.value = visible[0].target.id
    },
    { rootMargin: '0px 0px -70% 0px', threshold: 0.1 },
  )
  for (const t of targets) observer.observe(t)
}

onMounted(wireObserver)
onBeforeUnmount(() => observer?.disconnect())
watch(() => props.markdown, () => requestAnimationFrame(wireObserver))
</script>

<template>
  <aside class="hidden xl:block sticky top-12">
    <p class="font-mono text-[10px] uppercase tracking-widest text-meta mb-3">On this page</p>
    <ul class="space-y-1.5 text-sm">
      <li v-for="h in headings" :key="h.id">
        <a
          :href="`#${h.id}`"
          :class="[
            'block transition-colors',
            h.level === 1 ? 'text-fg-2' : h.level === 2 ? 'text-fg-2 pl-3' : 'text-meta pl-6',
            active === h.id ? 'text-accent' : 'hover:text-fg',
          ]"
        >{{ h.text }}</a>
      </li>
      <li v-if="!headings.length" class="text-xs text-meta italic">No headings yet.</li>
    </ul>
  </aside>
</template>
