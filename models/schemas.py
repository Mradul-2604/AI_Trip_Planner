"""
Pydantic schemas for the WanderBot multi-agent system.
Defines all structured inputs and outputs for the agents.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class UserPreferences(BaseModel):
    """Structured preferences extracted from the user's raw query."""
    destination: str = Field(description="The target destination for the trip.")
    duration: int = Field(description="Duration of the trip in days.")
    total_budget: float = Field(description="Total budget for the trip.")
    budget_currency: str = Field(description="Currency of the budget, e.g., 'USD', 'INR'.")
    travel_style: str = Field(description="Style of travel, e.g., 'luxury', 'budget', 'offbeat'.")
    interests: List[str] = Field(description="List of specific interests, e.g., 'history', 'food', 'nature'.", default_factory=list)
    things_to_avoid: List[str] = Field(description="List of things to avoid, e.g., 'crowds', 'hiking'.", default_factory=list)
    group_size: int = Field(description="Number of people traveling.", default=1)
    travel_dates: Optional[str] = Field(description="Specific dates of travel if provided, otherwise None.", default=None)
    is_domestic: bool = Field(description="True if the trip is within India (assuming user is from India), False otherwise.", default=True)

class Place(BaseModel):
    """Structured data for a place or attraction."""
    name: str = Field(description="Name of the place.")
    description: str = Field(description="Short description of the place.", default="No description provided.")
    category: str = Field(description="Category, e.g., 'attraction', 'activity', 'park'.", default="attraction")
    entry_fee: str = Field(description="Estimated entry fee, including currency.", default="Unknown")
    recommended_duration_hours: float = Field(description="Recommended hours to spend here.", default=1.0)
    best_time_to_visit: str = Field(description="Best time of day or season to visit.", default="Anytime")

class Restaurant(BaseModel):
    """Structured data for a restaurant or food place."""
    name: str = Field(description="Name of the restaurant.")
    cuisine: str = Field(description="Type of cuisine served.")
    average_cost: str = Field(description="Average cost for a meal, including currency.")
    rating: str = Field(description="Rating or popularity.")
    description: str = Field(description="Short description of the food and vibe.")

class Hotel(BaseModel):
    """Structured data for accommodation."""
    name: str = Field(description="Name of the hotel.")
    stars: str = Field(description="Star rating or category of the hotel.")
    price_per_night: str = Field(description="Estimated price per night.")
    amenities: List[str] = Field(description="List of key amenities.", default_factory=list)
    description: str = Field(description="Short description of the accommodation.")

class WeatherInfo(BaseModel):
    """Structured weather information for the destination."""
    summary: str = Field(description="General summary of the weather.")
    temperature_range: str = Field(description="Expected temperature range, e.g., '15°C - 25°C'.")
    conditions: str = Field(description="Specific conditions, e.g., 'Sunny', 'Rainy'.")
    packing_suggestions: List[str] = Field(description="List of suggested items to pack based on weather.", default_factory=list)
    travel_warnings: List[str] = Field(description="Any weather-related warnings.", default_factory=list)
    data_source: str = Field(description="Source of the data: 'live_api' or 'llm_fallback'.")
    fallback_used: bool = Field(description="True if an API fallback was used due to error or missing dates.", default=False)

class CategoryCost(BaseModel):
    name: str = Field(description="Name of the category, e.g., 'Accommodation', 'Food'.")
    amount: float = Field(description="Estimated amount for this category.")

class BudgetBreakdown(BaseModel):
    """Structured budget estimation."""
    total_estimated: float = Field(description="Total estimated cost for the entire trip.")
    currency: str = Field(description="Currency of the estimated costs.")
    categories: List[CategoryCost] = Field(description="Breakdown of costs by category.", default_factory=list)
    is_within_budget: bool = Field(description="True if total estimated is less than or equal to total budget.")
    adjustment_suggestions: List[str] = Field(description="Suggestions to adjust if over budget.", default_factory=list)

class MealInfo(BaseModel):
    """Information for a planned meal."""
    meal_type: str = Field(description="Breakfast, Lunch, or Dinner.")
    restaurant_name: str = Field(description="Name of the suggested restaurant.")
    estimated_cost: str = Field(description="Estimated cost of the meal.")

class AttractionVisit(BaseModel):
    """Information for a planned attraction visit."""
    place: Place = Field(description="The place to visit.")
    timing: str = Field(description="Suggested timing, e.g., '10:00 AM - 12:30 PM'.")

class Transport(BaseModel):
    """Information for local transport."""
    mode: str = Field(description="Mode of transport, e.g., 'Taxi', 'Metro', 'Walking'.")
    estimated_cost: str = Field(description="Estimated cost of the transport.")

class DayPlan(BaseModel):
    """A fully planned itinerary for a single day."""
    day_number: int = Field(description="The day number of the trip.")
    theme: str = Field(description="Overall theme or focus of the day.")
    hotel: Hotel = Field(description="Accommodation for this day.")
    meals: List[MealInfo] = Field(description="List of planned meals for the day.")
    attractions: List[AttractionVisit] = Field(description="List of attractions to visit.")
    activities: List[str] = Field(description="List of other activities or leisure time.", default_factory=list)
    transport: Transport = Field(description="Primary transport for the day.")
    estimated_day_cost: float = Field(description="Estimated total cost for this specific day.")

class CriticReview(BaseModel):
    """Review and scoring of the generated itinerary."""
    logical_flow_score: float = Field(description="Score for logical flow (0-10).", default=5.0)
    budget_alignment_score: float = Field(description="Score for budget alignment (0-10).", default=5.0)
    weather_suitability_score: float = Field(description="Score for weather suitability (0-10).", default=5.0)
    preference_match_score: float = Field(description="Score for preference match (0-10).", default=5.0)
    overall_score: float = Field(description="Overall score out of 10.")
    warnings: List[str] = Field(description="List of issues or warnings found in the plan.", default_factory=list)
    highlights: List[str] = Field(description="List of highly positive aspects of the plan.", default_factory=list)
    requires_revision: bool = Field(description="True if overall_score < 7, requiring the itinerary agent to try again.")
    revision_instructions: List[str] = Field(description="Specific, actionable changes for the next iteration.", default_factory=list)

class RevisionRecord(BaseModel):
    """Record of a reflection loop iteration."""
    iteration: int = Field(description="The iteration number.")
    score: float = Field(description="The overall score received in this iteration.")
    changes_made: str = Field(description="Summary of changes instructed or made.")

class TravelPlan(BaseModel):
    """The final compiled travel plan returned to the user."""
    preferences: Optional[UserPreferences] = Field(description="The user's extracted preferences.", default=None)
    weather: Optional[WeatherInfo] = Field(description="Weather forecast or fallback info.", default=None)
    budget: Optional[BudgetBreakdown] = Field(description="The structured budget breakdown.", default=None)
    itinerary: List[DayPlan] = Field(description="The detailed day-by-day itinerary.", default_factory=list)
    critic_review: Optional[CriticReview] = Field(description="The final review from the critic agent.", default=None)
    revision_history: List[RevisionRecord] = Field(description="History of revisions made during the reflection loop.", default_factory=list)
    data_freshness: Dict[str, str] = Field(description="Dictionary tracking which agents used live vs fallback data.", default_factory=dict)
    generated_at: datetime = Field(description="Timestamp of when the plan was generated.", default_factory=datetime.now)
