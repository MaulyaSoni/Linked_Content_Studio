"""
Data Models - Type-Safe Structures
==================================
Complete data models for the LinkedIn content generator.
All dataclasses are immutable and validated.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


# ============================================================================
# ENUMERATIONS - STRONGLY TYPED CHOICES
# ============================================================================

class GenerationMode(Enum):
    """Mode of generation - determines flow and quality."""
    SIMPLE = "simple"          # Direct LLM (1-3s) - for quick posts
    ADVANCED = "advanced"      # RAG-enhanced (8-15s) - for deep context


class ContentType(Enum):
    """LinkedIn post style/format."""
    BUILD_IN_PUBLIC = "build_in_public"
    EDUCATIONAL = "educational"
    HOT_TAKE = "hot_take"
    FOUNDER_LESSON = "founder_lesson"
    GITHUB_SHOWCASE = "github_showcase"
    AI_INSIGHTS = "ai_insights"
    LEARNING_SHARE = "learning_share"


class Tone(Enum):
    """Emotional tone of the post."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    THOUGHTFUL = "thoughtful"
    BOLD = "bold"
    CONVERSATIONAL = "conversational"


class Audience(Enum):
    """Who the post is for."""
    FOUNDERS = "founders"
    DEVELOPERS = "developers"
    PROFESSIONALS = "professionals"
    ENTREPRENEURS = "entrepreneurs"
    TECH_LEADERS = "tech_leaders"
    GENERAL = "general"


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

@dataclass
class PostRequest:
    """Request to generate a LinkedIn post.
    
    This is the primary input contract - everything the generator needs.
    Validates on construction to fail fast.
    """
    
    # ---- CORE INPUTS (at least one required) ----
    content_type: ContentType  # What type of post?
    topic: str = ""            # Topic for SIMPLE mode
    github_url: str = ""       # GitHub repo for ADVANCED mode
    text_input: str = ""       # Custom text for ADVANCED mode
    
    # ---- GENERATION MODE ----
    mode: GenerationMode = GenerationMode.SIMPLE
    
    # ---- STYLE PARAMETERS ----
    tone: Tone = Tone.PROFESSIONAL
    audience: Audience = Audience.PROFESSIONALS
    
    # ---- GENERATION OPTIONS ----
    include_hashtags: bool = True
    include_caption: bool = False
    max_length: int = 3000
    
    # ---- METADATA ----
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate request after initialization."""
        # At least one input required
        if not any([self.topic, self.github_url, self.text_input]):
            raise ValueError(
                "Must provide topic, GitHub URL, or text input"
            )
        
        # Validate GitHub URL if provided
        if self.github_url and not self._is_valid_github_url(self.github_url):
            raise ValueError(
                f"Invalid GitHub URL: {self.github_url}"
            )
    
    @staticmethod
    def _is_valid_github_url(url: str) -> bool:
        """Validate GitHub URL format."""
        patterns = [
            r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'^([^/]+)/([^/]+)/?$'  # username/repo format
        ]
        return any(re.search(pattern, url) for pattern in patterns)


@dataclass
class PostResponse:
    """Response from post generation.
    
    Contains the generated content and metadata about generation.
    Guaranteed to be populated even on partial success.
    """
    
    # ---- GENERATION RESULTS ----
    success: bool                              # Did generation succeed?
    post: str = ""                             # Main post content
    hashtags: str = ""                         # Generated hashtags
    caption: str = ""                          # Image caption (optional)
    
    # ---- CONTEXT & METADATA ----
    mode_used: str = "simple"                 # What mode was used?
    context_sources: List[str] = field(
        default_factory=list
    )                                          # What sources were used?
    
    # ---- QUALITY INDICATORS ----
    estimated_engagement: str = "medium"      # low/medium/high
    hook_strength: str = "good"                # weak/good/strong
    context_quality: float = 0.0               # 0-1 score
    hook_options: Dict[str, str] = field(
        default_factory=dict
    )                                          # Generated hook options: {style: hook_text}
    quality_score: Dict[str, Any] = field(
        default_factory=dict
    )                                          # Quality metrics: {dimension: score}
    
    # ---- PERFORMANCE METRICS ----
    generation_time: float = 0.0               # Seconds taken
    tokens_used: int = 0                       # LLM tokens
    
    # ---- ERROR HANDLING ----
    error_message: str = ""                    # Error description
    warnings: List[str] = field(default_factory=list)
    
    # ---- METADATA ----
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RepoContext:
    """Context loaded from a GitHub repository."""
    name: str                                    # Repository name (owner/repo)
    description: str = ""                        # Repository description
    readme_content: str = ""                     # README content
    readme_found: bool = False                   # Was README found?
    sources_used: List[str] = field(default_factory=list)  # Sources loaded
    quality_score: float = 0.0                   # 0-1 quality rating
    completeness: str = "minimal"                # complete, partial, or minimal
    fallback_used: bool = False                  # Was fallback used?
    transparency_message: str = ""               # User-facing message
    language: str = ""                           # Primary language
    stars: int = 0                               # Star count
    file_structure: List[str] = field(default_factory=list)  # File list
    topics: Optional[List[str]] = None           # Repository topics
    dependencies: Optional[List[str]] = None     # Dependencies
    recent_commits: Optional[List[str]] = None   # Recent commits


@dataclass
class RAGContext:
    """Context retrieved from RAG system."""
    content: str                    # The actual context text
    sources_used: List[str]        # Files/sections used
    quality_score: float           # 0-1 quality rating
    repo_context: Optional[Dict[str, Any]] = None


@dataclass
class LLMResult:
    """Result from LLM generation."""
    content: str                   # Generated text
    tokens_used: int = 0          # Tokens consumed
    success: bool = True          # Was it successful?
    error_message: str = ""       # Error if failed


# ============================================================================
# CONFIGURATION MODELS
# ============================================================================

@dataclass
class GenerationConfig:
    """Configuration for generation engine."""
    
    # LLM Settings
    model_name: str = "llama-3.1-8b-instant"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # RAG Settings
    chunk_size: int = 500
    chunk_overlap: int = 100
    max_context_length: int = 4000
    
    # Performance
    timeout_seconds: int = 30
    retry_attempts: int = 3
    
    # Quality
    enable_safety_check: bool = True
    enable_refinement: bool = False


# ============================================================================
# HELPER FUNCTIONS - FOR CONVENIENCE
# ============================================================================

def get_content_types() -> Dict[str, str]:
    """Get human-readable content type names."""
    return {
        ContentType.BUILD_IN_PUBLIC.value: "🚀 Build in Public",
        ContentType.EDUCATIONAL.value: "📚 Educational Breakdown",
        ContentType.HOT_TAKE.value: "🔥 Hot Take",
        ContentType.FOUNDER_LESSON.value: "💡 Founder Lesson",
        ContentType.GITHUB_SHOWCASE.value: "⚡ GitHub Showcase",
        ContentType.AI_INSIGHTS.value: "🤖 AI Insights",
        ContentType.LEARNING_SHARE.value: "📖 Learning Share",
    }


def get_tones() -> Dict[str, str]:
    """Get human-readable tone names."""
    return {
        Tone.PROFESSIONAL.value: "👔 Professional",
        Tone.CASUAL.value: "😊 Casual & Friendly",
        Tone.ENTHUSIASTIC.value: "🚀 Enthusiastic",
        Tone.THOUGHTFUL.value: "🤔 Thoughtful",
        Tone.BOLD.value: "💪 Bold & Direct",
        Tone.CONVERSATIONAL.value: "💬 Conversational",
    }


def get_audiences() -> Dict[str, str]:
    """Get human-readable audience names."""
    return {
        Audience.FOUNDERS.value: "🚀 Founders & Entrepreneurs",
        Audience.DEVELOPERS.value: "💻 Developers",
        Audience.PROFESSIONALS.value: "👔 Professionals",
        Audience.ENTREPRENEURS.value: "💡 Entrepreneurs",
        Audience.TECH_LEADERS.value: "⚡ Tech Leaders",
        Audience.GENERAL.value: "🌍 General Audience",
    }


# ============================================================================
# HACKATHON-SPECIFIC ENUMS
# ============================================================================

class HackathonAchievement(Enum):
    """Achievement levels for hackathons"""
    PARTICIPANT = "participant"
    TOP_10 = "top_10"
    TOP_5 = "top_5"
    RUNNER_UP = "runner_up"
    WINNER = "winner"
    SPECIAL_MENTION = "special_mention"


class HackathonType(Enum):
    """Types of hackathons"""
    AI_ML = "ai_ml"
    WEB_DEV = "web_dev"
    MOBILE = "mobile"
    SUSTAINABILITY = "sustainability"
    HEALTHCARE = "healthcare"
    FINTECH = "fintech"
    DATASCIENCE = "datascience"
    GENERAL = "general"


# ============================================================================
# HACKATHON REQUEST & RESPONSE
# ============================================================================

@dataclass
class HackathonProjectRequest:
    """Request data for hackathon/competition post generation"""
    
    # ---- HACKATHON BASICS ----
    hackathon_name: str                        # e.g., "Odoo X Adani Hackathon"
    project_name: str                          # e.g., "WaterFlow"
    hackathon_type: HackathonType = HackathonType.GENERAL
    
    # ---- TEAM INFO ----
    team_size: int = 4                         # Number of team members (1-10)
    team_members: List[str] = field(default_factory=list)  # Names of members
    your_role: str = "Developer"               # Your role in the team
    
    # ---- PROJECT DETAILS ----
    problem_statement: str = ""                # What problem does it solve?
    solution_description: str = ""             # How does your solution work?
    tech_stack: List[str] = field(default_factory=list)  # ["React", "Node.js", etc]
    key_features: List[str] = field(default_factory=list)  # Features of the project
    
    # ---- RESULTS & ACHIEVEMENT ----
    achievement: HackathonAchievement = HackathonAchievement.PARTICIPANT
    completion_time_hours: int = 24            # 24, 36, or 48 hours
    results_metrics: str = ""                  # e.g., "Built MVP in 24 hours"
    
    # ---- EMOTIONAL ELEMENTS ----
    personal_journey: str = ""                 # "Finally, after years..."
    key_learnings: List[str] = field(default_factory=list)  # What you learned
    growth_moment: str = ""                    # Key realization from experience
    
    # ---- GENERATION SETTINGS ----
    tone: str = "thoughtful"                   # thoughtful, enthusiastic, bold, casual
    audience: str = "developers"               # developers, founders, professionals
    max_length: int = 3000
    
    def validate(self):
        """Validate request"""
        if not self.hackathon_name:
            raise ValueError("Hackathon name is required")
        if not self.project_name:
            raise ValueError("Project name is required")
        if self.team_size < 1 or self.team_size > 10:
            raise ValueError("Team size must be between 1 and 10")
        if not self.problem_statement:
            raise ValueError("Problem statement is required")


@dataclass
class HackathonPostResponse(PostResponse):
    """Response for hackathon post generation"""
    
    # All fields from PostResponse, plus:
    achievement_level: str = "participant"     # Winner, Top 5, etc
    estimated_reach: str = "medium"            # low, medium, high
    project_showcase: str = ""                 # The technical section
    team_story: str = ""                       # The team collaboration section
    impact_statement: str = ""                 # The "what's next" section
