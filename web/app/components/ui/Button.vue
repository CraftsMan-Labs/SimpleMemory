<script setup lang="ts">
import { computed } from 'vue'
import { cva } from 'class-variance-authority'
import { cn } from '@/lib/utils'

export type ButtonVariant = 'primary' | 'accent' | 'ghost' | 'outline' | 'link' | 'danger'
export type ButtonSize = 'sm' | 'md' | 'lg' | 'icon'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-fg text-bg hover:opacity-90 [data-skin=mintlify]_&:bg-fg',
        accent: 'bg-accent text-accent-on hover:bg-accent-hover',
        ghost: 'bg-transparent text-fg hover:bg-surface',
        outline: 'border border-border bg-transparent text-fg hover:bg-surface',
        link: 'text-fg underline-offset-4 hover:underline hover:text-accent',
        danger: 'bg-danger text-white hover:opacity-90',
      },
      size: {
        sm: 'h-8 px-3 text-sm rounded-pill',
        md: 'h-10 px-5 text-base rounded-pill',
        lg: 'h-12 px-6 text-base rounded-pill',
        icon: 'h-9 w-9 rounded-pill',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  },
)

type Props = { variant?: ButtonVariant; size?: ButtonSize; class?: string; as?: string }
const props = withDefaults(defineProps<Props>(), { as: 'button' })
const classes = computed(() => cn(buttonVariants({ variant: props.variant, size: props.size }), props.class))
</script>

<template>
  <component :is="as" :class="classes">
    <slot />
  </component>
</template>
