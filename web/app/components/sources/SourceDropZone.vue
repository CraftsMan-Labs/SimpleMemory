<script setup lang="ts">
/**
 * Drag-and-drop + paste URL. Triggers presigned upload + confirm.
 * Emits the returned job id so callers can subscribe to ingestion progress.
 */
import { ref } from 'vue'
import { Upload, LinkIcon } from 'lucide-vue-next'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import { useSourceIngest, useCreateUrlSource } from '@/composables/useSourceIngest'
import { useToast } from '@/composables/useToast'

const emit = defineEmits<{ ingested: [jobId: string] }>()

const { ingest, progress } = useSourceIngest()
const createUrl = useCreateUrlSource()
const { push } = useToast()

const dragging = ref(false)
const url = ref('')
const busy = ref(false)

const onDrop = async (e: DragEvent) => {
  e.preventDefault()
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) await ingestFile(file)
}

const onPick = async (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) await ingestFile(file)
}

const ingestFile = async (file: File) => {
  busy.value = true
  try {
    const res = await ingest(file, { title: file.name })
    push({ title: 'Ingesting', message: file.name, tone: 'accent' })
    emit('ingested', res.job_id)
  } catch (e) {
    push({ title: 'Upload failed', message: String(e), tone: 'danger' })
  } finally {
    busy.value = false
  }
}

const submitUrl = async () => {
  if (!url.value) return
  busy.value = true
  try {
    await createUrl.mutateAsync({ url: url.value })
    push({ title: 'URL queued', message: url.value, tone: 'accent' })
    url.value = ''
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="space-y-4">
    <label
      :class="[
        'block border border-dashed border-border rounded-lg p-8 text-center cursor-pointer transition-colors',
        dragging && 'border-accent bg-[color-mix(in_oklab,var(--accent),transparent_95%)]',
      ]"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop="onDrop"
    >
      <input type="file" class="hidden" @change="onPick" />
      <Upload :size="20" class="text-accent mx-auto mb-3" />
      <p class="text-fg text-sm">Drop a PDF, markdown, or text file</p>
      <p class="text-meta text-xs mt-1">or click to choose · ingestion starts automatically</p>
      <div v-if="progress > 0 && progress < 100" class="mt-4 h-1 bg-surface rounded-pill overflow-hidden">
        <div class="h-full bg-accent transition-all" :style="{ width: `${progress}%` }" />
      </div>
    </label>

    <div class="flex items-center gap-2">
      <LinkIcon :size="14" class="text-meta shrink-0" />
      <Input v-model="url" placeholder="…or paste a URL" @keydown.enter="submitUrl" />
      <Button variant="outline" size="sm" :disabled="!url || busy" @click="submitUrl">Add</Button>
    </div>
  </div>
</template>
