/**
 * Displays wind, waves, and visibility from weather data.
 */
function WeatherPanel({ data, loading, error }) {
  if (loading) return <div className="weather-panel">Loading weather…</div>
  if (error) return <div className="weather-panel weather-panel--error">{error}</div>
  if (!data) return null

  return (
    <div className="weather-panel">
      <h3>Conditions</h3>
      {/* Structure according to your API response */}
      {data.wind != null && <p><strong>Wind:</strong> {JSON.stringify(data.wind)}</p>}
      {data.waves != null && <p><strong>Waves:</strong> {JSON.stringify(data.waves)}</p>}
      {data.visibility != null && <p><strong>Visibility:</strong> {JSON.stringify(data.visibility)}</p>}
    </div>
  )
}

export default WeatherPanel
