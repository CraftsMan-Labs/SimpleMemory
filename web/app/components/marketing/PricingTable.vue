<script setup lang="ts">
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import { Check } from 'lucide-vue-next'

const tiers = [
  {
    name: 'Hobby', price: '$0',
    desc: 'One Project Base, unlimited sources up to 100MB.',
    features: ['1 Project Base', '100MB storage', 'Local graph only', 'Community support'],
    cta: 'Start free',
  },
  {
    name: 'Pro', price: '$24/mo', highlight: true,
    desc: 'Unlimited bases, full graph, canvas AI organise.',
    features: ['Unlimited Project Bases', '10GB storage', 'Full graph + canvas', 'Priority ingest', 'Email support'],
    cta: 'Start Pro',
  },
  {
    name: 'Team', price: '$80/seat/mo',
    desc: 'Shared bases, permissions, audit trail.',
    features: ['Everything in Pro', 'Shared bases', 'Roles + audit', 'SSO + SCIM', 'Dedicated SLA'],
    cta: 'Talk to sales',
  },
]
</script>

<template>
  <section class="max-w-[var(--container-max)] mx-auto px-6 py-24">
    <h2 class="text-3xl text-fg mb-12 text-display text-center">Pricing.</h2>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <Card
        v-for="t in tiers"
        :key="t.name"
        padded
        :class="t.highlight ? 'border-accent shadow-[0_0_0_1px_var(--accent)]' : ''"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl text-fg">{{ t.name }}</h3>
          <span v-if="t.highlight" class="text-[10px] font-mono uppercase tracking-widest text-accent">Most popular</span>
        </div>
        <div class="text-3xl text-display text-fg mb-2">{{ t.price }}</div>
        <p class="text-sm text-muted mb-6">{{ t.desc }}</p>
        <ul class="space-y-2 text-sm text-fg-2 mb-8">
          <li v-for="f in t.features" :key="f" class="flex items-start gap-2">
            <Check :size="14" class="text-accent mt-0.5 shrink-0" />
            <span>{{ f }}</span>
          </li>
        </ul>
        <Button :variant="t.highlight ? 'accent' : 'outline'" size="md" class="w-full">{{ t.cta }}</Button>
      </Card>
    </div>
  </section>
</template>
