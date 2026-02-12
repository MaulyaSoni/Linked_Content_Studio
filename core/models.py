"""
Data Models - Clean Type Definitions
===================================
All data structures for the LinkedIn content generator.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class GenerationMode(Enum):
    """Generation modes for the LinkedIn generator."""
    SIMPLE = "simple"      # Direct LLM prompting (fast)
    ADVANCED = "advanced"  # RAG-enhanced (higher quality)


class ContentType(Enum):
    """Content types for different LinkedIn post styles."""
    BUILD_IN_PUBLIC = "build_in_public"
    EDUCATIONAL = "educational"
    HOT_TAKE = "hot_take" 
    FOUNDER_LESSON = "founder_lesson"
    GITHUB_SHOWCASE = "github_showcase"
    AI_INSIGHTS = "ai_insights"
    LEARNING_SHARE = "learning_share"


class Tone(Enum):
    """Available tones for post generation."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    THOUGHTFUL = "thoughtful"
    BOLD = "bold"
    CONVERSATIONAL = "conversational"


class Audience(Enum):
    """Target audiences for LinkedIn posts."""
    FOUNDERS = "founders"
    DEVELOPERS = "developers" 
    PROFESSIONALS = "professionals"
    ENTREPRENEURS = "entrepreneurs"
    TECH_LEADERS = "tech_leaders"
    GENERAL = "general"


@dataclass
class PostRequest:
    """Request model for post generation."""
    
    # Core input
    content_type: ContentType
    topic: str = ""
    github_url: str = ""
    text_input: str = ""
    
    # Generation settings
    mode: GenerationMode = GenerationMode.SIMPLE
    
    # Style parameters
    tone: Tone = Tone.PROFESSIONAL
    audience: Audience = Audience.PROFESSIONALS
    
    # Generation options
    include_hashtags: bool = True
    include_caption: bool = False
    max_length: int = 3000
    
    # Customization
    personal_voice: str = ""  # Future: user's brand voice
    cta_type: str = "question"  # question, comment, share, none
    
    # Metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate request after initialization."""
        if not self.topic and not self.github_url and not self.text_input:
            raise ValueError("Must provide topic, GitHub URL, or text input")
        
        if self.github_url and not self._is_valid_github_url(self.github_url):
            raise ValueError("Invalid GitHub URL format")
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Validate GitHub URL format."""
        import re
        patterns = [
            r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$',
            r'^([^/]+)/([^/]+)$'
        ]
        return any(re.search(pattern, url) for pattern in patterns)


@dataclass
class RepoContext:
    """Context extracted from GitHub repository."""
    
    # Repository info
    name: str
    description: str = ""
    language: str = ""
    stars: int = 0
    topics: List[str] = field(default_factory=list)
    
    # Content sources
    readme_content: str = ""
    file_structure: List[str] = field(default_factory=list)
    recent_commits: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Quality metrics
    sources_used: List[str] = field(default_factory=list)
    quality_score: float = 0.0  # 0-1 scale
    completeness: str = "unknown"  # unknown, partial, complete
    
    # Transparency
    readme_found: bool = False
    fallback_used: bool = False
    transparency_message: str = ""


@dataclass
class RAGContext:
    """Context retrieved by RAG engine."""
    content: str
    sources_used: List[str]
    quality_score: float
    repo_context: Optional[RepoContext] = None


@dataclass
class PostResponse:
    """Response model for generated posts."""
    
    # Generation results
    success: bool
    post: str = ""
    hashtags: str = ""
    caption: str = ""
    
    # Context information
    context_sources: List[str] = field(default_factory=list)
    mode_used: str = "simple"
    context_quality: float = 0.0
    
    # Performance metrics
    tokens_used: int = 0
    generation_time: float = 0.0
    
    # Quality indicators
    estimated_engagement: str = "medium"  # low, medium, high
    hook_strength: str = "good"  # weak, good, strong
    
    # Error handling
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    stats: Optional[Any] = None  # GenerationStats object
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LLMResult:
    """Result from LLM generation."""
    content: str
    tokens_used: int = 0
    model_used: str = ""
    success: bool = True
    error_message: str = ""


@dataclass
class UserProfile:
    """User profile for personalized generation (future feature)."""
    
    user_id: str
    brand_voice: str = ""
    preferred_tone: Tone = Tone.PROFESSIONAL
    target_audience: Audience = Audience.PROFESSIONALS
    
    # Analytics
    best_performing_hooks: List[str] = field(default_factory=list)
    preferred_content_types: List[ContentType] = field(default_factory=list)
    
    # Settings
    always_include_hashtags: bool = True
    max_post_length: int = 2000
    preferred_cta_style: str = "question"


@dataclass 
class GenerationConfig:
    """Configuration for generation engine."""
    
    # Model settings
    model_name: str = "llama-3.1-8b-instant"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # RAG settings
    chunk_size: int = 500
    chunk_overlap: int = 100
    max_context_length: int = 4000
    
    # Quality settings
    enable_refinement: bool = True
    enable_safety_check: bool = True
    
    # Performance settings
    timeout_seconds: int = 30
    retry_attempts: int = 3


# Type aliases for cleaner code
PostData = Dict[str, Any]  # Legacy compatibility
ContentTypes = Dict[str, str]  # UI content type mapping


# Helper functions
def create_post_request(
    content_type: str,
    topic: str = "",
    github_url: str = "",
    text_input: str = "",
    **kwargs
) -> PostRequest:
    """Helper to create PostRequest from string inputs."""
    
    # Convert string content_type to enum
    content_type_enum = ContentType(content_type)
    
    # Convert other string enums if provided
    tone = Tone(kwargs.get('tone', 'professional'))
    audience = Audience(kwargs.get('audience', 'professionals'))
    
    return PostRequest(
        content_type=content_type_enum,
        topic=topic,
        github_url=github_url,
        text_input=text_input,
        tone=tone,
        audience=audience,
        **{k: v for k, v in kwargs.items() if k not in ['tone', 'audience']}
    )


def get_content_type_display_names() -> Dict[str, str]:
    """Get user-friendly names for content types."""
    return {
        ContentType.BUILD_IN_PUBLIC.value: "🚀 Build in Public",
        ContentType.EDUCATIONAL.value: "📚 Educational Breakdown", 
        ContentType.HOT_TAKE.value: "🔥 Hot Take",
        ContentType.FOUNDER_LESSON.value: "💡 Founder Lesson",
        ContentType.GITHUB_SHOWCASE.value: "⚡ GitHub Project Showcase",
        ContentType.AI_INSIGHTS.value: "🤖 AI Insights",
        ContentType.LEARNING_SHARE.value: "📖 Learning Share"
    }


def get_tone_display_names() -> Dict[str, str]:
    """Get user-friendly names for tones."""
    return {
        Tone.PROFESSIONAL.value: "👔 Professional",
        Tone.CASUAL.value: "😊 Casual & Friendly",
        Tone.ENTHUSIASTIC.value: "🚀 Enthusiastic",
        Tone.THOUGHTFUL.value: "🤔 Thoughtful",
        Tone.BOLD.value: "💪 Bold & Direct", 
        Tone.CONVERSATIONAL.value: "💬 Conversational"
    }


def get_audience_display_names() -> Dict[str, str]:
    """Get user-friendly names for audiences."""
    return {
        Audience.FOUNDERS.value: "🚀 Founders & Entrepreneurs",
        Audience.DEVELOPERS.value: "💻 Developers & Engineers",
        Audience.PROFESSIONALS.value: "👔 Business Professionals",
        Audience.ENTREPRENEURS.value: "💡 Entrepreneurs", 
        Audience.TECH_LEADERS.value: "⚡ Tech Leaders",
        Audience.GENERAL.value: "🌍 General Audience"
    }