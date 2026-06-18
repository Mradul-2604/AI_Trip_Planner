"""
LangGraph Multi-Agent Workflow definition.
"""
import operator
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

from models.schemas import (
    UserPreferences, WeatherInfo, BudgetBreakdown, 
    DayPlan, CriticReview, RevisionRecord, TravelPlan
)
from agent.supervisor import supervisor_node
from agent.preference_extractor import preference_extractor_node
from agent.research_agent import research_agent_node
from agent.weather_agent import weather_agent_node
from agent.budget_agent import budget_agent_node
from agent.itinerary_agent import itinerary_agent_node
from agent.critic_agent import critic_agent_node
from memory.short_term import get_checkpointer

# Reducer for history
def append_history(left: List[RevisionRecord], right: List[RevisionRecord]) -> List[RevisionRecord]:
    if not left:
        left = []
    if not right:
        return left
    return left + right

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    past_context: str
    preferences: Optional[UserPreferences]
    research_data: Optional[Dict[str, Any]]
    weather_info: Optional[WeatherInfo]
    budget_breakdown: Optional[BudgetBreakdown]
    itinerary: Optional[List[DayPlan]]
    critic_review: Optional[CriticReview]
    iteration_count: int
    revision_history: Annotated[List[RevisionRecord], append_history]
    data_freshness: Dict[str, str]
    next_agent: str
    final_plan: Optional[TravelPlan]

# Enhanced critic agent wrapper to update iteration count and history
def critic_agent_wrapper(state: AgentState) -> Dict[str, Any]:
    result = critic_agent_node(state)
    review: CriticReview = result["critic_review"]
    iteration = state.get("iteration_count", 0) + 1
    
    history_update = []
    if review.requires_revision:
        history_update.append(RevisionRecord(
            iteration=iteration,
            score=review.overall_score,
            changes_made="; ".join(review.revision_instructions)
        ))
        
    return {
        "critic_review": review,
        "iteration_count": iteration,
        "revision_history": history_update
    }

def supervisor_router(state: AgentState) -> str:
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "FINISH":
        return END
    return next_agent

def reflection_router(state: AgentState) -> str:
    review = state.get("critic_review")
    iteration = state.get("iteration_count", 0)
    
    if review and review.requires_revision and iteration < 3:
        return "ItineraryAgent"
    
    # If no revision needed, compile final plan and end
    # We can handle compiling the final plan in a separate node or just before returning.
    # For simplicity, we just end here and compile it in the API response.
    return END

class GraphBuilder:
    def __init__(self, model_provider: str = "groq"):
        # Model provider is handled by ModelLoader directly via ENV, 
        # but we keep this for compatibility
        self.model_provider = model_provider

    def build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("Supervisor", supervisor_node)
        workflow.add_node("PreferenceExtractor", preference_extractor_node)
        workflow.add_node("ResearchAgent", research_agent_node)
        workflow.add_node("WeatherAgent", weather_agent_node)
        workflow.add_node("BudgetAgent", budget_agent_node)
        workflow.add_node("ItineraryAgent", itinerary_agent_node)
        workflow.add_node("CriticAgent", critic_agent_wrapper)
        
        # Add edges
        workflow.add_edge(START, "Supervisor")
        
        # Supervisor routes to workers
        workflow.add_conditional_edges(
            "Supervisor",
            supervisor_router,
            {
                "PreferenceExtractor": "PreferenceExtractor",
                "ResearchAgent": "ResearchAgent",
                "WeatherAgent": "WeatherAgent",
                "BudgetAgent": "BudgetAgent",
                "ItineraryAgent": "ItineraryAgent",
                "CriticAgent": "CriticAgent",
                END: END
            }
        )
        
        # Workers route back to Supervisor
        workflow.add_edge("PreferenceExtractor", "Supervisor")
        workflow.add_edge("ResearchAgent", "Supervisor")
        workflow.add_edge("WeatherAgent", "Supervisor")
        workflow.add_edge("BudgetAgent", "Supervisor")
        
        # Itinerary goes to Critic
        workflow.add_edge("ItineraryAgent", "CriticAgent")
        
        # Critic goes to reflection router
        workflow.add_conditional_edges(
            "CriticAgent",
            reflection_router,
            {
                "ItineraryAgent": "ItineraryAgent",
                END: END
            }
        )
        
        # Compile with checkpointer
        checkpointer = get_checkpointer()
        self.graph = workflow.compile(checkpointer=checkpointer)
        return self.graph

    def __call__(self):
        return self.build_graph()