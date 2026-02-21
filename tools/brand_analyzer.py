"""
Brand Analyzer Tool
===================
Learns from past LinkedIn posts to build a Personal Brand DNA profile.
Analyzes voice patterns, writing style, and consistency.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class BrandProfile:
    """Distilled brand DNA from analyzed posts."""
    success: bool
    dominant_tone: str = "professional"
    vocabulary_level: str = "intermediate"        # basic/intermediate/advanced
    avg_post_length: int = 250
    uses_emojis: bool = False
    uses_storytelling: bool = False
    uses_lists: bool = False
    uses_questions: bool = False
    signature_phrases: List[str] = field(default_factory=list)
    common_themes: List[str] = field(default_factory=list)
    hashtag_style: str = "moderate"               # none/light/moderate/heavy
    avg_hashtag_count: float = 3.0
    writing_style: str = ""
    brand_voice_summary: str = ""
    consistency_score: float = 0.5
    error_message: str = ""


@dataclass
class ConsistencyCheckResult:
    """Result when checking a new post against brand DNA."""
    success: bool
    consistency_score: float = 0.5
    aligned_elements: List[str] = field(default_factory=list)
    deviations: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    brand_aligned: bool = True
    error_message: str = ""


class BrandAnalyzer:
    """
    Analyzes a user's past LinkedIn posts to extract brand DNA.
    Checks new posts for consistency with established voice.
    """

    def __init__(self, llm_provider=None, profile_path: str = "data/brand_profile.json"):
        self.llm = llm_provider
        self.profile_path = Path(profile_path)
        self._cached_profile: Optional[BrandProfile] = None
        logger.info("✅ BrandAnalyzer initialized")

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze_past_posts(self, posts: List[str]) -> BrandProfile:
        """Extract brand DNA from a list of past post texts."""
        if not posts:
            return BrandProfile(success=False, error_message="No posts provided")
        try:
            if self.llm:
                profile = self._llm_analyze(posts)
            else:
                profile = self._heuristic_analyze(posts)
            self._cache_profile(profile)
            return profile
        except Exception as exc:
            logger.error(f"❌ Brand analysis failed: {exc}")
            return BrandProfile(success=False, error_message=str(exc))

    def check_consistency(self, new_post: str, profile: Optional[BrandProfile] = None) -> ConsistencyCheckResult:
        """Check how well a new post aligns with brand DNA."""
        bp = profile or self._cached_profile
        if not bp or not bp.success:
            return ConsistencyCheckResult(
                success=True,
                consistency_score=0.5,
                suggestions=["Build your brand profile first by analyzing past posts."],
            )
        try:
            if self.llm:
                return self._llm_check(new_post, bp)
            return self._heuristic_check(new_post, bp)
        except Exception as exc:
            return ConsistencyCheckResult(success=False, error_message=str(exc))

    def load_profile(self) -> Optional[BrandProfile]:
        """Load persisted brand profile from disk."""
        if not self.profile_path.exists():
            return None
        try:
            data = json.loads(self.profile_path.read_text())
            profile = BrandProfile(success=True, **data)
            self._cached_profile = profile
            return profile
        except Exception as exc:
            logger.warning(f"⚠️ Could not load brand profile: {exc}")
            return None

    # ------------------------------------------------------------------
    # LLM ANALYSIS
    # ------------------------------------------------------------------

    def _llm_analyze(self, posts: List[str]) -> BrandProfile:
        sample = "\n\n---\n\n".join(posts[:10])[:5000]
        prompt = f"""Analyze these LinkedIn posts to extract a brand DNA profile.

Posts:
{sample}

Return in EXACT format:
DOMINANT_TONE: [professional/casual/enthusiastic/thoughtful/bold]
VOCABULARY_LEVEL: [basic/intermediate/advanced]
AVG_POST_LENGTH: [number in words]
USES_EMOJIS: [yes/no]
USES_STORYTELLING: [yes/no]
USES_LISTS: [yes/no]
USES_QUESTIONS: [yes/no]
SIGNATURE_PHRASES: [pipe-separated phrases this author uses]
COMMON_THEMES: [comma-separated topics]
HASHTAG_STYLE: [none/light/moderate/heavy]
AVG_HASHTAG_COUNT: [number]
WRITING_STYLE: [one sentence description]
BRAND_VOICE_SUMMARY: [2-3 sentence overall brand voice description]"""

        result = self.llm.generate(prompt=prompt, system_prompt="You are a brand voice analyst.")
        if not result.success:
            return self._heuristic_analyze(posts)
        return self._parse_llm_profile(result.content)

    def _parse_llm_profile(self, raw: str) -> BrandProfile:
        data: Dict = {}
        for line in raw.strip().split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                data[k.strip().upper()] = v.strip()

        def g(k, d=""):
            return data.get(k, d)

        return BrandProfile(
            success=True,
            dominant_tone=g("DOMINANT_TONE", "professional"),
            vocabulary_level=g("VOCABULARY_LEVEL", "intermediate"),
            avg_post_length=self._safe_int(g("AVG_POST_LENGTH", "250")),
            uses_emojis=g("USES_EMOJIS", "no").lower() == "yes",
            uses_storytelling=g("USES_STORYTELLING", "no").lower() == "yes",
            uses_lists=g("USES_LISTS", "no").lower() == "yes",
            uses_questions=g("USES_QUESTIONS", "no").lower() == "yes",
            signature_phrases=[p.strip() for p in g("SIGNATURE_PHRASES", "").split("|") if p.strip()],
            common_themes=[t.strip() for t in g("COMMON_THEMES", "").split(",") if t.strip()],
            hashtag_style=g("HASHTAG_STYLE", "moderate"),
            avg_hashtag_count=self._safe_float(g("AVG_HASHTAG_COUNT", "3")),
            writing_style=g("WRITING_STYLE", ""),
            brand_voice_summary=g("BRAND_VOICE_SUMMARY", ""),
            consistency_score=0.85,
        )

    def _llm_check(self, post: str, profile: BrandProfile) -> ConsistencyCheckResult:
        summary = profile.brand_voice_summary or f"Tone: {profile.dominant_tone}, style: {profile.writing_style}"
        prompt = f"""Brand DNA: {summary}
Tone: {profile.dominant_tone} | Storytelling: {profile.uses_storytelling} | Lists: {profile.uses_lists}

New Post:
{post[:1500]}

Return:
SCORE: [0.0-1.0]
ALIGNED: [pipe-separated aligned elements]
DEVIATIONS: [pipe-separated deviations]
SUGGESTIONS: [pipe-separated improvement suggestions]"""

        result = self.llm.generate(prompt=prompt, system_prompt="You are a brand consistency expert.")
        if not result.success:
            return self._heuristic_check(post, profile)

        data: Dict = {}
        for line in result.content.strip().split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                data[k.strip().upper()] = v.strip()

        score = self._safe_float(data.get("SCORE", "0.7"))
        return ConsistencyCheckResult(
            success=True,
            consistency_score=score,
            aligned_elements=[e.strip() for e in data.get("ALIGNED", "").split("|") if e.strip()],
            deviations=[e.strip() for e in data.get("DEVIATIONS", "").split("|") if e.strip()],
            suggestions=[e.strip() for e in data.get("SUGGESTIONS", "").split("|") if e.strip()],
            brand_aligned=score >= 0.6,
        )

    # ------------------------------------------------------------------
    # HEURISTIC ANALYSIS
    # ------------------------------------------------------------------

    def _heuristic_analyze(self, posts: List[str]) -> BrandProfile:
        all_text = " ".join(posts)
        words = all_text.split()
        avg_len = sum(len(p.split()) for p in posts) // max(1, len(posts))

        emoji_count = sum(1 for p in posts if any(ord(c) > 127 for c in p))
        uses_emojis = emoji_count > len(posts) * 0.4

        question_count = sum(1 for p in posts if "?" in p)
        uses_questions = question_count > len(posts) * 0.3

        list_count = sum(1 for p in posts if "•" in p or "\n-" in p or "\n1." in p)
        uses_lists = list_count > len(posts) * 0.3

        hashtag_counts = [len(re.findall(r"#\w+", p)) for p in posts]
        avg_hashtags = sum(hashtag_counts) / max(1, len(hashtag_counts))

        return BrandProfile(
            success=True,
            dominant_tone="professional",
            avg_post_length=avg_len,
            uses_emojis=uses_emojis,
            uses_questions=uses_questions,
            uses_lists=uses_lists,
            uses_storytelling=any("when" in p.lower() or "story" in p.lower() for p in posts),
            avg_hashtag_count=round(avg_hashtags, 1),
            hashtag_style="heavy" if avg_hashtags > 8 else "moderate" if avg_hashtags > 3 else "light",
            common_themes=["professional", "tech", "growth"],
            writing_style="Concise professional posts with practical insights.",
            brand_voice_summary="Informed professional voice sharing actionable knowledge.",
            consistency_score=0.7,
        )

    def _heuristic_check(self, post: str, profile: BrandProfile) -> ConsistencyCheckResult:
        score = 0.5
        aligned = []
        deviations = []
        suggestions = []

        has_emojis = any(ord(c) > 127 for c in post)
        if has_emojis == profile.uses_emojis:
            score += 0.1
            aligned.append("Emoji usage matches brand style")
        else:
            deviations.append("Emoji usage differs from brand style")
            if profile.uses_emojis:
                suggestions.append("Add a few emojis to match your brand style")
            else:
                suggestions.append("Reduce emoji usage to match brand tone")

        words = len(post.split())
        if abs(words - profile.avg_post_length) < profile.avg_post_length * 0.4:
            score += 0.1
            aligned.append("Post length aligns with brand average")
        else:
            deviations.append("Post length differs from usual")

        return ConsistencyCheckResult(
            success=True,
            consistency_score=min(1.0, score),
            aligned_elements=aligned,
            deviations=deviations,
            suggestions=suggestions or ["Great brand alignment!"],
            brand_aligned=score >= 0.5,
        )

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _cache_profile(self, profile: BrandProfile):
        self._cached_profile = profile
        try:
            self.profile_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                k: v for k, v in profile.__dict__.items()
                if k not in ("success", "error_message")
            }
            self.profile_path.write_text(json.dumps(data, indent=2))
        except Exception as exc:
            logger.warning(f"⚠️ Could not persist brand profile: {exc}")

    def _safe_int(self, val: str) -> int:
        try:
            return int(re.sub(r"[^\d]", "", val) or "250")
        except (ValueError, TypeError):
            return 250

    def _safe_float(self, val: str) -> float:
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.5
