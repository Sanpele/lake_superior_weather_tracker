/**
 * Wind utility functions for converting wind data to visual representations
 * Coordinates use the SVG's native viewBox (0-1024 x, 0-649 y)
 */

// Map full-word compass directions to degrees (0° = North, clockwise)
const DIRECTION_TO_DEGREES = {
  'north': 0,
  'northeast': 45,
  'east': 90,
  'southeast': 135,
  'south': 180,
  'southwest': 225,
  'west': 270,
  'northwest': 315
}

// Region bounds for arrow grids (native SVG coordinates)
// Lake split at x=590 to balance visible lake area (lake extends further east)
const REGION_BOUNDS = {
  eastern_lake_superior: { minX: 590, maxX: 1024, minY: 0, maxY: 649 },
  western_lake_superior: { minX: 0, maxX: 590, minY: 0, maxY: 649 }
}

/**
 * Convert wind direction string to degrees
 * @param {string} direction - Wind direction as full word (e.g., "north", "northeast")
 * @returns {number} Degrees (0-360), 0 = North
 */
export function directionToDegrees(direction) {
  if (!direction) return 0
  const normalized = direction.toLowerCase().trim()
  return DIRECTION_TO_DEGREES[normalized] ?? 0
}

/**
 * A marine wind is named for where it blows from, so its arrow points the opposite way
 * @param {string} fromDirection - Direction the wind blows from (e.g., "northwest")
 * @returns {number} Heading the arrow points toward (0-360), 0 = North
 */
export function windArrowHeading(fromDirection) {
  return (directionToDegrees(fromDirection) + 180) % 360
}

/**
 * Only a reported wind has a direction an arrow can honestly show
 * @param {{wind: {state: string}}} conditions - Daily conditions for a region
 * @returns {boolean} Whether to draw wind arrows
 */
export function hasWindArrows(conditions) {
  return conditions.wind.state === 'reported'
}

/**
 * Describe a region's opening wind for display
 * @param {{state: string, from_direction: ?string, speed_knots: ?number}} wind
 * @returns {string} Display text
 */
export function describeWind(wind) {
  switch (wind.state) {
    case 'reported':
      return `${wind.from_direction} ${wind.speed_knots} kt`
    case 'light':
      return 'Light'
    case 'variable':
      return `Variable ${wind.speed_knots} kt`
    default:
      return 'N/A'
  }
}

/**
 * Calculate individual arrow size based on wind speed
 * Stronger winds = larger arrows
 * @param {number|string} windSpeed - Wind speed in knots
 * @returns {number} Arrow size in SVG viewBox units
 */
export function getArrowSize(windSpeed) {
  const speed = parseFloat(windSpeed) || 0
  if (speed >= 30) return 126  // Large for gale force
  if (speed >= 20) return 90   // Medium for strong winds
  if (speed >= 10) return 72   // Small for moderate winds
  return 54                     // Smaller for light winds
}

/**
 * Get arrow color based on wind intensity
 * @param {number|string} windSpeed - Wind speed in knots
 * @returns {string} Hex color code
 */
export function getArrowColor(windSpeed) {
  const speed = parseFloat(windSpeed) || 0
  if (speed >= 30) return '#ef4444'  // Red - gale force
  if (speed >= 20) return '#f97316'  // Orange - strong winds
  if (speed >= 10) return '#fbbf24'  // Yellow - moderate winds
  return '#4ade80'                    // Green - light winds
}

/**
 * Get bounds for a region (area to fill with arrows)
 * @param {string} regionId - Region id from the daily conditions
 * @returns {{minX: number, maxX: number, minY: number, maxY: number}|undefined} Bounds in native SVG coordinates
 */
export function getRegionBounds(regionId) {
  return REGION_BOUNDS[regionId]
}

/**
 * Calculate grid spacing for arrows
 * @param {number|string} windSpeed - Wind speed in knots
 * @returns {number} Grid spacing in SVG viewBox units
 */
export function getGridSpacing(windSpeed) {
  const speed = parseFloat(windSpeed) || 0
  if (speed >= 30) return 90   // Gale force - dense grid
  if (speed >= 20) return 100  // Strong winds
  if (speed >= 10) return 110  // Moderate winds
  return 100                    // Light winds
}
