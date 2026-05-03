from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Post, User

class UserContextService:
    """Service for loading and managing user context to improve post generation."""

    def __init__(self, db: Session):
        self.db = db

    async def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """
        Load user's past posts, brand profile, and style preferences.
        Returns an enriched context dictionary.
        """
        # Fetch up to 10 most recent posts by the user
        past_posts = self.db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).limit(10).all()
        
        # In the future: Add user preferences from related models (Tone, Industry, etc.)
        user = self.db.query(User).filter(User.id == user_id).first()
        
        # 1. TONE DETECTION
        # Analyze existing posts or fallback to a default
        tones = [p.tone for p in past_posts if p.tone]
        preferred_tone = max(set(tones), key=tones.count) if tones else "Professional and insightful"

        # 2. SENTENCE PATTERN
        # Simple extraction of average length or pattern representation
        # Mock logic to represent sentence pattern extraction
        content_lengths = [len(p.content.split()) for p in past_posts if p.content]
        avg_word_count = sum(content_lengths) / len(content_lengths) if content_lengths else 150

        # 3. CONTENT THEMES
        # Extract keywords/topics frequently used by the user
        topics = [p.topic for p in past_posts if p.topic]
        common_topics = list(set(topics))[:3] if topics else ["Technology", "Leadership", "Innovation"]

        return {
            "first_name": user.username if user else "Professional",
            "preferred_tone": preferred_tone,
            "average_word_count": avg_word_count,
            "recent_topics": common_topics,
            "past_posts_sample": [p.content[:200] + "..." for p.content in past_posts[:3]] if past_posts else []
        }
