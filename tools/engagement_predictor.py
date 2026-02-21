"""
Engagement Predictor Tool
=========================
Forecasts reach, engagement metrics, and optimal posting times.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class EngagementPrediction:
    """Predicted engagement metrics for a LinkedIn post."""
    success: bool
    estimated_impressions: str = "500-2,000"
    estimated_likes: str = "10-50"
    estimated_comments: str = "2-10"
    estimated_shares: str = "1-5"
    engagement_rate: str = "2-4%"
    virality_score: float = 0.3           # 0-1
    best_posting_times: List[str] = field(default_factory=list)
    best_posting_days: List[str] = field(default_factory=list)
    format_recommendations: List[str] = field(default_factory=list)
    content_score: float = 0.5            # 0-1
    predicted_reach_tier: str = "moderate"  # low / moderate / high / viral
    optimization_tips: List[str] = field(default_factory=list)
    error_message: str = ""


# ---------------------------------------------------------------------------
# Scoring heuristics
# ---------------------------------------------------------------------------
VIRALITY_SIGNALS = {
    "question_mark": 0.15,
    "personal_story": 0.12,
    "numbered_list": 0.10,
    "emoji": 0.05,
    "controversial_word": 0.08,
    "data_mention": 0.07,
    "call_to_action": 0.10,
    "hashtag_count_optimal": 0.08,
}

BEST_TIMES = ["Tuesday 8-10 AM", "Wednesday 12-1 PM", "Thursday 9-11 AM", "Friday 7-9 AM"]
BEST_DAYS = ["Tuesday", "Wednesday", "Thursday"]


class EngagementPredictor:
    """
    Predicts LinkedIn post engagement based on content signals.
    """

    def __init__(self, llm_provider=None):
        self.llm = llm_provider
        logger.info("✅ EngagementPredictor initialized")

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def predict(self, post_text: str, hashtags: str = "", author_followers: int = 1000) -> EngagementPrediction:
        """Predict engagement for a post."""
        try:
            if self.llm:
                return self._llm_predict(post_text, hashtags, author_followers)
            return self._heuristic_predict(post_text, hashtags, author_followers)
        except Exception as exc:
            logger.error(f"❌ Engagement prediction failed: {exc}")
            return EngagementPrediction(success=False, error_message=str(exc))

    def get_optimal_time(self) -> str:
        """Return best single posting time."""
        hour = datetime.now().hour
        # Morning slot
        if 7 <= hour <= 9:
            return "Now is a great time! Post within the next hour."
        return "Best time: Tuesday or Thursday, 8-10 AM in your local timezone."

    def get_format_tips(self, post_text: str) -> List[str]:
        result = self.predict(post_text)
        return result.format_recommendations

    # ------------------------------------------------------------------
    # LLM PREDICTION
    # ------------------------------------------------------------------

    def _llm_predict(self, post_text: str, hashtags: str, followers: int) -> EngagementPrediction:
        prompt = f"""Analyze this LinkedIn post for engagement potential.

Post:
{post_text[:2000]}

Hashtags: {hashtags}
Author followers: ~{followers}

Return analysis in EXACT format:
IMPRESSIONS: [range]
LIKES: [range]
COMMENTS: [range]
SHARES: [range]
ENGAGEMENT_RATE: [percentage range]
VIRALITY_SCORE: [0.0-1.0]
REACH_TIER: [low/moderate/high/viral]
POSTING_TIMES: [comma-separated best times]
POSTING_DAYS: [comma-separated best days]
FORMAT_TIPS: [pipe-separated tips]
OPTIMIZATION_TIPS: [pipe-separated tips]"""

        result = self.llm.generate(prompt=prompt, system_prompt="You are a LinkedIn analytics expert.")
        if not result.success:
            return self._heuristic_predict(post_text, hashtags, followers)
        return self._parse_llm_prediction(result.content)

    def _parse_llm_prediction(self, raw: str) -> EngagementPrediction:
        data: Dict = {}
        for line in raw.strip().split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                data[key.strip().upper()] = val.strip()

        def get(k, default=""):
            return data.get(k, default)

        return EngagementPrediction(
            success=True,
            estimated_impressions=get("IMPRESSIONS", "500-2,000"),
            estimated_likes=get("LIKES", "10-50"),
            estimated_comments=get("COMMENTS", "2-10"),
            estimated_shares=get("SHARES", "1-5"),
            engagement_rate=get("ENGAGEMENT_RATE", "2-4%"),
            virality_score=self._safe_float(get("VIRALITY_SCORE", "0.4")),
            predicted_reach_tier=get("REACH_TIER", "moderate").lower(),
            best_posting_times=[t.strip() for t in get("POSTING_TIMES", "").split(",") if t.strip()] or BEST_TIMES,
            best_posting_days=[d.strip() for d in get("POSTING_DAYS", "").split(",") if d.strip()] or BEST_DAYS,
            format_recommendations=[t.strip() for t in get("FORMAT_TIPS", "").split("|") if t.strip()],
            optimization_tips=[t.strip() for t in get("OPTIMIZATION_TIPS", "").split("|") if t.strip()],
            content_score=self._safe_float(get("VIRALITY_SCORE", "0.4")),
        )

    # ------------------------------------------------------------------
    # HEURISTIC PREDICTION
    # ------------------------------------------------------------------

    def _heuristic_predict(self, post_text: str, hashtags: str, followers: int) -> EngagementPrediction:
        score = 0.0
        text_lower = post_text.lower()

        if "?" in post_text:
            score += VIRALITY_SIGNALS["question_mark"]
        if any(w in text_lower for w in ["i ", "my ", "we ", "our "]):
            score += VIRALITY_SIGNALS["personal_story"]
        if any(c in post_text for c in ["1.", "2.", "3.", "•", "-"]):
            score += VIRALITY_SIGNALS["numbered_list"]
        if any(c in post_text for c in ["🚀", "💡", "✅", "🎯", "🔥"]):
            score += VIRALITY_SIGNALS["emoji"]
        if any(w in text_lower for w in ["%", "study", "data", "research", "increase"]):
            score += VIRALITY_SIGNALS["data_mention"]
        if any(w in text_lower for w in ["comment", "share", "thoughts", "let me know"]):
            score += VIRALITY_SIGNALS["call_to_action"]

        hashtag_count = len(hashtags.split()) if hashtags else 0
        if 3 <= hashtag_count <= 8:
            score += VIRALITY_SIGNALS["hashtag_count_optimal"]

        score = min(1.0, score)

        if score >= 0.7:
            tier = "high"
            impressions = "5,000-20,000"
            likes = "200-800"
        elif score >= 0.45:
            tier = "moderate"
            impressions = "1,000-5,000"
            likes = "50-200"
        else:
            tier = "low"
            impressions = "200-1,000"
            likes = "10-50"

        # Scale with followers
        multiplier = max(1, followers / 1000)
        tips = []
        if "?" not in post_text:
            tips.append("Add a question to spark comments")
        if score < 0.5:
            tips.append("Include a personal story or lesson")
        if hashtag_count < 3:
            tips.append("Add 3-5 relevant hashtags")
        tips.append("Post on Tuesday or Thursday morning for best reach")

        return EngagementPrediction(
            success=True,
            estimated_impressions=impressions,
            estimated_likes=likes,
            estimated_comments="5-30",
            estimated_shares="1-10",
            engagement_rate=f"{round(score * 6, 1)}-{round(score * 10, 1)}%",
            virality_score=round(score, 2),
            predicted_reach_tier=tier,
            best_posting_times=BEST_TIMES[:3],
            best_posting_days=BEST_DAYS,
            format_recommendations=["Use line breaks for mobile readability", "Keep under 1500 chars for best reach"],
            optimization_tips=tips,
            content_score=round(score, 2),
        )

    def _safe_float(self, val: str) -> float:
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.4
