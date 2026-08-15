"""
Supervisor agent — single-pass, runs ONCE at workflow start.

In the new linear pipeline the Supervisor does NOT route between agents.
Its only job is to extract the user's query from the messages list
and store it in state so downstream agents can read it via state['query'].
"""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from logger.logging import get_logger
from utils.llm_loader import invoke_with_fallback
from models.schemas import SupervisorDecision

logger = get_logger(__name__)


def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts the user query from state['messages'] and stores it as state['query'].
    Uses an LLM to determine if the intent is 'plan_trip' or 'general_chat'.
    """
    logger.info("Supervisor: initializing workflow, extracting user query.")

    # Pull query from messages list (most recent HumanMessage)
    query = state.get("query", "").strip()
    if not query:
        messages: List = state.get("messages", [])
        for msg in reversed(messages):
            content = getattr(msg, "content", "") if hasattr(msg, "content") else str(msg)
            if content and content.strip():
                query = content.strip()
                logger.info("Supervisor: extracted query from messages list.")
                break

    if not query:
        logger.warning("Supervisor: no query found in state or messages.")
        query = "Plan a trip"

    logger.info(f"Supervisor: query = '{query[:80]}{'...' if len(query) > 80 else ''}'")
    
    def build_chain(llm):
        return llm.with_structured_output(SupervisorDecision)
        
    system_prompt = (
        "You are a routing supervisor for an AI Trip Planner.\n"
        "Your job is to determine the user's intent based on their query.\n"
        "If the user is asking to plan a trip, generate a new itinerary, or create a travel plan, output 'plan_trip'.\n"
        "If the user is asking a conversational follow-up question about an existing plan, asking for details about a specific place (e.g. 'what is toit?'), or just making general chatter, output 'general_chat'."
    )
    
    try:
        decision = invoke_with_fallback(build_chain, [SystemMessage(content=system_prompt), HumanMessage(content=query)])
        intent = decision.intent
        logger.info(f"Supervisor determined intent: {intent}")
    except Exception as e:
        logger.error(f"Supervisor LLM failed: {e}")
        intent = "plan_trip" # fallback
        
    return {"query": query, "intent": intent}
