/**
 * Spring + tween presets pulled from CSS motion tokens.
 * Components import these into motion-v transitions so timings stay consistent.
 */
export function useMotionPresets() {
  return {
    spring: { type: 'spring', stiffness: 80, damping: 16, mass: 0.9 } as const,
    snap: { type: 'spring', stiffness: 240, damping: 28 } as const,
    quick: { duration: 0.15, ease: [0.2, 0, 0, 1] } as const,
    base: { duration: 0.2, ease: [0.2, 0, 0, 1] } as const,
  }
}
