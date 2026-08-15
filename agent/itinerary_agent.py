"""
Itinerary Agent to synthesize all gathered data into a structured DayPlan.
Uses summarize_for_itinerary() to pass only a compact context to the LLM,
reducing token usage significantly vs. passing full JSON blobs.
"""
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from utils.llm_loader import invoke_with_fallback
from utils.context_summarizer import summarize_for_itinerary
from prompt_library.itinerary_prompt import SYSTEM_PROMPT
from models.schemas import DayPlan, BudgetBreakdown, CategoryCost
from logger.logging import get_logger

logger = get_logger(__name__)

class ItineraryOutput(BaseModel):
    """Structured output containing a list of daily plans."""
    itinerary: List[DayPlan] = Field(description="The final day-by-day itinerary.")

def _extract_number(val: Any) -> float:
    """Helper to safely extract float from numbers or strings with currency symbols."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    import re
    cleaned = "".join(ch for ch in str(val) if ch.isdigit() or ch == ".")
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0

def itinerary_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes preferences, weather, budget, and research data into a chronological
    DayPlan itinerary. Applies critic revisions if they exist.
    Uses summarize_for_itinerary() to keep the prompt compact.
    Reconciles the budget breakdown with the actual generated day items.
    """
    logger.info("ItineraryAgent started.")

    preferences = state.get("preferences")
    if not preferences:
        logger.warning("No preferences found. Returning empty itinerary.")
        return {"itinerary": [], "completed_agents": ["ItineraryAgent"]}

    weather = state.get("weather_info")
    budget = state.get("budget_breakdown")
    research_data = state.get("research_data", {})
    critic_review = state.get("critic_review")

    # ── Compact context ───────────────────────────────────────────────────────
    context_summary = summarize_for_itinerary(
        research_data,
        weather,
        budget,
        user_budget=preferences.total_budget,
        user_currency=preferences.budget_currency,
    )

    # ── Core prompt ───────────────────────────────────────────────────────────
    content = (
        f"Destination: {preferences.destination}\n"
        f"Duration: {preferences.duration} days\n"
        f"Travel Style: {preferences.travel_style}\n"
        f"Group Size: {preferences.group_size}\n"
        f"Interests: {', '.join(preferences.interests) if preferences.interests else 'General'}\n\n"
        f"{context_summary}\n"
    )

    if critic_review and critic_review.requires_revision:
        content += "\nCRITIC REVISIONS REQUIRED:\n"
        content += "\n".join(f"- {instr}" for instr in critic_review.revision_instructions)

    def build_chain(llm):
        return llm.with_structured_output(ItineraryOutput)

    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=content),
        ]
        final_response = invoke_with_fallback(build_chain, messages)
        logger.info(f"Itinerary created with {len(final_response.itinerary)} days.")

        # Reconcile actual category sums from the generated daily plans
        total_hotel = 0.0
        total_meals = 0.0
        total_attractions = 0.0
        total_transport = 0.0

        for day in final_response.itinerary:
            hotel_cost = _extract_number(day.hotel.price_per_night if day.hotel else 0)
            meals_cost = sum(_extract_number(m.estimated_cost) for m in (day.meals or []))
            attr_cost = sum(_extract_number(a.place.entry_fee if a.place else 0) for a in (day.attractions or []))
            trans_cost = _extract_number(day.transport.estimated_cost if day.transport else 0)

            day_total = hotel_cost + meals_cost + attr_cost + trans_cost
            day.estimated_day_cost = round(day_total, 2)

            total_hotel += hotel_cost
            total_meals += meals_cost
            total_attractions += attr_cost
            total_transport += trans_cost

        actual_grand_total = round(total_hotel + total_meals + total_attractions + total_transport, 2)
        user_total_budget = preferences.total_budget if preferences else actual_grand_total

        reconciled_budget = BudgetBreakdown(
            total_estimated=actual_grand_total,
            currency=preferences.budget_currency if preferences else "INR",
            categories=[
                CategoryCost(name="Accommodation", amount=round(total_hotel, 2)),
                CategoryCost(name="Food & Dining", amount=round(total_meals, 2)),
                CategoryCost(name="Attractions & Activities", amount=round(total_attractions, 2)),
                CategoryCost(name="Local Transport", amount=round(total_transport, 2)),
            ],
            is_within_budget=actual_grand_total <= user_total_budget,
            adjustment_suggestions=[] if actual_grand_total <= user_total_budget else ["Consider booking budget stays or using public transport."]
        )

        return {
            "itinerary": [day.model_dump() for day in final_response.itinerary],
            "budget_breakdown": reconciled_budget,
            "completed_agents": ["ItineraryAgent"],
        }

    except Exception as e:
        logger.error(f"ItineraryAgent failed: {e}")
        return {"itinerary": [], "failed_agents": ["ItineraryAgent"]}
