from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Optional
from app.core.config import settings


class LLMService:
    """Service for interacting with LLM providers."""
    
    def __init__(self):
        self.groq = ChatGroq(
            model="llama-3.1-70b-versatile",
            groq_api_key=settings.GROQ_API_KEY
        )
        self.openai = None
        if settings.OPENAI_API_KEY:
            try:
                from langchain_openai import ChatOpenAI
                self.openai = ChatOpenAI(
                    model="gpt-4-turbo",
                    openai_api_key=settings.OPENAI_API_KEY
                )
            except Exception:
                self.openai = None
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_openai: bool = False
    ) -> str:
        """Generate text using LLM."""
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        # Use OpenAI if requested and available, otherwise use Groq
        llm = self.openai if (use_openai and self.openai) else self.groq
        
        response = await llm.ainvoke(messages)
        return response.content
    
    async def generate_multiple(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None
    ) -> List[str]:
        """Generate multiple texts in parallel."""
        from asyncio import gather
        
        tasks = [self.generate(prompt, system_prompt) for prompt in prompts]
        return await gather(*tasks)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get text embedding using OpenAI."""
        if not self.openai:
            raise ValueError("OpenAI not configured")
        
        # Use OpenAI embeddings
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        
        return response.data[0].embedding
