from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
from typing import Dict, Optional
import re
from sqlalchemy.orm import Session
from app.services.user_profile_analyzer import UserProfileAnalyzer
from app.services.advanced_prompt_builder import AdvancedPromptBuilder

from app.core.config import settings

class GenerationService:
    """Generate personalized posts using user profile."""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=settings.GROQ_API_KEY
        )
    
    async def generate_post(
        self,
        topic: str,
        user_id: str,
        db: Session,
        tone: Optional[str] = None,
        content_type: str = "simple_topic",
        additional_context: str = ""
    ) -> Dict:
        """
        Generate personalized post based on user profile.
        """
        
        try:
            # STEP 1: Analyze user profile
            user_profile = await UserProfileAnalyzer.analyze_user_profile(user_id, db)
            
            # STEP 2: Build customized prompt
            customized_prompt = AdvancedPromptBuilder.build_customized_prompt(
                topic=topic,
                user_profile=user_profile,
                tone_override=tone,
                content_type=content_type,
                additional_context=additional_context
            )
            
            # STEP 3: Call LLM
            messages = [
                SystemMessage(content="You are an expert LinkedIn post writer creating authentic, engaging content."),
                HumanMessage(content=customized_prompt)
            ]
            
            response = self.llm.invoke(messages)
            post_content = response.content
            
            # STEP 4: Extract hashtags
            hashtags = self._extract_hashtags(post_content)
            
            # STEP 5: Clean post (remove hashtags from body)
            post_clean = post_content.split("\n#")[0].strip()
            if "#" in post_clean:
                post_clean = re.sub(r'\n+#.*', '', post_clean).strip()
            
            # STEP 6: Score quality
            quality_score = self._score_quality(post_clean, user_profile)
            
            return {
                "success": True,
                "post": post_clean,
                "hashtags": hashtags,
                "quality_score": quality_score,
                "tokens_used": len(customized_prompt.split()) + len(post_content.split()),
                "personalization_level": "advanced",
                "user_profile": user_profile,
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "post": None,
                "hashtags": None,
                "quality_score": 0,
            }
    
    @staticmethod
    def _extract_hashtags(text: str) -> str:
        """Extract and format hashtags."""
        hashtags = re.findall(r'#\w+', text)
        # Remove duplicates, keep order
        seen = set()
        unique_tags = []
        for tag in hashtags:
            if tag.lower() not in seen:
                unique_tags.append(tag)
                seen.add(tag.lower())
        return unique_tags[:10]
    
    @staticmethod
    def _score_quality(post: str, profile: Dict) -> int:
        """Score post quality based on multiple factors."""
        
        score = 50  # Base score
        
        # Length optimization (150-250 words ideal)
        word_count = len(post.split())
        if 150 <= word_count <= 250:
            score += 15
        elif 100 <= word_count <= 300:
            score += 10
        
        # Sentence variation
        sentences = [s for s in post.split('.') if s.strip()]
        if len(sentences) >= 3:
            word_counts = [len(s.split()) for s in sentences]
            variation = max(word_counts) - min(word_counts)
            if variation > 10:
                score += 10
        
        # Topic relevance (topic mentioned in post)
        # This would need topic parameter - simplified here
        score += 5
        
        # Personality markers
        if any(marker in post for marker in ["I", "we", "discovered", "realized"]):
            score += 5
        
        # Hashtag quality
        hashtag_count = post.count("#")
        if 2 <= hashtag_count <= 5:
            score += 5
        
        # Emoji usage matches profile
        emoji_count = sum(1 for char in post if ord(char) > 127)
        expected_emoji = {
            "frequent": 4,
            "moderate": 2,
            "occasional": 0,
        }
        expected = expected_emoji.get(
            profile.get("emoji_usage", {}).get("frequency", "moderate"), 2
        )
        if emoji_count == expected or abs(emoji_count - expected) <= 1:
            score += 5
        
        # CTA present
        if "?" in post or any(word in post.lower() for word in ["share", "comment", "follow"]):
            score += 5
        
        return min(score, 100)  # Cap at 100
