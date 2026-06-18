"""
Supervisor agent for managing the multi-agent routing.
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from utils.llm_loader import invoke_with_fallback
from prompt_library.supervisor_prompt import SYSTEM_PROMPT
from logger.logging import get_logger

logger = get_logger(__name__)

class RouteSelection(BaseModel):
    """Structured output for the supervisor's routing decision."""
    reasoning: str = Field(description="Explanation of why this route was chosen based on the rules.")
    next_agents: List[str] = Field(description="Ordered list of agents to invoke. Empty list if 'FINISH'.")

def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the current state and determines which agents should run next.
    Applies explicit business rules for routing.
    """
    logger.info("Supervisor agent invoked to determine routing.")
    
    # Extract current state components
    user_query = state.get("query", "")
    preferences = state.get("preferences")
    weather = state.get("weather_info")
    budget = state.get("budget_breakdown")
    itinerary = state.get("itinerary", [])
    critic = state.get("critic_review")
    
    # Build status summary for the LLM
    status_summary = f"User Query: {user_query}\n\n"
    
    status_summary += "Current State Status:\n"
    status_summary += f"- Preferences Extracted: {preferences is not None}\n"
    if preferences:
        status_summary += f"- Is Domestic Travel: {preferences.is_domestic}\n"
        status_summary += f"- Explicit Dates Provided: {preferences.start_date is not None and preferences.end_date is not None}\n"
        
    status_summary += f"- Weather Fetched: {weather is not None}\n"
    status_summary += f"- Budget Calculated: {budget is not None}\n"
    status_summary += f"- Itinerary Drafted: {len(itinerary) > 0}\n"
    status_summary += f"- Critic Reviewed: {critic is not None}\n"
    
    if critic:
        status_summary += f"- Critic Score: {critic.overall_score}/10\n"
        status_summary += f"- Requires Revision: {critic.requires_revision}\n"
        
    if preferences:
        status_summary += f"- Explicit Total Budget Provided: {preferences.total_budget > 0} (If True, BudgetAgent runs in validation-only mode)\n"

    system_message = SystemMessage(content=SYSTEM_PROMPT)
    human_message = HumanMessage(content=status_summary)
    
    def build_chain(llm):
        return llm.with_structured_output(RouteSelection)

    try:
        selection = invoke_with_fallback(build_chain, [system_message, human_message])
        logger.info(f"Supervisor routing reasoning: {selection.reasoning}")
        logger.info(f"Supervisor selected sequence: {selection.next_agents}")
        
        return {"next_agent_sequence": selection.next_agents}
        
    except Exception as e:
        logger.error(f"Supervisor LLM call failed: {e}")
        # Safe fallback sequence if supervisor crashes
        fallback_sequence = []
        if not preferences:
            fallback_sequence.append("PreferenceExtractor")
        if not weather:
            fallback_sequence.append("WeatherAgent")
        if not budget:
            fallback_sequence.append("BudgetAgent")
        if not itinerary:
            fallback_sequence.append("ItineraryAgent")
            
        logger.warning(f"Using safe fallback sequence: {fallback_sequence}")
        return {"next_agent_sequence": fallback_sequence}
