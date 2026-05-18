<script setup lang="ts">
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import { useProjectBase } from '@/composables/useProjectBase'
import { useTheme } from '@/composables/useTheme'

definePageMeta({ layout: 'app' })

const { current } = useProjectBase()
const { skin, toggle } = useTheme()
</script>

<template>
  <div class="max-w-2xl mx-auto px-8 py-12 pb-24">
    <header class="mb-8">
      <p class="font-mono text-xs uppercase tracking-widest text-accent mb-2">Settings</p>
      <h1 class="text-display text-fg text-3xl">{{ current?.name ?? 'Project Base' }}</h1>
    </header>

    <Card padded class="mb-4">
      <h3 class="text-fg text-lg mb-2">Slug</h3>
      <p class="text-muted text-sm font-mono">/{{ current?.slug }}</p>
    </Card>

    <Card padded class="mb-4">
      <h3 class="text-fg text-lg mb-2">Theme</h3>
      <p class="text-muted text-sm mb-3">Workspace shell skin · current: <span class="font-mono">{{ skin }}</span></p>
      <Button variant="outline" size="sm" @click="toggle">Toggle skin</Button>
    </Card>

    <Card padded>
      <h3 class="text-fg text-lg mb-2">Default pipeline</h3>
      <p class="text-muted text-sm">{{ (current?.settings as any)?.default_pipeline_id ?? '—' }}</p>
    </Card>
  </div>
</template>
