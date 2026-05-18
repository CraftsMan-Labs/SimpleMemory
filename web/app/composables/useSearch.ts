/**
 * Search + chat. Search uses POST /search (vector-backed). Chat returns a single answer
 * with citations; streaming is supported by the proxy (passes raw body through).
 */
import { ref } from 'vue'
import { useMutation } from '@tanstack/vue-query'
import { apiClient } from '@/lib/api'
import type {
  ChatRequest,
  ChatResponse,
  SearchRequest,
  SearchResponse,
} from '@@/types/api'

export function useSearch() {
  return useMutation({
    mutationFn: (body: SearchRequest) =>
      apiClient<SearchResponse>('/search', { method: 'POST', body }),
  })
}

export function useChat() {
  const messages = ref<Array<{ role: 'user' | 'assistant'; text: string; citations?: unknown[] }>>([])
  const conversationId = ref<string | null>(null)
  const pending = ref(false)

  const ask = async (query: string, scope: ChatRequest['scope'] = 'current_project') => {
    pending.value = true
    messages.value.push({ role: 'user', text: query })
    try {
      const res = await apiClient<ChatResponse>('/chat', {
        method: 'POST',
        body: { query, scope, conversation_id: conversationId.value } satisfies ChatRequest,
      })
      conversationId.value = res.conversation_id
      messages.value.push({ role: 'assistant', text: res.answer, citations: res.citations })
      return res
    } finally {
      pending.value = false
    }
  }

  const reset = () => {
    messages.value = []
    conversationId.value = null
  }

  return { messages, conversationId, pending, ask, reset }
}
