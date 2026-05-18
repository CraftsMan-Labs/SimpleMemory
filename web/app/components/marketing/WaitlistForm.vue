<script setup lang="ts">
/**
 * Email + role waitlist capture. Uses valibot directly for schema validation
 * (no vee-validate field binding gymnastics) so the form composes cleanly with
 * our shared Input component.
 */
import { ref } from 'vue'
import * as v from 'valibot'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import { useToast } from '@/composables/useToast'

const schema = v.object({
  email: v.pipe(v.string(), v.email('Enter a valid email.')),
  role: v.pipe(v.string(), v.minLength(2, 'Tell us your role.')),
})

const email = ref('')
const role = ref('')
const submitting = ref(false)
const submitted = ref(false)
const errors = ref<{ email?: string; role?: string }>({})

const { push } = useToast()

const onSubmit = async () => {
  errors.value = {}
  const result = v.safeParse(schema, { email: email.value, role: role.value })
  if (!result.success) {
    for (const issue of result.issues) {
      const path = issue.path?.[0]?.key as 'email' | 'role' | undefined
      if (path) errors.value[path] = issue.message
    }
    return
  }
  submitting.value = true
  try {
    await $fetch('/api/waitlist', { method: 'POST', body: result.output })
    submitted.value = true
    push({ title: "You're on the list.", message: "We'll email you when your base is ready.", tone: 'accent' })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form v-if="!submitted" class="space-y-4" @submit.prevent="onSubmit">
    <div>
      <label class="block text-xs font-mono uppercase tracking-widest text-meta mb-2">Email</label>
      <Input v-model="email" inputmode="email" placeholder="you@company.com" />
      <p v-if="errors.email" class="mt-1 text-xs text-[var(--danger)]">{{ errors.email }}</p>
    </div>
    <div>
      <label class="block text-xs font-mono uppercase tracking-widest text-meta mb-2">Role</label>
      <Input v-model="role" placeholder="What do you do?" />
      <p v-if="errors.role" class="mt-1 text-xs text-[var(--danger)]">{{ errors.role }}</p>
    </div>
    <Button type="submit" variant="accent" size="lg" :disabled="submitting" class="w-full">
      Request access
    </Button>
  </form>
  <div v-else class="surface-card p-6 text-center">
    <p class="text-fg text-lg mb-2">You're on the list.</p>
    <p class="text-muted text-sm">We'll email you when your Project Base is ready.</p>
  </div>
</template>
