/**
 * motion-v default registration. Sets a global config object that consumers
 * can read for consistent springs/durations across the app.
 */
import type { Transition } from 'motion-v'

export interface MotionPresets {
  spring: Transition
  snap: Transition
  quick: Transition
  base: Transition
}

const presets: MotionPresets = {
  spring: { type: 'spring', stiffness: 80, damping: 16, mass: 0.9 },
  snap: { type: 'spring', stiffness: 240, damping: 28 },
  quick: { duration: 0.15, ease: [0.2, 0, 0, 1] },
  base: { duration: 0.2, ease: [0.2, 0, 0, 1] },
}

export default defineNuxtPlugin(() => ({
  provide: { motion: presets },
}))
