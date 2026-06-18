# WanderBot - AI Trip Planner

WanderBot is an intelligent, agentic travel planning application that helps users plan their trips effortlessly. It leverages a modern tech stack combining a FastAPI backend, a Streamlit frontend, and an advanced LangGraph-based agentic workflow. The AI agent utilizes various tools to gather weather information, search for places, calculate expenses, and convert currencies to provide a comprehensive and detailed travel plan.

## Features

- **Agentic Workflow**: Built using LangGraph, the AI agent can dynamically decide which tools to use to fulfill the user's travel query.
- **Weather Information**: Retrieves current weather and forecasts using OpenWeatherMap.
- **Place Search**: Uses Tavily search to find attractions, restaurants, activities, and transportation options for any destination.
- **Expense Calculator**: Built-in tool for the agent to estimate trip expenses.
- **Currency Conversion**: Converts currencies to help plan international trips.
- **Interactive UI**: A clean and simple Streamlit interface for users to enter their travel queries.
- **RESTful API**: A FastAPI backend that handles the query processing and interacts with the LLM.

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **AI/LLM**: LangChain, LangGraph, Groq (default), OpenAI (optional)
- **Search & Tools**: Tavily Search API, OpenWeatherMap API

## Project Structure

```
AI_Trip_Planner/
├── agent/
│   └── agentic_workflow.py    # LangGraph agent setup and logic
├── config/                    # Configuration loaders
├── env/                       # Environment utilities
├── exception/                 # Custom exceptions
├── logger/                    # Logging utilities
├── prompt_library/            # System prompts for the AI agent
├── tools/                     # LangChain tools for the agent
│   ├── arithmetic_op_tool.py
│   ├── currency_conversion_tool.py
│   ├── expense_calculator_tool.py
│   ├── place_search_tool.py
│   └── weather_info_tool.py
├── utils/                     # Utility functions (Model loader, API wrappers, etc.)
├── main.py                    # FastAPI application entry point
├── streamlit_app.py           # Streamlit frontend application
├── requirements.txt           # Python dependencies
└── pyproject.toml             # Project metadata
```

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd AI_Trip_Planner
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```
   Activate the virtual environment:
   - On Windows: `.venv\Scripts\activate`
   - On macOS/Linux: `source .venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   OPENWEATHERMAP_API_KEY=your_openweather_api_key_here
   # OPENAI_API_KEY=your_openai_api_key_here (if using OpenAI)
   ```

## Running the Application

To run the application, you need to start both the FastAPI backend and the Streamlit frontend.

### 1. Start the FastAPI Backend
Run the following command in your terminal:
```bash
uvicorn main:app --reload
```
The backend will start running at `http://localhost:8000`.

### 2. Start the Streamlit Frontend
Open a new terminal window, activate your virtual environment, and run:
```bash
streamlit run streamlit_app.py
```
The frontend will open in your default browser (usually at `http://localhost:8501`).

## Usage Example
1. Go to the Streamlit app in your browser.
2. In the input box, type a query like: *"Plan a trip to Goa for 5 days."*
3. Click **Send**.
4. WanderBot will use its agentic workflow to search for places, check the weather, and estimate expenses to return a detailed markdown-formatted travel plan.