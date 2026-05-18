import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import WikiCitationChip from '@/components/wiki/WikiCitationChip.vue'

describe('WikiCitationChip', () => {
  it('renders the index in square brackets', () => {
    const wrapper = mount(WikiCitationChip, { props: { index: 3 } })
    expect(wrapper.text()).toBe('[3]')
  })

  it('emits open with evidenceId when clicked', async () => {
    const wrapper = mount(WikiCitationChip, { props: { index: 1, evidenceId: 'ev-1' } })
    await wrapper.trigger('click')
    expect(wrapper.emitted('open')?.[0]).toEqual(['ev-1'])
  })
})
