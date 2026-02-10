/**
 * Static image of Lake Superior with overlays for wind/waves/visibility.
 * Place your Lake Superior image in public/lake-superior-map.png (or update the path below).
 */
function LakeSuperiorMap({ dailyReports }) {
  // Log the reports data for debugging overlays
  if (dailyReports) {
    console.log('Map received daily reports:', dailyReports)
  }

  return (
    <div className="lake-superior-map" aria-label="Map of Lake Superior">
      <div style={{ position: 'relative', width: '100%', maxWidth: 800, margin: '0.5rem auto' }}>
        {/* Static image - replace with your actual Lake Superior map image */}
        <img
          src="/lake-superior-map.png"
          alt="Lake Superior"
          style={{
            width: '100%',
            height: 'auto',
            display: 'block',
            borderRadius: 8
          }}
          onError={(e) => {
            // Fallback if image doesn't exist yet
            e.target.style.display = 'none'
            e.target.nextSibling.style.display = 'grid'
          }}
        />
        {/* Placeholder if image not found */}
        <div
          style={{
            height: 400,
            background: '#e2e8f0',
            display: 'none',
            grid: 'place-items: center',
            borderRadius: 8,
            border: '2px dashed #94a3b8'
          }}
        >
          <div style={{ textAlign: 'center', color: '#64748b' }}>
            <p>Place your Lake Superior map image at:</p>
            <code style={{ background: '#f1f5f9', padding: '0.25rem 0.5rem', borderRadius: 4 }}>
              public/lake-superior-map.png
            </code>
          </div>
        </div>
        
        {/* Overlay container for wind/waves/visibility indicators */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none'
          }}
        >
          {/* Overlays will be added here based on dailyReports */}
        </div>
      </div>
    </div>
  )
}

export default LakeSuperiorMap
