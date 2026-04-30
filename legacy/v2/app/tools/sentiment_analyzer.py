"""
Sentiment Analyzer Tool
=======================
Detects emotional tone, audience perception, and suggests emotional framing
for LinkedIn posts.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Result from sentiment analysis."""
    success: bool
    overall_sentiment: str = "neutral"    # positive / neutral / negative
    emotional_tone: str = "professional"  # e.g. inspiring, educational, urgent
    confidence: float = 0.5              # 0-1
    dominant_emotions: List[str] = field(default_factory=list)
    audience_perception: str = ""
    suggested_framing: str = ""
    engagement_potential: str = "medium"  # low / medium / high
    improvements: List[str] = field(default_factory=list)
    error_message: str = ""


# ---------------------------------------------------------------------------
# Simple keyword-based sentiment dictionaries
# ---------------------------------------------------------------------------
POSITIVE_WORDS = {
    "excited", "thrilled", "amazing", "incredible", "awesome", "love", "proud",
    "achieved", "won", "launched", "built", "shipped", "success", "milestone",
    "grateful", "inspired", "growth", "opportunity", "powerful", "breakthrough",
    "innovative", "game-changing", "transformative", "proud", "celebrate",
}

NEGATIVE_WORDS = {
    "failed", "mistake", "wrong", "lost", "struggle", "difficult", "hard",
    "rejected", "quit", "gave up", "impossible", "depressed", "frustrated",
    "broken", "worst", "mess", "disaster",
}

ENGAGING_WORDS = {
    "you", "your", "we", "our", "imagine", "what if", "how", "why",
    "question", "think", "believe", "share", "comment", "story",
}


class SentimentAnalyzer:
    """
    Analyzes the emotional tone of text for LinkedIn content optimization.
    """

    def __init__(self, llm_provider=None):
        self.llm = llm_provider
        logger.info("✅ SentimentAnalyzer initialized")

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment and emotional tone of text."""
        try:
            if self.llm:
                return self._llm_analyze(text)
            return self._heuristic_analyze(text)
        except Exception as exc:
            logger.error(f"❌ Sentiment analysis failed: {exc}")
            return SentimentResult(success=False, error_message=str(exc))

    def get_tone(self, text: str) -> str:
        """Quick shortcut — return dominant tone string."""
        result = self.analyze(text)
        return result.emotional_tone if result.success else "neutral"

    def predict_engagement(self, text: str) -> str:
        """Quick shortcut — return engagement potential."""
        result = self.analyze(text)
        return result.engagement_potential if result.success else "medium"

    # ------------------------------------------------------------------
    # LLM-BASED ANALYSIS
    # ------------------------------------------------------------------

    def _llm_analyze(self, text: str) -> SentimentResult:
        prompt = f"""Analyze the sentiment and emotional tone of this LinkedIn post text.

Text:
{text[:2000]}

Return your analysis in this exact format:
SENTIMENT: [positive/neutral/negative]
TONE: [one of: inspiring/educational/professional/urgent/celebratory/conversational/bold]
DOMINANT_EMOTIONS: [comma-separated emotions]
AUDIENCE_PERCEPTION: [one sentence how audience will perceive this]
SUGGESTED_FRAMING: [one sentence on how to improve framing]
ENGAGEMENT_POTENTIAL: [low/medium/high]
IMPROVEMENTS: [2-3 concrete improvements, pipe-separated]"""

        result = self.llm.generate(prompt=prompt, system_prompt="You are a LinkedIn content psychologist.")
        if not result.success:
            return self._heuristic_analyze(text)

        return self._parse_llm_result(result.content)

    def _parse_llm_result(self, raw: str) -> SentimentResult:
        data = {
            "sentiment": "neutral",
            "tone": "professional",
            "emotions": [],
            "perception": "",
            "framing": "",
            "engagement": "medium",
            "improvements": [],
        }

        for line in raw.strip().split("\n"):
            line = line.strip()
            if line.upper().startswith("SENTIMENT:"):
                data["sentiment"] = self._extract_value(line).lower()
            elif line.upper().startswith("TONE:"):
                data["tone"] = self._extract_value(line).lower()
            elif line.upper().startswith("DOMINANT_EMOTIONS:"):
                raw_emotions = self._extract_value(line)
                data["emotions"] = [e.strip() for e in raw_emotions.split(",") if e.strip()]
            elif line.upper().startswith("AUDIENCE_PERCEPTION:"):
                data["perception"] = self._extract_value(line)
            elif line.upper().startswith("SUGGESTED_FRAMING:"):
                data["framing"] = self._extract_value(line)
            elif line.upper().startswith("ENGAGEMENT_POTENTIAL:"):
                data["engagement"] = self._extract_value(line).lower()
            elif line.upper().startswith("IMPROVEMENTS:"):
                raw_imp = self._extract_value(line)
                data["improvements"] = [i.strip() for i in raw_imp.split("|") if i.strip()]

        return SentimentResult(
            success=True,
            overall_sentiment=data["sentiment"],
            emotional_tone=data["tone"],
            dominant_emotions=data["emotions"],
            audience_perception=data["perception"],
            suggested_framing=data["framing"],
            engagement_potential=data["engagement"],
            improvements=data["improvements"],
            confidence=0.85,
        )

    def _extract_value(self, line: str) -> str:
        parts = line.split(":", 1)
        return parts[1].strip() if len(parts) > 1 else ""

    # ------------------------------------------------------------------
    # HEURISTIC ANALYSIS (no LLM)
    # ------------------------------------------------------------------

    def _heuristic_analyze(self, text: str) -> SentimentResult:
        words = set(re.findall(r"\b\w+\b", text.lower()))

        pos_count = len(words & POSITIVE_WORDS)
        neg_count = len(words & NEGATIVE_WORDS)
        eng_count = len(words & ENGAGING_WORDS)

        if pos_count > neg_count + 2:
            sentiment = "positive"
            tone = "inspiring"
        elif neg_count > pos_count:
            sentiment = "negative"
            tone = "reflective"
        else:
            sentiment = "neutral"
            tone = "professional"

        if eng_count >= 3:
            engagement = "high"
        elif eng_count >= 1:
            engagement = "medium"
        else:
            engagement = "low"

        return SentimentResult(
            success=True,
            overall_sentiment=sentiment,
            emotional_tone=tone,
            dominant_emotions=[sentiment, "authentic"],
            audience_perception=f"Audience will find this {tone}.",
            suggested_framing="Add a personal story element to increase authenticity.",
            engagement_potential=engagement,
            improvements=["Add a question to invite discussion", "Use more personal pronouns"],
            confidence=0.6,
        )
