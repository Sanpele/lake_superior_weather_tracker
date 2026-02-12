import {
  directionToDegrees,
  getArrowSize,
  getArrowColor,
  getRegionBounds,
  getGridSpacing,
  isPointInPolygon,
  getLakePolygon
} from '../../utils/windUtils'

/**
 * Renders a grid of wind arrows filling a specific region
 * Arrows only appear within the Lake Superior outline shape
 */
function WindArrow({ region, windDirection, windSpeed }) {
  // Calculate arrow properties
  const degrees = directionToDegrees(windDirection)
  const arrowSize = getArrowSize(windSpeed)
  const color = getArrowColor(windSpeed)
  const bounds = getRegionBounds(region)
  const gridSpacing = getGridSpacing(windSpeed)
  const lakePolygon = getLakePolygon(region)

  // Convert degrees to radians for calculations
  const radians = (degrees * Math.PI) / 180

  // Generate grid of arrow positions
  const arrows = []
  let arrowKey = 0

  for (let y = bounds.minY; y <= bounds.maxY; y += gridSpacing) {
    for (let x = bounds.minX; x <= bounds.maxX; x += gridSpacing) {
      // Only add arrow if position is inside the lake polygon
      if (!isPointInPolygon(x, y, lakePolygon)) {
        continue
      }

      // Start position for this arrow
      const startX = x
      const startY = y

      // End position (arrow points in wind direction)
      const endX = startX + arrowSize * Math.sin(radians)
      const endY = startY - arrowSize * Math.cos(radians)

      // Arrowhead geometry
      const arrowheadSize = arrowSize * 0.3
      const arrowheadAngle = 30 * (Math.PI / 180)

      const leftX = endX - arrowheadSize * Math.sin(radians - arrowheadAngle)
      const leftY = endY + arrowheadSize * Math.cos(radians - arrowheadAngle)

      const rightX = endX - arrowheadSize * Math.sin(radians + arrowheadAngle)
      const rightY = endY + arrowheadSize * Math.cos(radians + arrowheadAngle)

      arrows.push({
        key: arrowKey++,
        line: { x1: startX, y1: startY, x2: endX, y2: endY },
        arrowhead: `${endX},${endY} ${leftX},${leftY} ${rightX},${rightY}`
      })
    }
  }

  return (
    <g>
      {/* Render all arrow instances */}
      {arrows.map((arrow) => (
        <g key={arrow.key}>
          {/* Arrow shaft */}
          <line
            x1={arrow.line.x1}
            y1={arrow.line.y1}
            x2={arrow.line.x2}
            y2={arrow.line.y2}
            stroke={color}
            strokeWidth="0.4"
            strokeLinecap="round"
          />

          {/* Arrowhead */}
          <polygon
            points={arrow.arrowhead}
            fill={color}
          />
        </g>
      ))}

      {/* Wind speed label at center of region */}
      <text
        x={(bounds.minX + bounds.maxX) / 2}
        y={(bounds.minY + bounds.maxY) / 2}
        fontSize="3"
        fill={color}
        textAnchor="middle"
        fontWeight="bold"
        style={{ textShadow: '0 0 3px rgba(0,0,0,0.8)' }}
      >
        {windSpeed} kt
      </text>
    </g>
  )
}

export default WindArrow
