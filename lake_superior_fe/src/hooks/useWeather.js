import { useState, useEffect } from 'react'
import { getWeather } from '../api/weatherApi'

/**
 * Hook to load and expose weather data (wind, waves, visibility).
 */
export function useWeather() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getWeather()
      .then((d) => {
        if (!cancelled) {
          console.log('API Response:', d)
          console.log('Daily Reports:', d?.daily_reports)
          if (d?.daily_reports) {
            d.daily_reports.forEach((report, idx) => {
              console.log(`Report ${idx + 1} (${report.region}):`, {
                wind_direction: report.wind_direction,
                wind_speed: report.wind_speed,
                wave_height: report.wave_height,
                visibility: report.visibility
              })
            })
          }
          setData(d)
        }
      })
      .catch((e) => {
        if (!cancelled) setError(e?.message ?? 'Failed to load weather')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [])

  return { data, loading, error }
}
