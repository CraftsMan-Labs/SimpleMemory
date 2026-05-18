<script setup lang="ts">
/**
 * Mintlify light layout — used for full-page reading surfaces (e.g. embedded
 * docs view). The wiki page mounts WikiReader inline within the app shell;
 * this layout exists for routes that want the whole viewport in light mode.
 */
</script>

<template>
  <div data-skin="mintlify" class="min-h-screen bg-bg text-fg">
    <slot />
  </div>
</template>
