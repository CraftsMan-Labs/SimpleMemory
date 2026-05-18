import { defineStore } from 'pinia'
import type { Workspace } from '@@/types/api'

export const useProjectBaseStore = defineStore('projectBase', {
  state: () => ({
    tenantId: '' as string,
    workspaces: [] as Workspace[],
    currentSlug: '' as string,
  }),
  getters: {
    current(state): Workspace | null {
      return state.workspaces.find((w) => w.slug === state.currentSlug) ?? null
    },
    currentWorkspaceId(): string {
      return this.current?.id ?? ''
    },
  },
  actions: {
    setWorkspaces(list: Workspace[]) {
      this.workspaces = list
      if (list.length && list[0]) this.tenantId = list[0].tenant_id
    },
    selectBySlug(slug: string) {
      this.currentSlug = slug
    },
  },
})
