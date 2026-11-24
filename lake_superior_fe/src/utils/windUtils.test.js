import { describe, expect, it } from 'vitest'
import {
  describeWind,
  getRegionBounds,
  hasWindArrows,
  windArrowHeading
} from './windUtils'

describe('windArrowHeading', () => {
  it.each([
    ['north', 180],
    ['east', 270],
    ['south', 0],
    ['west', 90],
    ['northwest', 135],
    ['southeast', 315]
  ])('points a %s wind toward %i degrees', (fromDirection, heading) => {
    expect(windArrowHeading(fromDirection)).toBe(heading)
  })
})

describe('describeWind', () => {
  it.each([
    [{ state: 'reported', from_direction: 'northwest', speed_knots: 20 }, 'northwest 20 kt'],
    [{ state: 'light', from_direction: null, speed_knots: null }, 'Light'],
    [{ state: 'variable', from_direction: null, speed_knots: 10 }, 'Variable 10 kt'],
    [{ state: 'unknown', from_direction: null, speed_knots: null }, 'N/A']
  ])('describes %o as %s', (wind, text) => {
    expect(describeWind(wind)).toBe(text)
  })
})

describe('hasWindArrows', () => {
  it.each([
    ['reported', true],
    ['light', false],
    ['variable', false],
    ['unknown', false]
  ])('for %s wind is %s', (state, expected) => {
    expect(hasWindArrows({ wind: { state } })).toBe(expected)
  })
})

describe('getRegionBounds', () => {
  it('finds each region by its exact id', () => {
    expect(getRegionBounds('western_lake_superior')).toEqual({ minX: 0, maxX: 590, minY: 0, maxY: 649 })
    expect(getRegionBounds('eastern_lake_superior')).toEqual({ minX: 590, maxX: 1024, minY: 0, maxY: 649 })
  })

  it('has no bounds for an id it does not know', () => {
    expect(getRegionBounds('Eastern Lake Superior')).toBeUndefined()
  })
})
