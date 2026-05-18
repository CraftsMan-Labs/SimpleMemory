<script setup lang="ts">
import MarketingHero from '@/components/marketing/MarketingHero.vue'
import FeatureGrid from '@/components/marketing/FeatureGrid.vue'
definePageMeta({ layout: 'marketing' })
useSeoMeta({
  title: 'KMG — Drop a source. Get a living vault.',
  description: 'AI-generated Obsidian vaults for every project base.',
})
</script>

<template>
  <MarketingHero />
  <FeatureGrid />
</template>
