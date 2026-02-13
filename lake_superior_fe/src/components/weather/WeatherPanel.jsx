/**
 * Displays wind, waves, and visibility from weather data.
 */
function WeatherPanel({ data, loading, error }) {
  if (loading) return <div className="weather-panel">Loading weather…</div>
  if (error) return <div className="weather-panel weather-panel--error">{error}</div>
  if (!data || !data.daily_reports) return null

  // Sort reports to ensure eastern is first, western is second
  const sortedReports = [...data.daily_reports].sort((a, b) => {
    if (a.region.toLowerCase().includes('eastern')) return 1
    if (b.region.toLowerCase().includes('eastern')) return -1
    return 0
  })

  return (
    <div className="weather-panel">
      <h3 style={{ margin: '0 0 0.5rem 0' }}>Daily Weather Reports</h3>
      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
        {sortedReports.map((report, idx) => (
          <div
            key={idx}
            style={{
              flex: '0 1 280px',
              padding: '0.4rem',
              border: '1px solid #ccc',
              borderRadius: 4,
              fontSize: '0.85rem'
            }}
          >
            <h4 style={{ margin: '0 0 0.3rem 0', fontSize: '0.95rem' }}>
              {report.region.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </h4>
            <p style={{ margin: '0.15rem 0' }}><strong>Wind Direction:</strong> {report.wind_direction ?? 'N/A'}</p>
            <p style={{ margin: '0.15rem 0' }}><strong>Wind Speed:</strong> {report.wind_speed ?? 'N/A'}</p>
            <p style={{ margin: '0.15rem 0' }}><strong>Wave Height:</strong> {report.wave_height ?? 'N/A'} ft</p>
            <p style={{ margin: '0.15rem 0' }}><strong>Visibility:</strong> {report.visibility ?? 'N/A'}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default WeatherPanel
