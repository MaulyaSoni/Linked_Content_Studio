"""
Content Intelligence Agent
==========================
Third agent in the pipeline.
Develops a full content strategy: identifies key messages, segments the
audience, and plans 3 post angles to be generated next.
"""

import time
from typing import Dict, List

from agents.base_agent import AgentResult, BaseAgent


class ContentIntelligenceAgent(BaseAgent):
    """Builds the content strategy and post variant plan."""

    def __init__(self, llm_provider=None):
        super().__init__("ContentIntelligence", llm_provider)

    def run(self, input_data: Dict) -> AgentResult:
        """
        input_data (merged context from previous agents):
            synthesis            : str
            combined_content     : str
            hashtags             : str
            recommended_tone     : str
            best_content_type    : str
            market_intelligence  : str
            content_gaps         : str
            tone (user pref)     : str
            audience (user pref) : str
        """
        start = time.time()
        self.logger.info("🧠 ContentIntelligenceAgent: building strategy...")

        synthesis = input_data.get("synthesis", "")
        combined = input_data.get("combined_content", "")
        hashtags = input_data.get("hashtags", "")
        market_intel = input_data.get("market_intelligence", "")
        content_gaps = input_data.get("content_gaps", "")
        tone = input_data.get("tone") or input_data.get("recommended_tone", "professional")
        audience = input_data.get("audience", "professionals")
        content_type = input_data.get("best_content_type", "educational")

        if not synthesis and not combined:
            return self._failure("No content to strategize", time.time() - start)

        strategy = {}
        angles = self._default_angles()

        if self.llm:
            strategy_raw = self.think(
                prompt=(
                    f"Build a LinkedIn content strategy for this topic.\n\n"
                    f"CONTENT:\n{synthesis[:2000]}\n\n"
                    f"MARKET INTELLIGENCE:\n{market_intel}\n\n"
                    f"CONTENT GAPS:\n{content_gaps}\n\n"
                    f"Tone preference: {tone} | Audience: {audience}\n\n"
                    f"Return:\n"
                    f"KEY_MESSAGE: [the single most important thing to communicate]\n"
                    f"TARGET_AUDIENCE: [specific audience description]\n"
                    f"EMOTIONAL_HOOK: [the emotional angle to lead with]\n"
                    f"ANGLE_1_STORYTELLER: [narrative-driven post angle in 2 sentences]\n"
                    f"ANGLE_2_STRATEGIST: [data/insight-driven angle in 2 sentences]\n"
                    f"ANGLE_3_PROVOCATEUR: [contrarian/bold angle in 2 sentences]\n"
                    f"CONTENT_PILLARS: [3 content pillars, comma-separated]\n"
                    f"CALL_TO_ACTION: [best CTA for this content]"
                ),
                system_prompt="You are a senior LinkedIn content strategist.",
            )
            strategy = self._parse_strategy(strategy_raw)
            angles = {
                "storyteller": strategy.pop("angle_storyteller", angles["storyteller"]),
                "strategist": strategy.pop("angle_strategist", angles["strategist"]),
                "provocateur": strategy.pop("angle_provocateur", angles["provocateur"]),
            }
        else:
            strategy = {
                "key_message": synthesis[:150],
                "target_audience": audience,
                "emotional_hook": "Share your authentic experience",
                "content_pillars": ["leadership", "innovation", "growth"],
                "call_to_action": "What's your experience? Share in the comments.",
            }

        output = {
            "strategy": strategy,
            "angles": angles,
            "tone": tone,
            "audience": audience,
            "content_type": content_type,
            "hashtags": hashtags,
            "synthesis": synthesis,
            "combined_content": combined,
        }

        return self._success(
            output=output,
            summary=f"Strategy built: 3 angles identified | KM: {strategy.get('key_message', '')[:80]}",
            context=output,
            next_hint="GenerationAgent",
            time=time.time() - start,
        )

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _parse_strategy(self, raw: str) -> Dict:
        data: Dict = {}
        for line in raw.strip().split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                key = k.strip().upper()
                val = v.strip()
                if key == "KEY_MESSAGE":
                    data["key_message"] = val
                elif key == "TARGET_AUDIENCE":
                    data["target_audience"] = val
                elif key == "EMOTIONAL_HOOK":
                    data["emotional_hook"] = val
                elif key == "ANGLE_1_STORYTELLER":
                    data["angle_storyteller"] = val
                elif key == "ANGLE_2_STRATEGIST":
                    data["angle_strategist"] = val
                elif key == "ANGLE_3_PROVOCATEUR":
                    data["angle_provocateur"] = val
                elif key == "CONTENT_PILLARS":
                    data["content_pillars"] = [p.strip() for p in val.split(",")]
                elif key == "CALL_TO_ACTION":
                    data["call_to_action"] = val
        return data

    def _default_angles(self) -> Dict:
        return {
            "storyteller": "Share a personal narrative around the topic.",
            "strategist": "Present data-driven insights and frameworks.",
            "provocateur": "Challenge conventional wisdom with a bold take.",
        }
