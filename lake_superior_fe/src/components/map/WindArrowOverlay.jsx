import WindArrow from './WindArrow'

/**
 * SVG overlay container for wind arrows
 * Maps through dailyReports and renders wind arrows for each region
 */
function WindArrowOverlay({ dailyReports }) {
  // Don't render anything if no data
  if (!dailyReports || dailyReports.length === 0) {
    return null
  }

  return (
    <svg
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none'
      }}
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid meet"
    >
      {dailyReports.map((report, idx) => (
        <WindArrow
          key={`${report.region}-${idx}`}
          region={report.region}
          windDirection={report.wind_direction}
          windSpeed={report.wind_speed}
        />
      ))}
    </svg>
  )
}

export default WindArrowOverlay
