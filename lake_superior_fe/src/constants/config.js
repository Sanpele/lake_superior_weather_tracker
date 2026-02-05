/**
 * App configuration (API base URL, map defaults, etc.)
 * Use import.meta.env for Vite env vars in production.
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const MAP_DEFAULTS = {
  center: [47.0, -87.5],
  zoom: 6,
}
