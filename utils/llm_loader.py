import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from logger.logging import get_logger

load_dotenv()
logger = get_logger(__name__)

def get_primary_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.warning("GROQ_API_KEY is not set.")
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_api_key, temperature=0.0)

def get_fallback_llm():
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logger.warning("GOOGLE_API_KEY is not set.")
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=google_api_key, temperature=0.0)

def invoke_with_fallback(chain_builder, *args, **kwargs):
    """
    Tries to build and invoke the chain with the primary Groq LLM.
    If a 429 rate limit error occurs, it builds and invokes the chain with Gemini instead.
    
    chain_builder is a function that takes an LLM instance and returns a runnable chain
    (e.g., lambda llm: llm.with_structured_output(Schema))
    """
    try:
        llm = get_primary_llm()
        chain = chain_builder(llm)
        return chain.invoke(*args, **kwargs)
    except Exception as e:
        error_msg = str(e).lower()
        if '429' in error_msg or 'rate limit' in error_msg or 'rate_limit' in error_msg:
            logger.warning('Groq rate limit hit, switching to Gemini fallback')
            try:
                fallback_llm = get_fallback_llm()
                fallback_chain = chain_builder(fallback_llm)
                return fallback_chain.invoke(*args, **kwargs)
            except Exception as fallback_e:
                logger.error(f"Fallback to Gemini also failed: {fallback_e}")
                raise fallback_e
        logger.error(f"Primary LLM failed with non-rate-limit error: {e}")
        raise e
