# 🌍 WanderBot: Multi-Agent Travel Planner

WanderBot is a highly sophisticated, multi-agent travel planning system built on **LangGraph**. By coordinating a team of specialized AI agents, WanderBot handles the complex logistics of building a personalized itinerary—researching places, checking weather, calculating accurate budgets, and verifying constraints through a rigid critique/reflection loop.

It features long-term memory (ChromaDB) for personalized trip context, strict Pydantic schemas for structured data output, and Server-Sent Events (SSE) for a real-time, responsive Streamlit dashboard.

---

## 🏗️ Architecture

WanderBot operates on a **Supervisor-Worker** architectural pattern using LangGraph. The Supervisor dynamically routes tasks based on the current system state, ensuring strict business rules (e.g. running the Critic reflection loop). If API rate limits are hit (e.g. Groq 429s), the system seamlessly falls back to Gemini 2.0 Flash.

```text
                        +-------------------+
                        |   User Request    |
                        +---------+---------+
                                  |
                                  v
                        +-------------------+
             +--------> |  SUPERVISOR AGENT | <---------+
             |          +---------+---------+           |
             |                    |                     |
             v                    v                     v
   +-------------------+  +-------------------+  +-------------------+
   | PreferenceExtract |  |   WeatherAgent    |  |   ResearchAgent   |
   | (Extracts context |  | (Live OpenWeather |  | (Tavily/Foursquare|
   |  & ChromaDB RAG)  |  |  or fallbacks)    |  |  places search)   |
   +---------+---------+  +---------+---------+  +---------+---------+
             |                    |                     |
             +--------------------+---------------------+
                                  |
                                  v
   +-------------------+  +-------------------+  +-------------------+
   |   BudgetAgent     |  |  ItineraryAgent   |  |   CriticAgent     |
   | (Math calculators |->| (Synthesizes all  |->| (Reflection loop: |
   |  & FX converters) |  |  data into days)  |  |  Scores < 7.0     |
   +---------+---------+  +-------------------+  |  trigger rework)  |
                                                 +---------+---------+
                                                           |
                        +-------------------+              |
                        | FINAL TRAVEL PLAN | <------------+
                        +-------------------+
```

*(You can also dynamically render the LangGraph mermaid flowchart by running the backend and visiting `GET /graph`)*

---

## ✨ Key Features
- **Intelligent Orchestration:** LangGraph supervisor controls state, deciding which agent executes next based on extracted requirements.
- **Automated Critique Loop:** The `CriticAgent` evaluates itineraries on 4 dimensions (Logical flow, Budget, Weather, Preferences) and triggers automatic revisions if the score is below 7.0/10.
- **Robust LLM Fallback Mechanism:** Custom `FallbackLLMWrapper` automatically intercepts Groq 429 rate limit errors and re-routes exactly to Google Gemini without losing context.
- **Long-Term Memory:** Uses ChromaDB to remember your past preferences across multiple sessions (e.g., "I prefer luxury travel").
- **Live SSE Streaming UI:** The Streamlit frontend beautifully streams the backend LangGraph execution node-by-node in real-time.
- **External Tools:** Real-time calculators, currency converters, and web-search APIs.

---

## 🛠️ Tech Stack
- **Frameworks:** LangGraph, LangChain, FastAPI, Streamlit
- **LLMs:** Groq (`llama-3.3-70b-versatile`), Google Generative AI (`gemini-2.0-flash`)
- **Memory & State:** ChromaDB, `MemorySaver` (LangGraph Short-Term State)
- **Data Validation:** Pydantic (Strict structured LLM outputs)
- **Tools:** Tavily Search, OpenWeatherMap, API Ninjas Exchange Rate

---

## 🚀 Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/WanderBot.git
   cd WanderBot
   ```

2. **Setup Python Environment**
   ```bash
   uv venv
   # Activate your virtual environment (.venv/Scripts/activate on Windows)
   uv pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY="your_groq_api_key"
   GOOGLE_API_KEY="your_gemini_api_key"
   TAVILAY_API_KEY="your_tavily_api_key"
   OPENWEATHERMAP_API_KEY="your_openweathermap_api_key"
   EXCHANGE_RATE_API_KEY="your_exchange_api_key"
   ```

4. **Run the Backend (FastAPI)**
   ```bash
   uvicorn main:app --reload
   ```

5. **Run the Frontend (Streamlit)**
   Open a new terminal window:
   ```bash
   uv run streamlit run streamlit_app.py
   ```

---

## 💬 Example Queries
- *"Plan a 5-day luxury trip to Paris in October. I love art history and fine dining. My budget is $5,000 USD."*
- *"I'm going to Tokyo for 3 days next week. I need a tight budget itinerary focusing entirely on anime and street food."*
- *"Book a relaxing weekend getaway in Malibu. (The system will remember your previous preferences if stored!)"*