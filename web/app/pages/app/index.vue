<script setup lang="ts">
/** Project Base picker / "home". List of bases + create new. */
import { ref } from 'vue'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Dialog from '@/components/ui/Dialog.vue'
import { useWorkspaceList, useCreateWorkspace } from '@/composables/useWorkspaceApi'
import { Plus, FolderOpen } from 'lucide-vue-next'
import { useToast } from '@/composables/useToast'

definePageMeta({ layout: 'default' })

const { data, isLoading } = useWorkspaceList()
const create = useCreateWorkspace()
const router = useRouter()
const { push } = useToast()

const newOpen = ref(false)
const newName = ref('')
const newSlug = ref('')

const onCreate = async () => {
  if (!newName.value || !newSlug.value) return
  const ws = await create.mutateAsync({ name: newName.value, slug: newSlug.value })
  push({ title: 'Project Base created', message: ws.name, tone: 'accent' })
  newOpen.value = false
  newName.value = ''
  newSlug.value = ''
  router.push(`/app/${ws.slug}`)
}
</script>

<template>
  <div data-skin="framer" class="min-h-screen bg-bg text-fg">
    <div class="max-w-3xl mx-auto px-6 py-20">
      <div class="flex items-end justify-between mb-12">
        <div>
          <p class="font-mono text-xs uppercase tracking-widest text-accent mb-2">Project Bases</p>
          <h1 class="text-3xl text-display">Choose your vault.</h1>
        </div>
        <Button variant="accent" @click="newOpen = true"><Plus :size="14" /> New base</Button>
      </div>

      <div v-if="isLoading" class="text-meta">Loading…</div>
      <div v-else-if="!data?.workspaces.length" class="surface-card p-12 text-center">
        <FolderOpen :size="36" class="text-meta mx-auto mb-4" />
        <p class="text-fg mb-2">No Project Bases yet.</p>
        <p class="text-muted text-sm mb-6">Each base is an isolated AI-generated Obsidian vault.</p>
        <Button variant="accent" @click="newOpen = true"><Plus :size="14" /> Create your first base</Button>
      </div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <NuxtLink v-for="w in data.workspaces" :key="w.id" :to="`/app/${w.slug}`">
          <Card padded class="hover:border-accent transition-colors h-full">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-fg text-lg">{{ w.name }}</h3>
              <span class="font-mono text-[10px] uppercase tracking-widest text-meta">{{ w.status }}</span>
            </div>
            <p class="text-muted text-xs font-mono">/{{ w.slug }}</p>
          </Card>
        </NuxtLink>
      </div>
    </div>

    <Dialog v-model="newOpen" size="md">
      <div class="p-6 space-y-4">
        <h2 class="text-xl text-fg">New Project Base</h2>
        <div>
          <label class="block text-xs font-mono uppercase tracking-widest text-meta mb-2">Name</label>
          <Input v-model="newName" placeholder="Client Research" />
        </div>
        <div>
          <label class="block text-xs font-mono uppercase tracking-widest text-meta mb-2">Slug</label>
          <Input v-model="newSlug" placeholder="client-research" />
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <Button variant="ghost" @click="newOpen = false">Cancel</Button>
          <Button variant="accent" :disabled="create.isPending.value" @click="onCreate">Create</Button>
        </div>
      </div>
    </Dialog>
  </div>
</template>
