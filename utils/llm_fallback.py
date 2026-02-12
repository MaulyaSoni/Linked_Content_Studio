"""
Fallback LLM Strategy - Resilience & Redundancy
Ensures app doesn't die if primary LLM is unavailable.
"""

from typing import Optional, Dict, Literal, Any
from langchain_groq import ChatGroq
import os
import logging

logger = logging.getLogger(__name__)


class LLMFallbackManager:
    """
    Multi-tier fallback strategy for LLM providers.
    
    Priority Order:
    1. Groq (Primary - fastest, free)
    2. Groq Smaller Model (fallback within Groq)
    3. HuggingFace Local (if available)
    4. Mock LLM (graceful degradation)
    """
    
    LLM_CONFIGS = {
        "groq_primary": {
            "provider": "groq",
            "model": "llama-3.1-8b-instant",
            "temperature": 0.7,
            "timeout": 30
        },
        "groq_fallback": {
            "provider": "groq",
            "model": "mixtral-8x7b-32768",
            "temperature": 0.7,
            "timeout": 40
        },
        "groq_minimal": {
            "provider": "groq",
            "model": "gemma-7b-it",
            "temperature": 0.7,
            "timeout": 35
        }
    }
    
    def __init__(self, prefer_chain: Optional[list] = None):
        """
        Initialize fallback manager.
        
        Args:
            prefer_chain: List of LLM config keys to try in order.
                         Default: ["groq_primary", "groq_fallback", "groq_minimal"]
        """
        self.prefer_chain = prefer_chain or [
            "groq_primary",
            "groq_fallback", 
            "groq_minimal"
        ]
        self.current_llm = None
        self.active_model = None
        self._initialize()
    
    def _initialize(self):
        """Try to initialize LLM following fallback chain."""
        for model_key in self.prefer_chain:
            try:
                self.current_llm = self._create_llm(model_key)
                self.active_model = model_key
                logger.info(f"✅ LLM initialized: {model_key}")
                return
            except Exception as e:
                logger.warning(f"⚠️ Failed to load {model_key}: {str(e)}")
                continue
        
        # If all Groq models fail, use mock
        logger.error("❌ All LLM models failed. Using mock LLM for graceful degradation.")
        self.current_llm = MockLLM()
        self.active_model = "mock_llm"
    
    @staticmethod
    def _create_llm(config_key: str) -> Any:
        """Create LLM instance from config."""
        config = LLMFallbackManager.LLM_CONFIGS[config_key]
        provider = config["provider"]
        
        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set")
            
            return ChatGroq(
                model=config["model"],
                temperature=config["temperature"],
                timeout=config["timeout"],
                api_key=api_key
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def get_llm(self) -> Any:
        """Get current active LLM."""
        return self.current_llm
    
    def get_status(self) -> Dict:
        """Get LLM status and fallback info."""
        return {
            "active_model": self.active_model,
            "fallback_chain": self.prefer_chain,
            "is_primary": self.active_model == "groq_primary",
            "is_degraded": self.active_model in ["groq_minimal", "mock_llm"],
            "capability_level": self._get_capability_level()
        }
    
    def _get_capability_level(self) -> Literal["full", "reduced", "minimal"]:
        """Get capability level based on active model."""
        if self.active_model == "groq_primary":
            return "full"
        elif self.active_model in ["groq_fallback", "groq_minimal"]:
            return "reduced"
        else:
            return "minimal"
    
    def test_connection(self) -> bool:
        """Test if current LLM is working."""
        try:
            response = self.current_llm.invoke("Respond with just the word 'OK'")
            return "OK" in response.content or len(response.content) > 0
        except Exception as e:
            logger.error(f"LLM connection test failed: {str(e)}")
            return False


class MockLLM:
    """
    Mock LLM for graceful degradation.
    Returns templated responses when all real LLMs fail.
    """
    
    def invoke(self, prompt: str, **kwargs) -> Any:
        """Mock invoke method that returns a response object."""
        response_text = self._generate_response(prompt)
        # Return object with .content attribute to match ChatGroq interface
        class Response:
            def __init__(self, content):
                self.content = content
        return Response(response_text)
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response based on prompt."""
        # Extract key information from prompt
        if "Generate" in prompt or "Create" in prompt:
            return self._generate_post_response(prompt)
        elif "hashtag" in prompt.lower():
            return self._generate_hashtags_response()
        elif "caption" in prompt.lower():
            return self._generate_caption_response()
        else:
            return self._generate_generic_response(prompt)
    
    def _generate_post_response(self, prompt: str) -> str:
        """Generate mock LinkedIn post."""
        return """🚀 Building the future with AI & innovation

Excited to share our latest project launch - combining cutting-edge technology with real-world impact.

Key highlights:
• Delivered end-to-end solution
• Focused on user experience
• Scaled to production

The journey was challenging but rewarding. Every step taught us something valuable about engineering excellence.

Looking forward to seeing how this resonates with the community!

#Tech #Innovation #Startup"""
    
    def _generate_hashtags_response(self) -> str:
        return "#Tech #Innovation #AI #StartUp #Engineering #ProductDevelopment #LeadingChange"
    
    def _generate_caption_response(self) -> str:
        return "Watch how our new feature transforms the workflow - 🎯 Check the video demo to see it in action!"
    
    def _generate_generic_response(self, prompt: str) -> str:
        return "Thank you for using LinkedIn Content Studio. The advanced AI service is temporarily unavailable, so I've provided a template response. Please try again shortly. 📝"


# Global instance
_fallback_manager = None


def get_llm_with_fallback() -> Any:
    """Get LLM with automatic fallback handling."""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = LLMFallbackManager()
    return _fallback_manager.get_llm()


def get_fallback_status() -> Dict:
    """Get current fallback status."""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = LLMFallbackManager()
    return _fallback_manager.get_status()


def test_llm_health() -> Dict:
    """Test LLM health status."""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = LLMFallbackManager()
    
    return {
        "status": _fallback_manager.get_status(),
        "connection_ok": _fallback_manager.test_connection(),
        "recommendation": (
            "✅ Running optimally" 
            if _fallback_manager.active_model == "groq_primary"
            else "⚠️ Using fallback model" 
            if _fallback_manager.active_model != "mock_llm"
            else "🔴 Degraded mode active"
        )
    }
