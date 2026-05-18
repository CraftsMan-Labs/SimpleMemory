<script setup lang="ts">
import WaitlistForm from '@/components/marketing/WaitlistForm.vue'
definePageMeta({ layout: 'marketing' })
</script>

<template>
  <section class="max-w-md mx-auto px-6 py-24">
    <h1 class="text-3xl text-fg text-display mb-4">Join the waitlist.</h1>
    <p class="text-muted mb-8">
      KMG is opening Project Bases in small batches so the graph quality stays high.
      Tell us a little — we'll let you in.
    </p>
    <WaitlistForm />
  </section>
</template>
