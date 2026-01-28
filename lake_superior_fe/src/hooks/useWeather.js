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
        if (!cancelled) setData(d)
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
