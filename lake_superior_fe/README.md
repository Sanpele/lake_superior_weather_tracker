# Lake Superior Weather (React + Vite)

Weather visualization over a Lake Superior map — wind, waves, visibility from the backend API.

## Project structure

```
src/
├── api/              # Backend API client
│   └── weatherApi.js
├── components/
│   ├── map/          # Lake Superior map (e.g. Leaflet/Mapbox)
│   │   └── LakeSuperiorMap.jsx
│   ├── weather/      # Weather readouts (wind, waves, visibility)
│   │   └── WeatherPanel.jsx
│   └── ui/           # Shared UI components
├── constants/
│   └── config.js     # API base URL, map defaults
├── hooks/
│   └── useWeather.js
├── pages/
│   └── HomePage.jsx
├── utils/            # Helpers, formatters
├── App.jsx
├── App.css
├── main.jsx
└── index.css
```

Set `VITE_API_URL` in `.env` for the backend base URL (default: `http://localhost:3000`).
