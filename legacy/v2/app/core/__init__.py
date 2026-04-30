"""
Core Package - LinkedIn Content Generation Engine
===============================================
Clean 3-layer architecture for LinkedIn content generation.
"""

# Load environment variables
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .generator import LinkedInGenerator
from .models import (
    PostRequest, PostResponse, GenerationMode,
    ContentType, Tone, Audience
)
from .llm import LLMProvider
from .rag import RAGEngine

__version__ = "2.0.0"
__author__ = "LinkedIn Content Studio"
__all__ = [
    "LinkedInGenerator",
    "PostRequest",
    "PostResponse",
    "GenerationMode",
    "ContentType",
    "Tone",
    "Audience",
    "LLMProvider",
    "RAGEngine"
]
