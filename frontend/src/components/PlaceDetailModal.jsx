import { useEffect } from 'react'
import './PlaceDetailModal.css'

export default function PlaceDetailModal({ attraction, destination, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'unset'
    }
  }, [onClose])

  if (!attraction) return null

  const { place = {}, timing } = attraction
  const {
    name = 'Attraction Details',
    description = 'No detailed description available.',
    category = 'Attraction',
    entry_fee = 'Free',
    recommended_duration_hours = 1,
    best_time_to_visit = 'Anytime'
  } = place

  const categoryIcon = (cat = '') => {
    const l = cat.toLowerCase()
    if (l.includes('beach')) return '🏖️'
    if (l.includes('fort') || l.includes('heritage')) return '🏰'
    if (l.includes('waterfall') || l.includes('nature') || l.includes('park')) return '🌊'
    if (l.includes('market') || l.includes('shop')) return '🛍️'
    if (l.includes('temple') || l.includes('church') || l.includes('mosque')) return '⛪'
    if (l.includes('food') || l.includes('rest')) return '🍽️'
    if (l.includes('museum') || l.includes('art')) return '🏛️'
    return '📍'
  }

  const queryLocation = destination ? `${name}, ${destination}` : name
  const mapEmbedUrl = `https://maps.google.com/maps?q=${encodeURIComponent(queryLocation)}&t=&z=15&ie=UTF8&iwloc=&output=embed`
  const mapSearchUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(queryLocation)}`

  return (
    <div className="place-modal-backdrop" onClick={onClose}>
      <div 
        className="place-modal-card glass" 
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="place-modal-title"
      >
        {/* Modal Header */}
        <div className="place-modal-header">
          <div className="place-modal-badges">
            <span className="place-cat-badge">
              <span className="badge-icon">{categoryIcon(category)}</span>
              {category}
            </span>
            {timing && <span className="place-time-badge">🕒 {timing}</span>}
          </div>
          <button 
            className="place-modal-close-btn" 
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div className="place-modal-body">
          <div className="place-title-section">
            <h2 id="place-modal-title" className="place-modal-title gradient-text">{name}</h2>
            <p className="place-modal-desc">{description}</p>
          </div>

          {/* Key details grid */}
          <div className="place-details-grid">
            <div className="detail-pill">
              <span className="detail-icon">⏱️</span>
              <div className="detail-meta">
                <span className="detail-label">Duration</span>
                <span className="detail-value">{recommended_duration_hours} {recommended_duration_hours === 1 ? 'hour' : 'hours'}</span>
              </div>
            </div>

            <div className="detail-pill">
              <span className="detail-icon">🎟️</span>
              <div className="detail-meta">
                <span className="detail-label">Entry Fee</span>
                <span className="detail-value">{entry_fee}</span>
              </div>
            </div>

            <div className="detail-pill">
              <span className="detail-icon">🌅</span>
              <div className="detail-meta">
                <span className="detail-label">Best Time</span>
                <span className="detail-value">{best_time_to_visit}</span>
              </div>
            </div>
          </div>

          {/* Map Section */}
          <div className="place-map-container">
            <div className="place-map-header">
              <span className="place-map-title">📍 Location Preview</span>
              <a 
                href={mapSearchUrl} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="place-map-link"
              >
                Open in Google Maps ↗
              </a>
            </div>
            <div className="place-map-frame-wrapper">
              <iframe
                title={`Map of ${name}`}
                src={mapEmbedUrl}
                loading="lazy"
                allowFullScreen
                className="place-map-iframe"
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="place-modal-footer">
          <button className="place-btn-secondary" onClick={onClose}>
            Close
          </button>
          <a 
            href={mapSearchUrl} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="place-btn-primary"
          >
            🧭 Navigate in Google Maps
          </a>
        </div>
      </div>
    </div>
  )
}
