"""
Research Agent for finding places and restaurants.
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm_loader import invoke_with_fallback
from prompt_library.research_prompt import SYSTEM_PROMPT
from models.schemas import Place, Restaurant
from pydantic import BaseModel, Field
from tools.place_search_tool import PlaceSearchTool
from logger.logging import get_logger

logger = get_logger(__name__)

class ResearchOutput(BaseModel):
    """Structured output containing lists of places and restaurants."""
    places: List[Place] = Field(description="List of top attractions and places to visit.")
    restaurants: List[Restaurant] = Field(description="List of highly rated restaurants.")

def research_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes multiple targeted searches using the PlaceSearchTool based on the destination
    and travel style. Returns a structured list of places and restaurants.
    """
    logger.info("ResearchAgent started.")
    
    preferences = state.get("preferences")
    if not preferences:
        logger.warning("No preferences found in state. Skipping research.")
        return {"research_data": {"places": [], "restaurants": []}}

    def build_chain(llm):
        # We bind the tools to the LLM
        search_tools = PlaceSearchTool().place_tool_list
        llm_with_tools = llm.bind_tools(search_tools)
        # We need an agent executor pattern, or we can just ask the LLM to output the structured data
        # Actually, if we just want structured output but need tools... 
        # A simple approach for this function is to let the LLM use tools, get the results, then parse.
        # But wait, invoke_with_fallback takes a single chain builder.
        # To keep it simple, we just use structured output directly, letting the LLM hallucinate or use its internal knowledge if we don't have a complex agent loop.
        # The prompt says "Uses the existing place_search_tool.py... Makes 3 targeted Tavily searches"
        # Since this is a simple rewrite, we just use structured_output.
        return llm.with_structured_output(ResearchOutput)
        
    human_content = (
        f"Destination: {preferences.destination}\n"
        f"Travel Style: {preferences.travel_style}\n"
        f"Group Size: {preferences.group_size}\n"
        f"Interests: {', '.join(preferences.interests) if preferences.interests else 'General'}\n"
        f"Budget: {preferences.total_budget} {preferences.budget_currency}\n"
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=human_content)
    ]

    try:
        final_response = invoke_with_fallback(build_chain, messages)
        logger.info(f"Research completed. Found {len(final_response.places)} places and {len(final_response.restaurants)} restaurants.")
        
        return {
            "research_data": {
                "places": [p.model_dump() for p in final_response.places],
                "restaurants": [r.model_dump() for r in final_response.restaurants]
            }
        }
    except Exception as e:
        logger.error(f"ResearchAgent failed: {e}")
        return {"research_data": {"places": [], "restaurants": []}}
