<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import WikiPageHeader from '@/components/wiki/WikiPageHeader.vue'
import WikiReader from '@/components/wiki/WikiReader.vue'
import WikiEditor from '@/components/wiki/WikiEditor.vue'
import WikiTOC from '@/components/wiki/WikiTOC.vue'
import BacklinksPanel from '@/components/panels/BacklinksPanel.vue'
import RelatedPanel from '@/components/panels/RelatedPanel.vue'
import EvidencePanel from '@/components/panels/EvidencePanel.vue'
import LocalGraphPanel from '@/components/panels/LocalGraphPanel.vue'
import Button from '@/components/ui/Button.vue'
import { useWikiPageBySlug, useUpdateWikiPage } from '@/composables/useWikiPage'
import { useToast } from '@/composables/useToast'

definePageMeta({ layout: 'app' })

const route = useRoute()
const slug = computed(() => route.params.slug as string)
const { data: page } = useWikiPageBySlug(slug)

const mode = ref<'read' | 'edit'>('read')
const draft = ref('')
const dirty = ref(false)
const evidenceOpenIndex = ref<number | null>(null)
const readerRoot = ref<HTMLElement | null>(null)

watch(page, (p) => {
  if (p && !dirty.value) draft.value = p.markdown
}, { immediate: true })

watch(draft, (v) => {
  if (page.value && v !== page.value.markdown) dirty.value = true
})

const update = useUpdateWikiPage()
const { push } = useToast()
const onSave = async () => {
  if (!page.value) return
  await update.mutateAsync({ id: page.value.id, body: { markdown: draft.value } })
  dirty.value = false
  push({ title: 'Saved', tone: 'accent', timeoutMs: 1500 })
}

const pageId = computed(() => page.value?.id ?? '')
const owningNodeId = computed(() => {
  const meta = page.value?.metadata as Record<string, unknown> | undefined
  return (meta?.owning_graph_node_id as string | undefined) ?? undefined
})
</script>

<template>
  <div v-if="page" class="grid grid-cols-1 xl:grid-cols-[1fr_200px] gap-8 max-w-5xl mx-auto px-8 py-12 pb-32">
    <div>
      <WikiPageHeader
        :page="page"
        :mode="mode"
        @update:mode="(v) => (mode = v)"
        @regenerate="() => push({ title: 'Regenerate queued', tone: 'accent' })"
      />

      <WikiReader
        v-if="mode === 'read'"
        :markdown="draft"
        @open-evidence="(i) => (evidenceOpenIndex = i)"
        @root-ready="(el) => (readerRoot = el)"
      />
      <div v-else>
        <WikiEditor v-model="draft" />
        <div class="mt-4 flex items-center justify-end gap-2">
          <span v-if="dirty" class="text-xs text-meta">Unsaved changes</span>
          <Button variant="ghost" size="sm" @click="() => (mode = 'read')">Cancel</Button>
          <Button variant="accent" size="sm" :disabled="!dirty || update.isPending.value" @click="onSave">Save</Button>
        </div>
      </div>
    </div>

    <WikiTOC v-if="mode === 'read'" :markdown="draft" :root-el="readerRoot" />

    <Teleport to="#kmg-right-rail" defer>
      <BacklinksPanel v-if="pageId" :page-id="pageId" />
      <RelatedPanel v-if="pageId" :page-id="pageId" />
      <EvidencePanel v-if="pageId" :page-id="pageId" :open-index="evidenceOpenIndex" />
      <LocalGraphPanel :node-id="owningNodeId" />
    </Teleport>
  </div>
</template>
