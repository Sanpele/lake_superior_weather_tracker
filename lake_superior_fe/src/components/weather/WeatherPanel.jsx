import { describeWind } from '../../utils/windUtils'

/**
 * Displays wind, waves, and visibility from weather data.
 */
function WeatherPanel({ data, loading, error }) {
  if (loading) return <div className="weather-panel">Loading weather…</div>
  if (error) return <div className="weather-panel weather-panel--error">{error}</div>
  if (!data || !data.daily_conditions) return null

  return (
    <div className="weather-panel">
      <h3 style={{ margin: '0 0 0.5rem 0' }}>Daily Weather Reports</h3>
      <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem' }}>
        Updated: {data.updated_at ? new Date(data.updated_at).toLocaleString() : 'N/A'}
      </p>
      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
        {data.daily_conditions.map((conditions) => (
          <div
            key={conditions.region.id}
            style={{
              flex: '0 1 280px',
              padding: '0.4rem',
              border: '1px solid #ccc',
              borderRadius: 4,
              fontSize: '0.85rem'
            }}
          >
            <h4 style={{ margin: '0 0 0.3rem 0', fontSize: '0.95rem' }}>
              {conditions.region.name}
            </h4>
            <p style={{ margin: '0.15rem 0' }}><strong>Wind:</strong> {describeWind(conditions.wind)}</p>
            <p style={{ margin: '0.15rem 0' }}><strong>Wave Height:</strong> {conditions.peak_wave_height_m != null ? `${conditions.peak_wave_height_m} m` : 'N/A'}</p>
            <p style={{ margin: '0.15rem 0' }}><strong>Visibility:</strong> {conditions.visibility ?? 'N/A'}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default WeatherPanel
