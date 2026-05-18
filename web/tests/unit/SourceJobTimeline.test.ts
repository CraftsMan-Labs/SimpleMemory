import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import SourceJobTimeline from '@/components/sources/SourceJobTimeline.vue'

const job = (stage: string | null, status = 'running') => ({
  id: 'j',
  status,
  stage,
  progress: 0.5,
  error: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
})

describe('SourceJobTimeline', () => {
  it('renders nothing without jobs', () => {
    const wrapper = mount(SourceJobTimeline, { props: { jobs: [] } })
    expect(wrapper.text()).toBe('')
  })

  it('renders all eight stages and marks current', () => {
    const wrapper = mount(SourceJobTimeline, { props: { jobs: [job('wiki_generation')] } })
    const labels = wrapper.findAll('li').map((li) => li.text())
    expect(labels.join(' ')).toContain('Parse')
    expect(labels.join(' ')).toContain('Wiki')
    expect(labels.join(' ')).toContain('Done')
  })

  it('shows error message when present', () => {
    const j = { ...job('parsing', 'failed'), error: 'boom' }
    const wrapper = mount(SourceJobTimeline, { props: { jobs: [j] } })
    expect(wrapper.text()).toContain('boom')
  })
})
