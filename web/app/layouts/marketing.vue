<script setup lang="ts">
/** Public marketing shell — Framer dark, full-bleed, dramatic. */
</script>

<template>
  <div data-skin="framer" class="min-h-screen bg-bg text-fg">
    <header class="sticky top-0 z-30 backdrop-blur bg-bg/70 border-b border-border-soft">
      <div class="max-w-[var(--container-max)] mx-auto px-6 h-14 flex items-center justify-between">
        <NuxtLink to="/" class="font-mono text-xs tracking-widest uppercase text-fg">
          KMG · Knowledge Memory Graph
        </NuxtLink>
        <nav class="hidden sm:flex items-center gap-6 text-sm text-muted">
          <NuxtLink to="/pricing" class="hover:text-fg transition-colors">Pricing</NuxtLink>
          <NuxtLink to="/waitlist" class="hover:text-fg transition-colors">Waitlist</NuxtLink>
          <NuxtLink to="/app" class="text-fg">Open app →</NuxtLink>
        </nav>
      </div>
    </header>
    <slot />
    <footer class="border-t border-border-soft py-12 mt-24">
      <div class="max-w-[var(--container-max)] mx-auto px-6 flex items-center justify-between text-xs text-meta">
        <span>© KMG, Inc.</span>
        <span class="font-mono uppercase tracking-widest">v3 · obsidian-grade</span>
      </div>
    </footer>
  </div>
</template>
