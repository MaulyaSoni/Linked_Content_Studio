"""
Optimization Agent
==================
Sixth and final agent in the pipeline.
Predicts engagement, recommends posting times, optimizes hashtags,
and produces the final polished outputs.
"""

import time
from typing import Any, Dict, List

from agents.base_agent import AgentResult, BaseAgent
from tools.engagement_predictor import EngagementPredictor
from tools.sentiment_analyzer import SentimentAnalyzer


class OptimizationAgent(BaseAgent):
    """Optimizes posts for reach, engagement, and timing."""

    def __init__(self, llm_provider=None):
        super().__init__("OptimizationAgent", llm_provider)
        self.engagement_predictor = EngagementPredictor(llm_provider)
        self.sentiment_analyzer = SentimentAnalyzer(llm_provider)

    def run(self, input_data: Dict) -> AgentResult:
        """
        input_data (from BrandVoiceAgent output):
            variants            : dict  {storyteller, strategist, provocateur}
            hashtags            : str
            brand_feedback      : dict
            strategy            : dict
        """
        start = time.time()
        self.logger.info("⚡ OptimizationAgent: optimizing for engagement...")

        variants: Dict = input_data.get("variants", {})
        hashtags: str = input_data.get("hashtags", "")
        brand_feedback: Dict = input_data.get("brand_feedback", {})
        strategy: Dict = input_data.get("strategy", {})

        if not variants:
            return self._failure("No variants to optimize", time.time() - start)

        optimization_data: Dict = {}
        best_variant_key = "storyteller"
        best_score = 0.0

        for variant_key, post_text in variants.items():
            # Engagement prediction
            eng = self.engagement_predictor.predict(post_text, hashtags)
            # Sentiment analysis
            sent = self.sentiment_analyzer.analyze(post_text)

            opt_tips = eng.optimization_tips if eng.success else []
            if sent.success:
                opt_tips.extend(sent.improvements)

            score = eng.virality_score if eng.success else 0.4

            optimization_data[variant_key] = {
                "engagement": {
                    "impressions": eng.estimated_impressions if eng.success else "500-2,000",
                    "likes": eng.estimated_likes if eng.success else "10-50",
                    "comments": eng.estimated_comments if eng.success else "2-10",
                    "engagement_rate": eng.engagement_rate if eng.success else "2-4%",
                    "virality_score": score,
                    "reach_tier": eng.predicted_reach_tier if eng.success else "moderate",
                    "best_times": eng.best_posting_times if eng.success else [],
                    "best_days": eng.best_posting_days if eng.success else [],
                },
                "sentiment": {
                    "tone": sent.emotional_tone if sent.success else "professional",
                    "sentiment": sent.overall_sentiment if sent.success else "neutral",
                    "audience_perception": sent.audience_perception if sent.success else "",
                },
                "optimization_tips": list(dict.fromkeys(opt_tips))[:5],
                "virality_score": score,
            }

            if score > best_score:
                best_score = score
                best_variant_key = variant_key

        # Final hashtag optimization
        optimized_hashtags = self._optimize_hashtags(hashtags, variants, strategy)

        output = {
            "variants": variants,
            "hashtags": optimized_hashtags,
            "optimization": optimization_data,
            "best_variant": best_variant_key,
            "best_variant_score": round(best_score, 2),
            "brand_feedback": brand_feedback,
            "strategy": strategy,
            "overall_recommendations": self._build_recommendations(
                optimization_data, best_variant_key, strategy
            ),
        }

        return self._success(
            output=output,
            summary=(
                f"Optimization complete. Best variant: {best_variant_key} "
                f"(score {best_score:.1f}). "
                f"Hashtags: {len(optimized_hashtags.split())} tags."
            ),
            context=output,
            next_hint="COMPLETE",
            time=time.time() - start,
        )

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _optimize_hashtags(self, hashtags: str, variants: Dict, strategy: Dict) -> str:
        """Keep 5-8 best hashtags."""
        tags = hashtags.split()
        # Add strategy-based tags
        pillars = strategy.get("content_pillars", [])
        for pillar in pillars[:2]:
            tag = f"#{pillar.replace(' ', '').capitalize()}"
            if tag not in tags:
                tags.append(tag)
        # Limit to 8
        return " ".join(tags[:8])

    def _build_recommendations(
        self, opt_data: Dict, best_variant: str, strategy: Dict
    ) -> List[str]:
        recs = [
            f"🏆 Use the '{best_variant.capitalize()}' variant for best expected engagement",
            f"⏰ {self.engagement_predictor.get_optimal_time()}",
        ]
        tips = opt_data.get(best_variant, {}).get("optimization_tips", [])
        recs.extend(tips[:3])
        if strategy.get("call_to_action"):
            recs.append(f"💬 CTA: {strategy['call_to_action']}")
        return recs
