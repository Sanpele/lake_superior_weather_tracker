import { API_BASE_URL } from '../constants/config'

/**
 * Fetch daily weather (wind, waves, visibility) from the backend.
 * @returns {Promise<{ wind?: object, waves?: object, visibility?: object }>}
 */
export async function getWeather() {
  const res = await fetch(`${API_BASE_URL}/weather`)
  if (!res.ok) throw new Error('Failed to fetch weather')
  return res.json()
}
