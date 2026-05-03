from sqlalchemy.orm import Session
from app.models.models import Post
from typing import Dict, List, Optional
import re
from collections import Counter

class UserProfileAnalyzer:
    """Analyze user's writing style from past posts."""
    
    @staticmethod
    async def analyze_user_profile(user_id: str, db: Session) -> Dict:
        """
        Complete analysis of user's writing profile.
        Returns 9-dimension profile for personalization.
        """
        
        # Get past posts
        posts = db.query(Post).filter(
            Post.user_id == user_id
        ).order_by(Post.created_at.desc()).limit(10).all()
        
        if not posts:
            return UserProfileAnalyzer._default_profile()
        
        # Combine all text
        all_text = "\n".join([p.content for p in posts])
        
        # Analyze each dimension
        profile = {
            "user_id": user_id,
            "post_count": len(posts),
            
            # 1. TONE
            "tone": UserProfileAnalyzer._analyze_tone(all_text),
            
            # 2. VOCABULARY
            "vocabulary_level": UserProfileAnalyzer._analyze_vocabulary(all_text),
            
            # 3. SENTENCE PATTERNS
            "sentence_patterns": UserProfileAnalyzer._analyze_sentences(all_text),
            
            # 4. CONTENT THEMES
            "content_themes": UserProfileAnalyzer._extract_themes(all_text),
            
            # 5. PERSONALITY ARCHETYPE
            "personality": UserProfileAnalyzer._detect_personality(all_text),
            
            # 6. STORYTELLING STYLE
            "storytelling_style": UserProfileAnalyzer._analyze_storytelling(all_text),
            
            # 7. EMOJI USAGE
            "emoji_usage": UserProfileAnalyzer._analyze_emoji_usage(all_text),
            
            # 8. CTA STYLE
            "cta_style": UserProfileAnalyzer._analyze_cta(all_text),
            
            # 9. AUDIENCE CONNECTION
            "audience_connection": UserProfileAnalyzer._analyze_audience(all_text),
        }
        
        return profile
    
    @staticmethod
    def _analyze_tone(text: str) -> str:
        """Detect primary tone: professional, casual, humorous, inspirational."""
        
        text_lower = text.lower()
        
        # Count tone indicators
        professional_markers = len(re.findall(r'\b(analysis|strategy|insights|solutions|framework)\b', text_lower))
        casual_markers = len(re.findall(r'\b(lol|haha|😂|tbh|ngl|btw)\b|[!]{2,}', text_lower))
        humorous_markers = len(re.findall(r'\b(funny|joke|hilarious|cringe|roast)\b', text_lower))
        inspirational_markers = len(re.findall(r'\b(inspiring|together|amazing|growth|journey|passion)\b', text_lower))
        
        scores = {
            "professional": professional_markers,
            "casual": casual_markers,
            "humorous": humorous_markers,
            "inspirational": inspirational_markers,
        }
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "professional"
    
    @staticmethod
    def _analyze_vocabulary(text: str) -> str:
        """Detect vocabulary level: simple, intermediate, advanced."""
        
        words = text.split()
        
        # Count complex words (>10 chars typically indicate advanced vocab)
        complex_words = sum(1 for w in words if len(w) > 10)
        complex_ratio = complex_words / len(words) if words else 0
        
        # Check for technical terms
        technical_terms = len(re.findall(r'\b(algorithm|machine learning|framework|architecture|paradigm|methodology)\b', text.lower()))
        
        if complex_ratio > 0.3 or technical_terms > 5:
            return "advanced"
        elif complex_ratio > 0.15 or technical_terms > 2:
            return "intermediate"
        else:
            return "simple"
    
    @staticmethod
    def _analyze_sentences(text: str) -> Dict:
        """Analyze sentence structure patterns."""
        
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if not sentences:
            return {"avg_length": 15, "variation": "medium"}
        
        # Average sentence length
        word_counts = [len(s.split()) for s in sentences]
        avg_length = sum(word_counts) / len(word_counts)
        
        # Variation (std dev)
        variance = sum((x - avg_length) ** 2 for x in word_counts) / len(word_counts)
        std_dev = variance ** 0.5
        
        # Classify variation
        if std_dev > 8:
            variation = "high"  # Lots of sentence length variation
        elif std_dev > 4:
            variation = "medium"
        else:
            variation = "low"  # Consistent length
        
        return {
            "avg_length": round(avg_length),
            "variation": variation,
            "min_length": min(word_counts),
            "max_length": max(word_counts),
        }
    
    @staticmethod
    def _extract_themes(text: str) -> List[str]:
        """Extract main content themes/keywords."""
        
        # Simple keyword extraction (can upgrade to NLP)
        theme_keywords = {
            "technology": ["AI", "software", "code", "tech", "app", "data", "algorithm"],
            "business": ["startup", "growth", "revenue", "business", "market", "sales"],
            "leadership": ["team", "leadership", "culture", "people", "management"],
            "learning": ["learn", "education", "course", "skill", "knowledge"],
            "personal_development": ["growth", "mindset", "productivity", "success"],
        }
        
        text_lower = text.lower()
        detected_themes = []
        
        for theme, keywords in theme_keywords.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                detected_themes.append(theme)
        
        return detected_themes[:3] if detected_themes else ["general"]
    
    @staticmethod
    def _detect_personality(text: str) -> str:
        """Detect personality archetype."""
        
        text_lower = text.lower()
        
        # Thought leader
        if any(word in text_lower for word in ["insights", "analysis", "framework", "strategy"]):
            return "thought_leader"
        
        # Storyteller
        if any(word in text_lower for word in ["journey", "experience", "learned", "story"]):
            return "storyteller"
        
        # Expert
        if any(word in text_lower for word in ["tutorial", "how to", "guide", "step"]):
            return "expert"
        
        # Connector
        if any(word in text_lower for word in ["team", "community", "together", "network"]):
            return "connector"
        
        # Provocateur
        if any(word in text_lower for word in ["actually", "wrong", "myth", "controversial"]):
            return "provocateur"
        
        return "balanced"
    
    @staticmethod
    def _analyze_storytelling(text: str) -> str:
        """Analyze storytelling approach: narrative, data-driven, mixed."""
        
        text_lower = text.lower()
        
        # Narrative markers
        narrative = len(re.findall(r'\b(once|then|suddenly|but|however|therefore)\b', text_lower))
        
        # Data markers
        data = len(re.findall(r'\b(data|statistics|showed|found|research|study)\b|[\d]+%', text_lower))
        
        if data > narrative * 2:
            return "data_driven"
        elif narrative > data * 2:
            return "narrative"
        else:
            return "mixed"
    
    @staticmethod
    def _analyze_emoji_usage(text: str) -> Dict:
        """Analyze emoji usage patterns."""
        
        # Count emojis (anything with ord > 127)
        emojis = [char for char in text if ord(char) > 127]
        emoji_count = len(emojis)
        
        if emoji_count == 0:
            return {"usage": "none", "frequency": "never"}
        
        words = text.split()
        emoji_ratio = emoji_count / len(words) if words else 0
        
        if emoji_ratio > 0.05:
            frequency = "frequent"
        elif emoji_ratio > 0.01:
            frequency = "moderate"
        else:
            frequency = "occasional"
        
        return {
            "usage": "yes",
            "frequency": frequency,
            "count": emoji_count,
            "ratio": round(emoji_ratio, 3),
        }
    
    @staticmethod
    def _analyze_cta(text: str) -> str:
        """Analyze call-to-action style."""
        
        text_lower = text.lower()
        
        # Question CTA
        if text.count("?") >= 1:
            return "question"
        
        # Action CTA
        if any(word in text_lower for word in ["click", "share", "comment", "join", "apply"]):
            return "action"
        
        # Statement CTA
        return "statement"
    
    @staticmethod
    def _analyze_audience(text: str) -> str:
        """Analyze audience connection style."""
        
        text_lower = text.lower()
        
        # Direct (you, your)
        direct = text.count(" you") + text.count(" your")
        
        # Inclusive (we, us)
        inclusive = text.count(" we ") + text.count(" us ")
        
        # Formal (formal markers)
        formal = len(re.findall(r'\b(respectfully|kindly|sincerely|regards)\b', text_lower))
        
        if formal > 2:
            return "formal"
        elif inclusive > direct:
            return "inclusive"
        else:
            return "direct"
    
    @staticmethod
    def _default_profile() -> Dict:
        """Default profile for users with no posts."""
        
        return {
            "user_id": "new_user",
            "post_count": 0,
            "tone": "professional",
            "vocabulary_level": "intermediate",
            "sentence_patterns": {
                "avg_length": 15,
                "variation": "medium",
                "min_length": 8,
                "max_length": 25,
            },
            "content_themes": ["general"],
            "personality": "balanced",
            "storytelling_style": "mixed",
            "emoji_usage": {
                "usage": "yes",
                "frequency": "moderate",
            },
            "cta_style": "question",
            "audience_connection": "direct",
        }
