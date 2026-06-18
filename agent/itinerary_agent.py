"""
Itinerary Agent to synthesize all gathered data into a structured DayPlan.
"""
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from utils.llm_loader import invoke_with_fallback
from prompt_library.itinerary_prompt import SYSTEM_PROMPT
from models.schemas import DayPlan
from logger.logging import get_logger

logger = get_logger(__name__)

class ItineraryOutput(BaseModel):
    """Structured output containing a list of daily plans."""
    itinerary: List[DayPlan] = Field(description="The final day-by-day itinerary.")

def itinerary_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes preferences, weather, budget, and research data into a chronological
    DayPlan itinerary. Applies critic revisions if they exist.
    """
    logger.info("ItineraryAgent started.")
    
    preferences = state.get("preferences")
    if not preferences:
        logger.warning("No preferences found. Returning empty itinerary.")
        return {"itinerary": []}
        
    weather = state.get("weather_info")
    budget = state.get("budget_breakdown")
    research_data = state.get("research_data", {})
    critic_review = state.get("critic_review")
    
    # Build prompt content
    content = f"Destination: {preferences.destination}\n"
    content += f"Duration: {preferences.duration} days\n"
    content += f"Travel Style: {preferences.travel_style}\n\n"
    
    if weather:
        content += f"Weather: High {weather.temperature_high}C, Low {weather.temperature_low}C, {weather.general_condition}\n"
        
    if budget:
        content += f"Budget Limit: {budget.total_estimated} {budget.currency}\n\n"
        
    content += f"Research Places: {[p.get('name') for p in research_data.get('places', [])]}\n"
    content += f"Research Restaurants: {[r.get('name') for r in research_data.get('restaurants', [])]}\n\n"
    
    if critic_review and critic_review.requires_revision:
        content += "CRITIC REVISIONS REQUIRED:\n"
        content += "\n".join([f"- {instr}" for instr in critic_review.revision_instructions])
        
    def build_chain(llm):
        return llm.with_structured_output(ItineraryOutput)
        
    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=content)
        ]
        
        final_response = invoke_with_fallback(build_chain, messages)
        logger.info(f"Itinerary created with {len(final_response.itinerary)} days.")
        
        return {"itinerary": [day.model_dump() for day in final_response.itinerary]}
        
    except Exception as e:
        logger.error(f"ItineraryAgent failed: {e}")
        return {"itinerary": []}
