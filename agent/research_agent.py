"""
Research Agent for finding places and restaurants.
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from utils.llm_loader import invoke_with_fallback
from prompt_library.research_prompt import SYSTEM_PROMPT
from models.schemas import Place, Restaurant, Hotel
from pydantic import BaseModel, Field
from tools.place_search_tool import PlaceSearchTool
from logger.logging import get_logger

logger = get_logger(__name__)

class ResearchOutput(BaseModel):
    """Structured output containing lists of places, hotels, restaurants, and famous local foods."""
    places: List[Place] = Field(description="List of top attractions and places to visit.")
    hotels: List[Hotel] = Field(description="List of top hotels located strictly within the destination.", default_factory=list)
    restaurants: List[Restaurant] = Field(description="List of highly rated restaurants.")
    famous_local_dishes: List[str] = Field(description="List of famous local dishes, street food, and specialties of the destination.", default_factory=list)

def research_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes multiple targeted searches using the PlaceSearchTool based on the destination
    and travel style. Returns a structured list of places and restaurants.
    """
    logger.info("ResearchAgent started.")
    
    preferences = state.get("preferences")
    if not preferences:
        logger.warning("No preferences found in state. Skipping research.")
        return {"research_data": {"places": [], "hotels": [], "restaurants": [], "famous_local_dishes": []}, "failed_agents": ["ResearchAgent"]}

    search_tools = PlaceSearchTool().place_search_tool_list
    
    def build_tool_chain(llm):
        return llm.bind_tools(search_tools)
        
    def build_structured_chain(llm):
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
        response_msg = invoke_with_fallback(build_tool_chain, messages)
        messages.append(response_msg)
        
        tool_map = {t.name: t for t in search_tools}
        if hasattr(response_msg, "tool_calls") and response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                if tool_name in tool_map:
                    logger.info(f"ResearchAgent executing tool: {tool_name} with args {tool_args}")
                    tool_result = tool_map[tool_name].invoke(tool_args)
                    messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))
            
            final_response = invoke_with_fallback(build_structured_chain, messages)
        else:
            logger.info("ResearchAgent executing search tools directly as fallback.")
            for tool_name in ["search_attractions", "search_hotels", "search_restaurants", "search_local_food", "search_activities"]:
                if tool_name in tool_map:
                    try:
                        tool_res = tool_map[tool_name].invoke({"place": preferences.destination})
                        messages.append(HumanMessage(content=f"Search results from {tool_name}:\n{tool_res}"))
                    except Exception as te:
                        logger.warning(f"Fallback search {tool_name} failed: {te}")
            final_response = invoke_with_fallback(build_structured_chain, messages)
            
        logger.info(f"Research completed. Found {len(final_response.places)} places, {len(final_response.hotels)} hotels, {len(final_response.restaurants)} restaurants, {len(final_response.famous_local_dishes)} local dishes.")
        
        return {
            "research_data": {
                "places": [p.model_dump() for p in final_response.places],
                "hotels": [h.model_dump() for h in final_response.hotels],
                "restaurants": [r.model_dump() for r in final_response.restaurants],
                "famous_local_dishes": final_response.famous_local_dishes
            },
            "completed_agents": ["ResearchAgent"]
        }
    except Exception as e:
        logger.error(f"ResearchAgent failed: {e}")
        # Mark as failed so the supervisor never routes here again
        return {
            "research_data": {"places": [], "restaurants": []},
            "failed_agents": ["ResearchAgent"]
        }
