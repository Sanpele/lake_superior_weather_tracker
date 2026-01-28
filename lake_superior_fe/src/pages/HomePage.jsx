import { useWeather } from '../hooks/useWeather'
import LakeSuperiorMap from '../components/map/LakeSuperiorMap'
import WeatherPanel from '../components/weather/WeatherPanel'

function HomePage() {
  const { data, loading, error } = useWeather()

  return (
    <main className="home-page">
      <h1>Lake Superior Weather</h1>
      <LakeSuperiorMap />
      <WeatherPanel data={data} loading={loading} error={error} />
    </main>
  )
}

export default HomePage
