"""
LLM Provider - Groq Integration
================================
Clean abstraction for LLM interactions with fallbacks.
"""

import os
import logging
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from .models import LLMResult, GenerationConfig


logger = logging.getLogger(__name__)


class LLMProvider:
    """Unified LLM provider with error handling and fallbacks."""
    
    def __init__(self, config: Optional[GenerationConfig] = None):
        """Initialize LLM provider.
        
        Args:
            config: Generation configuration
            
        Raises:
            ValueError: If GROQ_API_KEY not set
        """
        self.config = config or GenerationConfig()
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not set. "
                "Please set it in .env or environment variables"
            )
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            model=self.config.model_name,
            api_key=self.api_key,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        
        logger.info(f"✅ LLM Provider initialized: {self.config.model_name}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a professional LinkedIn content creator.",
        temperature: Optional[float] = None
    ) -> LLMResult:
        """Generate content using LLM.
        
        Args:
            prompt: User prompt/content to generate from
            system_prompt: System context
            temperature: Override default temperature
            
        Returns:
            LLMResult with generated content
        """
        try:
            # Prepare messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt),
            ]
            
            # Call LLM
            response = self.llm.invoke(messages)
            
            # Extract content and token count
            content = response.content
            tokens_used = self._estimate_tokens(prompt + content)
            
            logger.info(f"✅ Generation successful ({tokens_used} tokens)")
            
            return LLMResult(
                content=content,
                tokens_used=tokens_used,
                success=True,
                error_message=""
            )
            
        except Exception as e:
            error_msg = f"LLM generation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            return LLMResult(
                content="",
                tokens_used=0,
                success=False,
                error_message=error_msg
            )
    
    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)."""
        return max(1, len(text) // 4)
    
    def test_connectivity(self) -> bool:
        """Test if LLM is reachable.
        
        Returns:
            True if LLM is accessible
        """
        try:
            result = self.llm.invoke([
                HumanMessage(content="Test")
            ])
            return bool(result.content)
        except Exception as e:
            logger.error(f"LLM connectivity test failed: {e}")
            return False


# ============================================================================
# SINGLETON PROVIDER INSTANCES
# ============================================================================

# Default provider with standard settings
_default_provider: Optional[LLMProvider] = None

# Deterministic provider with temperature=0 for consistent outputs
_deterministic_provider: Optional[LLMProvider] = None


def get_llm() -> ChatGroq:
    """Get default LLM instance with standard temperature (0.7).
    
    Returns:
        ChatGroq instance configured for creative/varied outputs
    
    Lazy initialization - only creates on first call.
    """
    global _default_provider
    if _default_provider is None:
        config = GenerationConfig()
        _default_provider = LLMProvider(config)
    return _default_provider.llm


def get_llm_deterministic() -> ChatGroq:
    """Get deterministic LLM instance with temperature=0.
    
    Used for quality checking, scoring, and structured outputs
    where consistency is more important than creativity.
    
    Returns:
        ChatGroq instance configured for deterministic outputs
    
    Lazy initialization - only creates on first call.
    """
    global _deterministic_provider
    if _deterministic_provider is None:
        config = GenerationConfig(temperature=0)
        _deterministic_provider = LLMProvider(config)
    return _deterministic_provider.llm
