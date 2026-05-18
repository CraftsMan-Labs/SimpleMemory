<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
</script>

<template>
  <section class="relative overflow-hidden">
    <!-- electric glow -->
    <div
      aria-hidden="true"
      class="pointer-events-none absolute inset-x-0 top-0 h-[60vh]"
      :style="{
        background: 'radial-gradient(60% 50% at 50% 0%, color-mix(in oklab, var(--accent), transparent 80%), transparent 70%)',
      }"
    />
    <div class="relative max-w-[var(--container-max)] mx-auto px-6 pt-32 pb-24 text-center">
      <p class="font-mono text-xs uppercase tracking-[0.25em] text-accent mb-6">obsidian, but generated</p>
      <h1
        class="text-display text-fg mb-6"
        style="font-size: clamp(3rem, 7vw, var(--text-4xl)); line-height: 0.92;"
      >
        Drop a source.<br />
        Get a living vault.
      </h1>
      <p class="max-w-2xl mx-auto text-lg text-fg-2 leading-relaxed">
        KMG turns every PDF, page, and conversation into an AI-generated Obsidian vault —
        wiki pages, backlinks, and a semantic graph you can navigate, search, and reorganise on an infinite canvas.
      </p>
      <div class="mt-10 flex flex-wrap items-center justify-center gap-3">
        <Button variant="primary" size="lg" as="a" href="/waitlist">Join the waitlist →</Button>
        <Button variant="outline" size="lg" as="a" href="/app">Open app</Button>
      </div>
    </div>
  </section>
</template>
