"""
LLM Provider - Clean LLM Interface
=================================
Wraps Groq/OpenAI with fallback handling and clean abstraction.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time
from dotenv import load_dotenv
from .models import LLMResult, GenerationConfig

load_dotenv()
class LLMProvider:
    """
    Clean LLM interface with automatic fallback handling.
    
    Supports:
    - Groq (primary, fast and free)
    - OpenAI (fallback, reliable)
    - Future providers can be easily added
    """
    
    def __init__(self, config: Optional[GenerationConfig] = None):
        """Initialize LLM provider with configuration."""
        self.config = config or GenerationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Check for Groq API key first
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self.logger.info("Found GROQ_API_KEY, initializing primary provider...")
        else:
            self.logger.warning("GROQ_API_KEY not found - will attempt OpenAI fallback")
        
        # Initialize providers (Groq primary, OpenAI fallback)
        self.groq_client = self._init_groq()
        self.openai_client = self._init_openai() if not groq_key else None
        
        # Track provider health
        self.groq_available = bool(self.groq_client)
        self.openai_available = bool(self.openai_client)
        
        if self.groq_available:
            self.logger.info("✅ Groq provider ready - fast generation enabled!")
        elif self.openai_available:
            self.logger.info("⚠️ Using OpenAI fallback - Groq unavailable")
        else:
            self.logger.error("❌ No LLM providers available - please set GROQ_API_KEY")
    
    def _init_groq(self):
        """Initialize Groq client if API key available."""
        try:
            GROQ_API_KEY = os.getenv("GROQ_API_KEY")
            if not GROQ_API_KEY:
                self.logger.warning("GROQ_API_KEY not found")
                return None
            
            # Try importing with timeout protection
            self.logger.info("🔄 Importing Groq (this may take a moment on first run)...")
            
            try:
                # Use threading to timeout the import if it hangs
                import threading
                import_result = [None]
                import_error = [None]
                
                def try_import():
                    try:
                        from langchain_groq import ChatGroq
                        import_result[0] = ChatGroq
                    except Exception as e:
                        import_error[0] = e
                
                # Try import with 30 second timeout
                import_thread = threading.Thread(target=try_import)
                import_thread.daemon = True
                import_thread.start()
                import_thread.join(timeout=30.0)
                
                if import_thread.is_alive():
                    self.logger.error("❌ Groq import timed out (dependencies may be loading)")
                    self.logger.warning("⚠️ Running without LLM - demo mode will be used")
                    return None
                
                if import_error[0]:
                    raise import_error[0]
                
                if import_result[0] is None:
                    self.logger.error("❌ Groq import failed unexpectedly")
                    return None
                
                ChatGroq = import_result[0]
                self.logger.info("✅ Groq import successful")
                
            except Exception as import_error:
                self.logger.error(f"❌ Failed to import Groq: {import_error}")
                self.logger.error("This may be due to PyTorch/Transformers dependencies")
                self.logger.warning("⚠️ Running without LLM - demo mode will be used")
                return None
            
            # Initialize Groq client
            groq_client = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            self.logger.info("✅ Groq client created successfully")
            return groq_client
            
        except ImportError:
            self.logger.warning("langchain_groq not available")
            return None
        except Exception as e:
            self.logger.warning(f"Failed to initialize Groq: {e}")
            return None
    
    def _init_openai(self):
        """Initialize OpenAI client if API key available."""
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                self.logger.warning("OPENAI_API_KEY not found")
                return None
            
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=openai_api_key,
                model="gpt-4o-mini",  # Cost-effective model
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
        except ImportError:
            self.logger.warning("langchain_openai not available")
            return None
        except Exception as e:
            self.logger.warning(f"Failed to initialize OpenAI: {e}")
            return None
    
    def generate(self, prompt: str, prefer_groq: bool = True) -> LLMResult:
        """
        Generate content using the best available provider.
        
        Args:
            prompt: Input prompt for generation
            prefer_groq: Whether to try Groq first (faster + free)
        
        Returns:
            LLMResult with generated content and metadata
        """
        start_time = time.time()
        
        # Determine provider order (Groq prioritized)
        if self.groq_available:
            providers = [("groq", self.groq_client)]
            if self.openai_available and not prefer_groq:
                providers.append(("openai", self.openai_client))
        elif self.openai_available:
            providers = [("openai", self.openai_client)]
        else:
            return LLMResult(
                content="",
                success=False,
                error_message="❌ No valid API key found. Please add GROQ_API_KEY to your .env file for fast, free generation!"
            )
        
        # Try providers in order
        for provider_name, client in providers:
            if not client:
                continue
                
            try:
                result = self._generate_with_provider(client, prompt, provider_name)
                if result.success:
                    generation_time = time.time() - start_time
                    self.logger.info(f"Generated with {provider_name} in {generation_time:.2f}s")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"{provider_name} generation failed: {e}")
                continue
        
        # All providers failed
        return LLMResult(
            content="",
            success=False,
            error_message="All LLM providers failed. Please check your API keys and network connection."
        )
    
    def _generate_with_provider(self, client, prompt: str, provider_name: str) -> LLMResult:
        """Generate content with specific provider."""
        
        # Add timeout handling (Windows compatible)
        import platform
        
        # Track if we're using signal for cleanup
        using_signal = False
        signal_module = None
        
        try:
            # Format prompt for chat models
            messages = [{"role": "user", "content": prompt}]
            
            # Generate with provider (no signal timeout on Windows)
            if platform.system() == "Windows":
                # Windows doesn't support SIGALRM, so we skip timeout handling
                response = client.invoke(messages)
            else:
                # Unix systems can use signal timeout
                import signal as signal_module
                using_signal = True
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Generation timed out")
                
                signal_module.signal(signal_module.SIGALRM, timeout_handler)
                signal_module.alarm(self.config.timeout_seconds)
                response = client.invoke(messages)
                signal_module.alarm(0)  # Cancel alarm
            
            # Extract content based on provider type
            if hasattr(response, 'content'):
                content = response.content
            elif hasattr(response, 'text'):
                content = response.text
            else:
                content = str(response)
            
            # Estimate token usage (rough approximation)
            tokens_used = len(prompt.split()) + len(content.split())
            
            return LLMResult(
                content=content,
                tokens_used=tokens_used,
                model_used=provider_name,
                success=True
            )
            
        except TimeoutError:
            return LLMResult(
                content="",
                success=False,
                error_message="Generation timed out"
            )
        except Exception as e:
            return LLMResult(
                content="",
                success=False,
                error_message=str(e)
            )
        finally:
            # Only cancel alarm if we're on Unix and using signal
            if using_signal and signal_module:
                signal_module.alarm(0)
    
    def test_connectivity(self) -> Dict[str, bool]:
        """Test connectivity to all providers."""
        results = {}
        
        test_prompt = "Say 'Hello' in one word."
        
        # Test Groq
        if self.groq_client:
            try:
                result = self._generate_with_provider(self.groq_client, test_prompt, "groq")
                results["groq"] = result.success
            except Exception:
                results["groq"] = False
        else:
            results["groq"] = False
        
        # Test OpenAI  
        if self.openai_client:
            try:
                result = self._generate_with_provider(self.openai_client, test_prompt, "openai")
                results["openai"] = result.success
            except Exception:
                results["openai"] = False
        else:
            results["openai"] = False
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status information."""
        return {
            "providers_available": {
                "groq": self.groq_available,
                "openai": self.openai_available
            },
            "config": {
                "model": self.config.model_name,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "timeout": self.config.timeout_seconds
            },
            "health_check": self.test_connectivity()
        }


class FallbackLLM:
    """
    Simplified fallback LLM for when main providers fail.
    Uses basic text generation patterns.
    """
    
    FALLBACK_TEMPLATES = {
        "linkedin_post": """
        Here's a professional LinkedIn post about {topic}:

        🚀 Exciting development in {topic}!

        I've been exploring {topic} and here are my key takeaways:

        ✅ It's transforming how we work
        ✅ Creates new opportunities 
        ✅ Worth learning more about

        What's your experience with {topic}?

        #technology #innovation #learning
        """,
        
        "github_post": """
        🔧 Just discovered an interesting GitHub project!

        {repo_name} caught my attention because:

        → Solves a real problem
        → Clean codebase
        → Active community

        Worth checking out for developers working on similar challenges.

        What's the most useful GitHub project you've found recently?

        #opensource #development #coding
        """
    }
    
    @classmethod
    def generate_fallback(cls, content_type: str = "linkedin_post", **kwargs) -> str:
        """Generate fallback content when LLM providers fail."""
        
        template = cls.FALLBACK_TEMPLATES.get(content_type, cls.FALLBACK_TEMPLATES["linkedin_post"])
        
        try:
            return template.format(**kwargs)
        except KeyError:
            # If template variables missing, return basic template
            return cls.FALLBACK_TEMPLATES["linkedin_post"].format(topic="technology")


# Factory functions
def create_llm_provider(config: Optional[Dict[str, Any]] = None) -> LLMProvider:
    """Factory function to create LLM provider."""
    if config:
        gen_config = GenerationConfig(**config)
    else:
        gen_config = GenerationConfig()
    
    return LLMProvider(gen_config)


def test_llm_setup() -> bool:
    """Quick test to verify LLM setup is working."""
    provider = create_llm_provider()
    
    if not provider.groq_available and not provider.openai_available:
        print("❌ No LLM providers available")
        print("Please set GROQ_API_KEY or OPENAI_API_KEY in your .env file")
        return False
    
    # Test generation
    result = provider.generate("Say hello in 3 words")
    
    if result.success:
        print(f"✅ LLM setup working! Generated: {result.content[:50]}...")
        return True
    else:
        print(f"❌ LLM test failed: {result.error_message}")
        return False


if __name__ == "__main__":
    # Quick test when run directly
    test_llm_setup()