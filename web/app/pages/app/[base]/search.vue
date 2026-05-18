<script setup lang="ts">
/** Full-page chat history. The ⌘K palette is for quick asks; this is for sustained threads. */
import { ref } from 'vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { useChat } from '@/composables/useSearch'

definePageMeta({ layout: 'app' })

const { messages, pending, ask, reset } = useChat()
const draft = ref('')
const send = async () => {
  if (!draft.value.trim()) return
  const q = draft.value
  draft.value = ''
  await ask(q)
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-8 py-12 pb-32">
    <header class="mb-8 flex items-end justify-between">
      <div>
        <p class="font-mono text-xs uppercase tracking-widest text-accent mb-2">Chat</p>
        <h1 class="text-display text-fg text-3xl">Ask your vault.</h1>
      </div>
      <Button v-if="messages.length" variant="ghost" size="sm" @click="reset">New thread</Button>
    </header>

    <div class="space-y-3 mb-8">
      <Card v-for="(m, i) in messages" :key="i" padded>
        <div class="font-mono text-[10px] uppercase tracking-widest text-meta mb-2">{{ m.role }}</div>
        <div :class="m.role === 'user' ? 'text-fg' : 'text-fg-2 whitespace-pre-wrap'">{{ m.text }}</div>
        <div v-if="m.citations?.length" class="mt-3 flex flex-wrap gap-1.5">
          <span v-for="(_c, ci) in m.citations" :key="ci" class="text-[10px] px-1.5 py-0.5 rounded border border-border text-meta">
            [{{ ci + 1 }}]
          </span>
        </div>
      </Card>
      <p v-if="pending" class="text-sm text-meta italic">Thinking…</p>
    </div>

    <div class="sticky bottom-12 flex items-center gap-2 surface-raised p-2">
      <Input v-model="draft" placeholder="Ask anything grounded in your sources…" @keydown.enter="send" />
      <Button variant="accent" :disabled="pending || !draft.trim()" @click="send">Ask</Button>
    </div>
  </div>
</template>
