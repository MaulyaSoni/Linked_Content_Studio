"""
Trend Analyzer Tool
===================
Identifies trending topics, relevant hashtags, and market opportunities
for LinkedIn content based on topic keywords.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class TrendAnalysisResult:
    """Result from trend analysis."""
    success: bool
    topic: str = ""
    trending_hashtags: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    content_opportunities: List[str] = field(default_factory=list)
    audience_interests: List[str] = field(default_factory=list)
    recommended_tone: str = "professional"
    best_content_type: str = "educational"
    trend_score: float = 0.5
    error_message: str = ""


# ---------------------------------------------------------------------------
# Curated evergreen hashtag map (supplemented by LLM when available)
# ---------------------------------------------------------------------------
HASHTAG_MAP: Dict[str, List[str]] = {
    "ai": ["#AI", "#ArtificialIntelligence", "#MachineLearning", "#DeepLearning", "#GenAI"],
    "machine learning": ["#MachineLearning", "#ML", "#DataScience", "#AI", "#DeepLearning"],
    "startup": ["#Startup", "#Entrepreneurship", "#Founder", "#Building", "#TechStartup"],
    "python": ["#Python", "#Programming", "#Coding", "#SoftwareDevelopment", "#Developer"],
    "cloud": ["#Cloud", "#AWS", "#Azure", "#GCP", "#CloudComputing", "#DevOps"],
    "web": ["#WebDev", "#Frontend", "#FullStack", "#JavaScript", "#React"],
    "data": ["#DataScience", "#Analytics", "#BigData", "#DataEngineering", "#SQL"],
    "career": ["#CareerGrowth", "#JobSearch", "#ProfessionalDevelopment", "#LinkedIn"],
    "leadership": ["#Leadership", "#Management", "#CXO", "#ExecutiveCoach"],
    "product": ["#ProductManagement", "#ProductDesign", "#UX", "#AgileProduct"],
    "finance": ["#FinTech", "#Finance", "#Investing", "#Blockchain", "#Crypto"],
    "marketing": ["#DigitalMarketing", "#ContentMarketing", "#SEO", "#GrowthHacking"],
    "ux": ["#UX", "#UIDesign", "#UserExperience", "#Figma", "#DesignThinking"],
    "open source": ["#OpenSource", "#GitHub", "#DevCommunity", "#Contributors"],
    "llm": ["#LLM", "#GenAI", "#ChatGPT", "#PromptEngineering", "#AI"],
    "devops": ["#DevOps", "#CI_CD", "#Docker", "#Kubernetes", "#SRE"],
    "security": ["#CyberSecurity", "#InfoSec", "#ZeroTrust", "#SIEM"],
}

GENERIC_HASHTAGS = ["#Innovation", "#Tech", "#FutureOfWork", "#Learning", "#GrowthMindset"]


class TrendAnalyzer:
    """
    Analyzes trends and recommends hashtags for LinkedIn content.
    """

    def __init__(self, llm_provider=None):
        self.llm = llm_provider
        logger.info("✅ TrendAnalyzer initialized")

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze(self, topic: str, industry: str = "tech") -> TrendAnalysisResult:
        """Analyze trends for a given topic."""
        try:
            hashtags = self._get_hashtags(topic)
            related = self._get_related_topics(topic)
            opportunities = self._get_content_opportunities(topic)
            audience_interests = self._get_audience_interests(topic)

            return TrendAnalysisResult(
                success=True,
                topic=topic,
                trending_hashtags=hashtags,
                related_topics=related,
                content_opportunities=opportunities,
                audience_interests=audience_interests,
                recommended_tone=self._recommend_tone(topic),
                best_content_type=self._recommend_content_type(topic),
                trend_score=self._estimate_trend_score(topic),
            )
        except Exception as exc:
            logger.error(f"❌ Trend analysis failed: {exc}")
            return TrendAnalysisResult(success=False, topic=topic, error_message=str(exc))

    def get_hashtags_for_topic(self, topic: str, limit: int = 10) -> List[str]:
        result = self.analyze(topic)
        return result.trending_hashtags[:limit]

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------

    def _get_hashtags(self, topic: str) -> List[str]:
        """Return relevant hashtags from curated map + LLM enhancement."""
        base = []
        topic_lower = topic.lower()
        for key, tags in HASHTAG_MAP.items():
            if key in topic_lower or topic_lower in key:
                base.extend(tags)
        if not base:
            base = GENERIC_HASHTAGS.copy()

        if self.llm and len(base) < 5:
            try:
                result = self.llm.generate(
                    prompt=f"Suggest 8 relevant LinkedIn hashtags for the topic: {topic}. Return one per line.",
                    system_prompt="You are a LinkedIn hashtag expert.",
                )
                if result.success:
                    llm_tags = [
                        t.strip() if t.strip().startswith("#") else f"#{t.strip()}"
                        for t in result.content.split("\n")
                        if t.strip()
                    ]
                    base.extend(llm_tags)
            except Exception:
                pass

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for t in base:
            if t not in seen:
                seen.add(t)
                unique.append(t)
        return unique[:12]

    def _get_related_topics(self, topic: str) -> List[str]:
        if self.llm:
            try:
                result = self.llm.generate(
                    prompt=f"List 5 related topics to '{topic}' for LinkedIn content. One per line.",
                    system_prompt="Be concise.",
                )
                if result.success:
                    return [l.strip().lstrip("-•0123456789. ") for l in result.content.split("\n") if l.strip()][:5]
            except Exception:
                pass
        return [f"{topic} best practices", f"{topic} trends 2025", f"{topic} for beginners"]

    def _get_content_opportunities(self, topic: str) -> List[str]:
        opportunities = [
            f"Share your {topic} journey",
            f"Debunk common {topic} myths",
            f"Teach a {topic} framework",
            f"Celebrate a {topic} win",
            f"Start a {topic} discussion",
        ]
        return opportunities

    def _get_audience_interests(self, topic: str) -> List[str]:
        return ["practical tips", "real-world examples", "career impact", "tools & resources"]

    def _recommend_tone(self, topic: str) -> str:
        topic_lower = topic.lower()
        if any(w in topic_lower for w in ["startup", "founder", "build"]):
            return "enthusiastic"
        if any(w in topic_lower for w in ["leadership", "management", "career"]):
            return "thoughtful"
        if any(w in topic_lower for w in ["hot take", "opinion", "debate"]):
            return "bold"
        return "professional"

    def _recommend_content_type(self, topic: str) -> str:
        topic_lower = topic.lower()
        if any(w in topic_lower for w in ["learn", "how to", "guide", "tutorial"]):
            return "educational"
        if any(w in topic_lower for w in ["built", "launched", "shipped"]):
            return "build_in_public"
        if any(w in topic_lower for w in ["opinion", "hot take", "unpopular"]):
            return "hot_take"
        return "educational"

    def _estimate_trend_score(self, topic: str) -> float:
        """Heuristic trend score 0-1."""
        hot_keywords = ["ai", "llm", "genai", "gpt", "startup", "saas", "cloud native"]
        topic_lower = topic.lower()
        matches = sum(1 for k in hot_keywords if k in topic_lower)
        return min(1.0, 0.4 + matches * 0.15)
