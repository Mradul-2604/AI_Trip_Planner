import DayCard from './DayCard'
import CriticScore from './CriticScore'
import './PlanCard.css'

export default function PlanCard({ plan }) {
  const { itinerary = [], budget, critic_review, weather, preferences } = plan

  const conditionEmoji = (c = '') => {
    const l = c.toLowerCase()
    if (l.includes('rain')) return '🌧️'
    if (l.includes('cloud')) return '⛅'
    if (l.includes('sun') || l.includes('clear')) return '☀️'
    if (l.includes('storm')) return '⛈️'
    return '🌤️'
  }

  const extractNumber = (str) => {
    if (!str) return 0
    if (typeof str === 'number') return str
    const match = String(str).match(/[\d,.]+/)
    return match ? parseFloat(match[0].replace(/,/g, '')) : 0
  }

  const calculatedTotal = itinerary.reduce((total, day) => {
    const hotelCost = extractNumber(day.hotel?.price_per_night)
    const attrCost = (day.attractions || []).reduce((sum, a) => sum + extractNumber(a.place?.entry_fee), 0)
    const mealCost = (day.meals || []).reduce((sum, m) => sum + extractNumber(m.estimated_cost), 0)
    const transportCost = extractNumber(day.transport?.estimated_cost)
    return total + hotelCost + attrCost + mealCost + transportCost
  }, 0)

  const displayTotal = calculatedTotal > 0 ? calculatedTotal : (budget?.total_estimated || 0)
  const userBudget = preferences?.total_budget || 0
  const isWithin = userBudget > 0 ? displayTotal <= userBudget : (budget?.is_within_budget ?? true)

  return (
    <div className="plan-card">
      {/* Header */}
      <div className="plan-header">
        <div className="plan-header-left">
          <h2 className="plan-title gradient-text">
            {preferences?.destination ?? 'Your Trip'} Itinerary
          </h2>
          <div className="plan-meta-chips">
            {preferences?.duration && (
              <span className="meta-chip">📅 {preferences.duration} days</span>
            )}
            {weather?.conditions && (
              <span className="meta-chip">
                {conditionEmoji(weather.conditions)} {weather.conditions}
              </span>
            )}
            {weather?.temperature_range && (
              <span className="meta-chip">🌡️ {weather.temperature_range}</span>
            )}
            {preferences?.travel_style && (
              <span className="meta-chip capitalize">🎒 {preferences.travel_style}</span>
            )}
          </div>
        </div>

        <div className="plan-budget-pill">
          <span className="budget-pill-label">Total Cost</span>
          <span className="budget-pill-value">
            ₹{displayTotal.toLocaleString()}
          </span>
          <span className={`budget-status ${isWithin ? 'within' : 'over'}`}>
            {isWithin ? '✓ Within budget' : '⚠ Over budget'}
          </span>
        </div>
      </div>

      {/* Day cards */}
      <div className="plan-days">
        {itinerary.length === 0 ? (
          <div className="empty-itinerary">
            <span className="empty-icon">🗺️</span>
            <p className="empty-title">Itinerary generation failed</p>
            <p className="empty-sub">
              {critic_review?.warnings?.[0] ?? 'The AI could not build an itinerary for this query. Try rephrasing or reducing the number of days.'}
            </p>
          </div>
        ) : (
          itinerary.map((day, i) => (
            <DayCard key={day.day_number} day={day} index={i} destination={preferences?.destination} />
          ))
        )}
      </div>

      {/* Critic Review */}
      {critic_review && (
        <CriticScore review={critic_review} />
      )}
    </div>
  )
}
