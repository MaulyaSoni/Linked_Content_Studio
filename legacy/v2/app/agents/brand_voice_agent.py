"""
Brand Voice Agent
=================
Fifth agent in the pipeline.
Checks generated variants against the user's brand DNA and
personalizes them to match the established voice.
"""

import time
from typing import Dict, List, Optional

from agents.base_agent import AgentResult, BaseAgent
from tools.brand_analyzer import BrandAnalyzer, BrandProfile


class BrandVoiceAgent(BaseAgent):
    """Personalizes posts to match user's brand voice and DNA."""

    def __init__(self, llm_provider=None):
        super().__init__("BrandVoiceAgent", llm_provider)
        self.brand_analyzer = BrandAnalyzer(llm_provider)
        # Try to load persisted brand profile
        self._profile: Optional[BrandProfile] = self.brand_analyzer.load_profile()

    def run(self, input_data: Dict) -> AgentResult:
        """
        input_data (from GenerationAgent output):
            variants    : dict  {storyteller, strategist, provocateur}
            hashtags    : str
            strategy    : dict
            past_posts  : list  (optional — user's past posts for branding)
        """
        start = time.time()
        self.logger.info("🎨 BrandVoiceAgent: personalizing for brand voice...")

        variants: Dict = input_data.get("variants", {})
        hashtags: str = input_data.get("hashtags", "")
        past_posts: List[str] = input_data.get("past_posts", [])

        if not variants:
            return self._failure("No variants to brand-check", time.time() - start)

        # Build brand profile from past posts if provided and no profile loaded
        if past_posts and (not self._profile or not self._profile.success):
            self._profile = self.brand_analyzer.analyze_past_posts(past_posts)
            self.logger.info(f"📊 Brand profile built from {len(past_posts)} past posts")

        brand_feedback: Dict = {}
        adjusted_variants: Dict = dict(variants)

        for variant_key, post_text in variants.items():
            if self._profile and self._profile.success:
                check = self.brand_analyzer.check_consistency(post_text, self._profile)
                brand_feedback[variant_key] = {
                    "consistency_score": check.consistency_score,
                    "aligned": check.aligned_elements,
                    "deviations": check.deviations,
                    "suggestions": check.suggestions,
                    "brand_aligned": check.brand_aligned,
                }

                # If LLM available and consistency is low, personalize
                if self.llm and check.consistency_score < 0.7 and self._profile:
                    adjusted = self._personalize(post_text, self._profile)
                    if adjusted:
                        adjusted_variants[variant_key] = adjusted
            else:
                brand_feedback[variant_key] = {
                    "consistency_score": 0.7,
                    "aligned": ["No brand profile available — post is ready to use"],
                    "deviations": [],
                    "suggestions": ["Add past posts to build your brand DNA for better personalization"],
                    "brand_aligned": True,
                }

        avg_score = sum(
            v.get("consistency_score", 0.7) for v in brand_feedback.values()
        ) / max(1, len(brand_feedback))

        output = {
            "variants": adjusted_variants,
            "hashtags": hashtags,
            "brand_feedback": brand_feedback,
            "brand_consistency_avg": round(avg_score, 2),
            "strategy": input_data.get("strategy", {}),
        }

        return self._success(
            output=output,
            summary=f"Brand check complete. Avg consistency: {avg_score:.0%}",
            context=output,
            next_hint="OptimizationAgent",
            time=time.time() - start,
        )

    # ------------------------------------------------------------------
    # PERSONALIZATION
    # ------------------------------------------------------------------

    def _personalize(self, post: str, profile: BrandProfile) -> str:
        """Ask LLM to rewrite post to better match brand DNA."""
        voice_desc = profile.brand_voice_summary or (
            f"Tone: {profile.dominant_tone}. "
            f"Uses emojis: {profile.uses_emojis}. "
            f"Storytelling: {profile.uses_storytelling}. "
            f"Lists: {profile.uses_lists}."
        )
        prompt = (
            f"Rewrite this LinkedIn post to better match this brand voice:\n"
            f"BRAND VOICE: {voice_desc}\n\n"
            f"ORIGINAL POST:\n{post}\n\n"
            f"Rules:\n"
            f"- Keep the core message identical\n"
            f"- Only adjust tone/style to match brand\n"
            f"- No fake statistics\n"
            f"- Return ONLY the rewritten post"
        )
        result = self.llm.generate(prompt=prompt, system_prompt="You are a brand voice specialist.")
        return result.content.strip() if result.success else ""
