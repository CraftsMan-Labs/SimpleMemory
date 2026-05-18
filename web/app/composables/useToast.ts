/** Global toast queue. */
import { ref } from 'vue'

export type Toast = {
  id: string
  title?: string
  message?: string
  tone?: 'default' | 'accent' | 'warn' | 'danger'
  timeoutMs?: number
}

const toasts = ref<Toast[]>([])

export function useToast() {
  const push = (t: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).slice(2)
    const next: Toast = { id, tone: 'default', timeoutMs: 4000, ...t }
    toasts.value.push(next)
    if (next.timeoutMs) setTimeout(() => dismiss(id), next.timeoutMs)
    return id
  }
  const dismiss = (id: string) => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }
  return { toasts, push, dismiss }
}
