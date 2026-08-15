import os
import json
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

class TavilyPlaceSearchTool:
    def __init__(self):
        if not os.environ.get("TAVILY_API_KEY") and os.environ.get("TAVILAY_API_KEY"):
            os.environ["TAVILY_API_KEY"] = os.environ["TAVILAY_API_KEY"]

    def tavily_search_attractions(self, place: str) -> dict:
        """
        Searches for attractions in the specified place using TavilySearch.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"top famous tourist places, historic sights and attractions in {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result
    
    def tavily_search_hotels(self, place: str) -> dict:
        """
        Searches for real top-rated hotels, resorts, or homestays strictly located inside the specified place.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"best hotels, lodges, and accommodation stays strictly located in {place} with price and address"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def tavily_search_restaurants(self, place: str) -> dict:
        """
        Searches for available restaurants in the specified place using TavilySearch.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"top rated restaurants, eateries, and food joints with addresses in {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def tavily_search_local_food(self, place: str) -> dict:
        """
        Searches for famous local dishes, specialties, street food, and must-try delicacies in the specified place.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"famous local food, must-try traditional dishes, sweets and street food specialties of {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result
    
    def tavily_search_activity(self, place: str) -> dict:
        """
        Searches for popular activities in the specified place using TavilySearch.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"things to do and activities in {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def tavily_search_transportation(self, place: str) -> dict:
        """
        Searches for available modes of transportation in the specified place using TavilySearch.
        """
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"What are the different modes of transportations available in {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result