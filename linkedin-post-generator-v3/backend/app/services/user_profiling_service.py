from typing import List, Dict, Optional
from pydantic import BaseModel
from app.services.llm_service import LLMService


class StyleProfile(BaseModel):
    """User's unique writing style profile."""
    user_id: str
    tone: str = "professional"
    vocabulary: str = "intermediate"
    structure: Dict = {}
    themes: List[str] = []
    personality: str = "thought_leader"
    emoji_usage: bool = True
    storytelling_style: str = "narrative"
    cta_preference: str = "question"
    audience_connection: str = "direct"
    liked_elements: List = []
    improvement_notes: List = []
    performance_history: List = []
    
    @staticmethod
    def default(user_id: str) -> "StyleProfile":
        """Return default profile for new users."""
        return StyleProfile(user_id=user_id)


class UserProfilingService:
    """
    Learns and maintains user writing style profiles.
    Updates based on user feedback and post performance.
    """
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def extract_style_from_posts(
        self,
        user_id: str,
        posts: List[str],
        quality_scores: List[float]
    ) -> StyleProfile:
        """
        Extract writing style from user's past posts.
        Weight by quality scores (weight good posts more).
        """
        
        # Only analyze well-performing posts (score > 70)
        high_quality_posts = [
            post for post, score in zip(posts, quality_scores)
            if score > 70
        ]
        
        if not high_quality_posts:
            return StyleProfile.default(user_id)
        
        # Analyze various style dimensions
        tone = await self._extract_tone(high_quality_posts)
        vocabulary = await self._extract_vocabulary_level(high_quality_posts)
        structure = await self._extract_sentence_structure(high_quality_posts)
        personality = await self._extract_personality(high_quality_posts)
        themes = await self._extract_core_themes(high_quality_posts)
        
        style = StyleProfile(
            user_id=user_id,
            tone=tone,
            vocabulary=vocabulary,
            structure=structure,
            personality=personality,
            themes=themes,
        )
        
        return style
    
    async def _extract_tone(self, posts: List[str]) -> str:
        """Analyze tone from posts using LLM."""
        
        prompt = f"""
        Analyze the tone of these LinkedIn posts and pick ONE:
        professional, casual, humorous, inspirational, educational
        
        Posts:
        {''.join(posts[:3])}
        
        Response format: Just the tone word, nothing else.
        """
        
        response = await self.llm_service.generate(prompt)
        return response.strip().lower()
    
    async def _extract_vocabulary_level(self, posts: List[str]) -> str:
        """Simple vs Complex vocabulary analysis."""
        
        prompt = f"""
        Is the vocabulary in these posts:
        - Simple (everyday words, easy to understand)
        - Intermediate (professional terms, some technical)
        - Advanced (complex, industry-specific, jargon)
        
        Posts:
        {''.join(posts[:2])}
        
        Respond with ONE word: Simple, Intermediate, or Advanced.
        """
        
        response = await self.llm_service.generate(prompt)
        return response.strip()
    
    async def _extract_sentence_structure(self, posts: List[str]) -> Dict:
        """Analyze sentence length, use of questions, exclamations."""
        
        import numpy as np
        
        all_text = " ".join(posts)
        sentences = all_text.split(".")
        
        return {
            "avg_length": np.mean([len(s.split()) for s in sentences]),
            "questions_per_post": all_text.count("?") / len(posts),
            "exclamations_per_post": all_text.count("!") / len(posts),
            "short_sentences_ratio": sum(
                1 for s in sentences if len(s.split()) < 5
            ) / len(sentences),
        }
    
    async def _extract_personality(self, posts: List[str]) -> str:
        """Detect personality archetype."""
        
        prompt = f"""
        Based on these LinkedIn posts, what's the author's personality archetype?
        Choose ONE: thought_leader, storyteller, expert, connector, provocateur, educator
        
        Posts:
        {''.join(posts[:3])}
        
        Respond with just the archetype.
        """
        
        response = await self.llm_service.generate(prompt)
        return response.strip().lower()
    
    async def _extract_core_themes(self, posts: List[str]) -> List[str]:
        """Extract main topics/themes from posts."""
        
        prompt = f"""
        What are the 3-5 main topics or themes in these LinkedIn posts?
        
        Posts:
        {''.join(posts[:3])}
        
        Format: Comma-separated list, nothing else.
        """
        
        response = await self.llm_service.generate(prompt)
        return [t.strip() for t in response.split(",") if t.strip()]
    
    def create_style_injected_prompt(
        self,
        topic: str,
        style: StyleProfile,
        tone_override: Optional[str] = None,
        content_type: str = "general"
    ) -> str:
        """Create a post generation prompt that includes user's unique style."""
        
        tone = tone_override or style.tone
        
        prompt = f"""
        You are writing a LinkedIn post for a {tone} {content_type} professional.
        
        This user's unique writing style:
        - Tone: {style.tone} (speak with {style.tone} authority)
        - Vocabulary level: {style.vocabulary} (use {style.vocabulary} vocabulary)
        - Personality: {style.personality} (adopt {style.personality} perspective)
        - Storytelling: {style.storytelling_style} (tell stories {style.storytelling_style})
        - Audience approach: {style.audience_connection} (connect {style.audience_connection})
        - Emoji preference: {'Use emojis naturally' if style.emoji_usage else 'Avoid emojis'}
        - CTA style: {style.cta_preference} (end with a {style.cta_preference})
        - Core topics: {', '.join(style.themes)}
        - Sentence structure: Keep average sentence length around {style.structure.get('avg_length', 15)} words
        - Include roughly {style.structure.get('questions_per_post', 0.3)} questions per post
        
        Generate a LinkedIn post about: {topic}
        
        Rules:
        1. Write in the user's unique voice (not generic AI)
        2. Match their vocabulary level exactly
        3. Use their storytelling approach
        4. Follow their content themes when relevant
        5. Include their preferred CTA style
        6. Make it authentic to how they actually write
        7. Length: 150-300 words
        8. Include a strong hook in the first line
        9. Add 3-5 relevant hashtags at the end
        
        Post:
        """
        
        return prompt.strip()
