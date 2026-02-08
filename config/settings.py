import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# Stable Groq model (safe for demos & Streamlit apps)
MODEL_NAME = "llama-3.1-8b-instant"

TEMPERATURE = 0.7
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_llm(temperature=0.6):
    """Initialize ChatGroq LLM with specified temperature."""
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=MODEL_NAME,
        temperature=temperature
    )

def get_llm_deterministic():
    """Initialize ChatGroq LLM with low temperature for deterministic output."""
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=MODEL_NAME,
        temperature=0.2
    )
