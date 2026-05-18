<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { skin } = useTheme()

useHead({
  htmlAttrs: { 'data-skin': skin, lang: 'en' },
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
