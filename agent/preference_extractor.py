"""
Preference Extractor Agent.
Extracts structured travel preferences from the user's natural language query.
"""
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm_loader import invoke_with_fallback
from prompt_library.preference_prompt import SYSTEM_PROMPT
from models.schemas import UserPreferences
from memory.long_term import LongTermMemory
from logger.logging import get_logger

logger = get_logger(__name__)

def preference_extractor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses user query into structured UserPreferences.
    Checks ChromaDB for long-term user context and injects it into the prompt.
    """
    logger.info("PreferenceExtractor Agent started.")
    user_query = state.get("query", "")
    user_id = state.get("user_id", "default_user")

    # Step 1: Retrieve context from Long Term Memory
    try:
        memory = LongTermMemory()
        past_context = memory.retrieve_preferences(user_id=user_id, current_query=user_query)
        logger.info("Successfully retrieved past context from ChromaDB.")
    except Exception as e:
        logger.warning(f"Failed to retrieve long term memory: {e}")
        past_context = "No previous context found."

    system_content = f"{SYSTEM_PROMPT}\n\n[PAST USER CONTEXT]\n{past_context}"
    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_query)
    ]

    def build_chain(llm):
        return llm.with_structured_output(UserPreferences)

    try:
        # Step 2: Extract preferences
        response = invoke_with_fallback(build_chain, messages)
        
        # Step 3: Save the new query to Long Term Memory
        try:
            memory.save_preference(user_id=user_id, query=user_query, structured_prefs=response.model_dump())
        except Exception as e:
            logger.warning(f"Failed to save long term memory: {e}")
            
        logger.info(f"Successfully extracted preferences for destination: {response.destination}")
        return {"preferences": response}
    
    except Exception as e:
        logger.error(f"LLM failed to generate structured UserPreferences: {e}")
        # Fallback to minimal valid schema if everything fails
        fallback_prefs = UserPreferences(
            destination="Unknown",
            duration=3,
            travel_style="Balanced",
            budget_currency="USD",
            total_budget=0.0
        )
        return {"preferences": fallback_prefs}
