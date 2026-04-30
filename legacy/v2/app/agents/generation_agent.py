"""
Generation Agent
================
Fourth agent in the pipeline.
Generates 3 optimized LinkedIn post variants using the strategy from
ContentIntelligenceAgent: Storyteller, Strategist, Provocateur.
"""

import time
from typing import Dict, List

from agents.base_agent import AgentResult, BaseAgent


VARIANT_SYSTEM_PROMPTS = {
    "storyteller": (
        "You are a master LinkedIn storyteller. Write narrative-driven posts that "
        "open with a personal hook, build tension, deliver insight, and end with a "
        "genuine question. Sound like a real human, not a content machine."
    ),
    "strategist": (
        "You are a sharp LinkedIn strategist. Write data-driven, insight-led posts "
        "that open with a bold fact or framework, deliver structured value (lists/steps), "
        "and close with a discussion-provoking question."
    ),
    "provocateur": (
        "You are a bold LinkedIn thought leader. Write contrarian posts that challenge "
        "conventional wisdom, open with an opinion that makes people stop scrolling, "
        "argue your position with evidence, and invite debate."
    ),
}


class GenerationAgent(BaseAgent):
    """Creates 3 LinkedIn post variants from the content strategy."""

    def __init__(self, llm_provider=None):
        super().__init__("GenerationAgent", llm_provider)

    def run(self, input_data: Dict) -> AgentResult:
        """
        input_data (merged context, includes ContentIntelligenceAgent output):
            strategy        : dict
            angles          : dict (storyteller/strategist/provocateur)
            synthesis       : str
            combined_content: str
            tone            : str
            audience        : str
            hashtags        : str
        """
        start = time.time()
        self.logger.info("✍️  GenerationAgent: creating 3 post variants...")

        strategy: Dict = input_data.get("strategy", {})
        angles: Dict = input_data.get("angles", {})
        synthesis = input_data.get("synthesis", "")
        combined = input_data.get("combined_content", synthesis)
        tone = input_data.get("tone", "professional")
        audience = input_data.get("audience", "professionals")
        hashtags = input_data.get("hashtags", "")

        if not combined and not synthesis:
            return self._failure("No content available for generation", time.time() - start)

        variants: Dict[str, str] = {}
        variant_names = ["storyteller", "strategist", "provocateur"]

        for variant in variant_names:
            post = self._generate_variant(
                variant_type=variant,
                angle=angles.get(variant, ""),
                content=combined[:2500],
                strategy=strategy,
                tone=tone,
                audience=audience,
                hashtags=hashtags,
            )
            variants[variant] = post
            self.logger.info(f"  ✅ {variant.capitalize()} variant generated ({len(post)} chars)")

        output = {
            "variants": variants,
            "hashtags": hashtags,
            "strategy": strategy,
            "tone": tone,
            "audience": audience,
        }

        return self._success(
            output=output,
            summary=f"Generated 3 variants: Storyteller ({len(variants['storyteller'])} chars), "
                    f"Strategist ({len(variants['strategist'])} chars), "
                    f"Provocateur ({len(variants['provocateur'])} chars)",
            context=output,
            next_hint="BrandVoiceAgent",
            time=time.time() - start,
        )

    # ------------------------------------------------------------------
    # GENERATION
    # ------------------------------------------------------------------

    def _generate_variant(
        self,
        variant_type: str,
        angle: str,
        content: str,
        strategy: Dict,
        tone: str,
        audience: str,
        hashtags: str,
    ) -> str:
        if not self.llm:
            return self._fallback_variant(variant_type, content)

        sys_prompt = VARIANT_SYSTEM_PROMPTS.get(variant_type, VARIANT_SYSTEM_PROMPTS["storyteller"])
        key_message = strategy.get("key_message", "")
        cta = strategy.get("call_to_action", "What do you think? Share in the comments.")

        prompt = (
            f"Write a LinkedIn post using the '{variant_type}' style.\n\n"
            f"CONTENT TO USE:\n{content}\n\n"
            f"POST ANGLE: {angle}\n"
            f"KEY MESSAGE: {key_message}\n"
            f"TONE: {tone}\n"
            f"TARGET AUDIENCE: {audience}\n"
            f"CALL TO ACTION: {cta}\n\n"
            f"RULES:\n"
            f"- Max 1500 characters (ideal LinkedIn length)\n"
            f"- No fake statistics unless from the source content\n"
            f"- End with a genuine question\n"
            f"- Use line breaks for mobile readability\n"
            f"- DO NOT include hashtags (handled separately)\n"
            f"- Return ONLY the post text, no labels or explanations"
        )

        result = self.llm.generate(prompt=prompt, system_prompt=sys_prompt)
        return result.content.strip() if result.success else self._fallback_variant(variant_type, content)

    def _fallback_variant(self, variant_type: str, content: str) -> str:
        topic = content[:80].replace("\n", " ")
        fallbacks = {
            "storyteller": (
                f"Here's what changed my perspective on {topic}...\n\n"
                f"Three years ago I wouldn't have believed it.\n"
                f"Now it's how I approach everything.\n\n"
                f"The journey matters more than the destination.\n\n"
                f"What has shifted your perspective recently?"
            ),
            "strategist": (
                f"Most people overlook this about {topic}.\n\n"
                f"Here's a framework that actually works:\n\n"
                f"• Start with the outcome\n"
                f"• Remove friction at every step\n"
                f"• Measure what matters\n\n"
                f"Which step matters most to you?"
            ),
            "provocateur": (
                f"Unpopular opinion: {topic} is misunderstood.\n\n"
                f"Everyone talks about the 'right way'.\n"
                f"No one talks about the cost.\n\n"
                f"Maybe it's time to challenge the default.\n\n"
                f"Do you agree — or am I wrong?"
            ),
        }
        return fallbacks.get(variant_type, fallbacks["storyteller"])
