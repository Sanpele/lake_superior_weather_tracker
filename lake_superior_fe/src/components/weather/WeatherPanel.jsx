/**
 * Displays wind, waves, and visibility from weather data.
 */
function WeatherPanel({ data, loading, error }) {
  if (loading) return <div className="weather-panel">Loading weather…</div>
  if (error) return <div className="weather-panel weather-panel--error">{error}</div>
  if (!data || !data.daily_reports) return null

  return (
    <div className="weather-panel">
      <h3>Daily Weather Reports</h3>
      {data.daily_reports.map((report, idx) => (
        <div key={idx} style={{ marginBottom: '1rem', padding: '0.75rem', border: '1px solid #ccc', borderRadius: 4 }}>
          <h4>{report.region.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
          <p><strong>Wind Direction:</strong> {report.wind_direction ?? 'N/A'}</p>
          <p><strong>Wind Speed:</strong> {report.wind_speed ?? 'N/A'}</p>
          <p><strong>Wave Height:</strong> {report.wave_height ?? 'N/A'} ft</p>
          <p><strong>Visibility:</strong> {report.visibility ?? 'N/A'}</p>
        </div>
      ))}
    </div>
  )
}

export default WeatherPanel
