<script setup lang="ts">
/**
 * Dev/staging login. Accepts a Tenant UUID (matches the FastAPI dev bypass via
 * `X-Tenant-Id`). Production would replace this with the real JWT flow — the
 * tenant id ends up in localStorage either way for the proxy to inject.
 */
import { ref } from 'vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { useTenant } from '@/composables/useTenant'
import { useToast } from '@/composables/useToast'

definePageMeta({ layout: 'marketing' })

const { login } = useTenant()
const { push } = useToast()
const router = useRouter()
const route = useRoute()

const tenantId = ref('')
const submitting = ref(false)

const UUID_RX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

const onSubmit = async () => {
  if (!UUID_RX.test(tenantId.value.trim())) {
    push({ title: 'Invalid tenant id', message: 'Expected a UUID.', tone: 'danger' })
    return
  }
  submitting.value = true
  login(tenantId.value.trim())
  push({ title: 'Signed in', tone: 'accent' })
  const next = (route.query.next as string) || '/app'
  await router.push(next)
  submitting.value = false
}
</script>

<template>
  <section class="max-w-md mx-auto px-6 py-24">
    <h1 class="text-3xl text-fg text-display mb-3">Sign in.</h1>
    <p class="text-muted text-sm mb-8">
      Paste your tenant id to enter your Project Bases. Production replaces this with SSO.
    </p>
    <Card padded>
      <form class="space-y-4" @submit.prevent="onSubmit">
        <div>
          <label class="block text-xs font-mono uppercase tracking-widest text-meta mb-2">Tenant ID</label>
          <Input v-model="tenantId" placeholder="00000000-0000-0000-0000-000000000000" />
        </div>
        <Button type="submit" variant="accent" size="lg" :disabled="submitting" class="w-full">
          Enter
        </Button>
      </form>
    </Card>
  </section>
</template>
