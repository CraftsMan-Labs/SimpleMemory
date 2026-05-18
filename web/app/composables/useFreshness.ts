/**
 * Freshness helpers — derive UI variant + label from a WikiPage.freshness_status.
 */
import type { FreshnessStatus } from '@@/types/api'

export interface FreshnessView {
  variant: 'success' | 'warn' | 'danger' | 'default'
  label: string
  needsTending: boolean
}

export function useFreshness() {
  const view = (status: FreshnessStatus | null | undefined): FreshnessView => {
    switch (status) {
      case 'fresh':
        return { variant: 'success', label: 'fresh', needsTending: false }
      case 'stale':
        return { variant: 'warn', label: 'stale', needsTending: true }
      case 'outdated':
        return { variant: 'danger', label: 'outdated', needsTending: true }
      default:
        return { variant: 'default', label: status ?? 'unknown', needsTending: false }
    }
  }
  return { view }
}
