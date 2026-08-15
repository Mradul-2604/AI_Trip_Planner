"""
Context summarizer utility.
Reduces inter-agent data to the minimum tokens ItineraryAgent actually needs.
"""
from typing import Dict, Any, Optional


def summarize_for_itinerary(
    research: Optional[Dict[str, Any]],
    weather,        # WeatherInfo pydantic model or None
    budget,         # BudgetBreakdown pydantic model or None
    user_budget: Optional[float] = None,       # Original user-stated budget
    user_currency: Optional[str] = None,
) -> str:
    """
    Returns a compact, token-efficient summary string for the ItineraryAgent prompt.
    
    Instead of dumping full JSON objects, we extract only:
    - Top 5 place names + entry fees
    - Top 3 restaurant names + cuisine
    - Weather: one-line summary + conditions
    - Budget: total and currency only
    """
    lines = []

    # ── Places, Hotels, Foods & Restaurants ──────────────────────────────────
    if research:
        hotels = research.get("hotels", [])[:5]
        if hotels:
            lines.append("TOP VERIFIED HOTELS IN DESTINATION (USE ONLY THESE):")
            for h in hotels:
                name = h.get("name", "Unknown")
                stars = h.get("stars", "3")
                price = h.get("price_per_night", "₹2500")
                addr = h.get("address", "City Center")
                lines.append(f"  - {name} ({stars}★, ~{price}/night, address: {addr})")

        places = research.get("places", [])[:8]
        if places:
            lines.append("TOP PLACES (MUST USE ONLY THESE IN ITINERARY):")
            for p in places:
                name = p.get("name", "Unknown")
                fee = p.get("entry_fee", "Free")
                category = p.get("category", "attraction")
                duration = p.get("recommended_duration_hours", "")
                desc = p.get("description", "")
                duration_str = f", {duration}h" if duration else ""
                lines.append(f"  - {name} [Category: {category}] (entry: {fee}{duration_str}) - {desc}")

        famous_foods = research.get("famous_local_dishes", [])
        if famous_foods:
            lines.append("FAMOUS LOCAL CUISINE & MUST-TRY DISHES (FEATURE THESE IN MEALS):")
            for f in famous_foods:
                lines.append(f"  - {f}")

        restaurants = research.get("restaurants", [])[:6]
        if restaurants:
            lines.append("TOP RESTAURANTS (MUST USE ONLY THESE WITH ADDRESSES IN ITINERARY):")
            for r in restaurants:
                name = r.get("name", "Unknown")
                cuisine = r.get("cuisine", "")
                cost = r.get("average_cost", "")
                address = r.get("address", "Local area")
                lines.append(f"  - {name} (cuisine: {cuisine}, avg cost: {cost}, address: {address})")

    # ── Weather (one line) ────────────────────────────────────────────────────
    if weather:
        summary = getattr(weather, "summary", "")
        conditions = getattr(weather, "conditions", "")
        temp = getattr(weather, "temperature_range", "")
        warnings = getattr(weather, "travel_warnings", [])
        weather_line = f"WEATHER: {temp}, {conditions}."
        if summary:
            weather_line += f" {summary}"
        lines.append(weather_line)
        if warnings:
            lines.append(f"WEATHER WARNINGS: {'; '.join(warnings[:2])}")

    # ── Budget (totals only) ──────────────────────────────────────────────────
    if budget:
        total = getattr(budget, "total_estimated", 0)
        currency = getattr(budget, "currency", "")
        within = getattr(budget, "is_within_budget", True)
        lines.append(f"BUDGET LIMIT: {total} {currency} ({'within budget' if within else 'OVER BUDGET'}).")
        if user_budget and user_currency:
            lines.append(f"USER'S ORIGINAL BUDGET: {user_budget} {user_currency} — The itinerary MUST use this full budget, not less.")
        if not within:
            suggestions = getattr(budget, "adjustment_suggestions", [])[:2]
            if suggestions:
                lines.append(f"COST CUTS: {'; '.join(suggestions)}")

    return "\n".join(lines) if lines else "No context available."
