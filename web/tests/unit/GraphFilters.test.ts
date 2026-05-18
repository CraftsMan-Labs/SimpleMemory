import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import GraphFilters from '@/components/graph/GraphFilters.vue'

describe('GraphFilters', () => {
  it('switches layer when chip clicked', async () => {
    const wrapper = mount(GraphFilters, {
      props: { layer: 'unified', minConfidence: 0 },
    })
    const buttons = wrapper.findAll('button')
    // 3 layer buttons rendered
    expect(buttons.length).toBeGreaterThanOrEqual(3)
    await buttons[1]!.trigger('click') // semantic
    const evt = wrapper.emitted('update:layer')
    expect(evt?.[0]).toBeDefined()
  })

  it('emits min-confidence when slider changes', async () => {
    const wrapper = mount(GraphFilters, {
      props: { layer: 'unified', minConfidence: 0 },
    })
    const slider = wrapper.find('input[type="range"]')
    await slider.setValue('0.4')
    const evt = wrapper.emitted('update:minConfidence')
    expect(evt?.[0]).toEqual([0.4])
  })
})
