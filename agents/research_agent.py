"""
Research Agent
==============
Second agent in the pipeline.
Uses TrendAnalyzer and web research to gather market intelligence,
trending topics, and hashtag recommendations.
"""

import time
from typing import Dict, List

from agents.base_agent import AgentResult, BaseAgent
from tools.trend_analyzer import TrendAnalyzer


class ResearchAgent(BaseAgent):
    """Gathers trend data, hashtags, and market intelligence."""

    def __init__(self, llm_provider=None):
        super().__init__("ResearchAgent", llm_provider)
        self.trend_analyzer = TrendAnalyzer(llm_provider)

    def run(self, input_data: Dict) -> AgentResult:
        """
        input_data keys (from InputProcessorAgent context):
            synthesis       : str  - processed content summary
            combined_content: str  - full extracted content
            themes          : list - detected themes
        plus original input:
            text            : str
            topic           : str (optional explicit override)
        """
        start = time.time()
        self.logger.info("🔬 ResearchAgent: gathering market intelligence...")

        synthesis = input_data.get("synthesis", "")
        combined = input_data.get("combined_content", "")
        themes: List[str] = input_data.get("themes", [])
        topic = input_data.get("topic") or input_data.get("text", "") or synthesis[:100]

        if not topic.strip():
            return self._failure("No topic available for research", time.time() - start)

        # 1. Trend analysis
        trend_result = self.trend_analyzer.analyze(topic)

        # 2. If LLM available — deeper market intelligence
        competitor_insights = ""
        content_gaps = ""
        if self.llm:
            competitor_insights = self.think(
                prompt=(
                    f"Topic: {topic}\n"
                    f"What content about this topic performs best on LinkedIn right now? "
                    f"Give 3 insights about what the audience currently craves."
                ),
                system_prompt="You are a LinkedIn content market researcher.",
            )
            content_gaps = self.think(
                prompt=(
                    f"Topic: {topic}\n"
                    f"What angles or perspectives are under-represented on LinkedIn for this topic? "
                    f"Give 3 content gap opportunities."
                ),
                system_prompt="You are a content strategy expert.",
            )

        output = {
            "topic": topic,
            "trending_hashtags": trend_result.trending_hashtags if trend_result.success else [],
            "related_topics": trend_result.related_topics if trend_result.success else [],
            "content_opportunities": trend_result.content_opportunities if trend_result.success else [],
            "recommended_tone": trend_result.recommended_tone if trend_result.success else "professional",
            "best_content_type": trend_result.best_content_type if trend_result.success else "educational",
            "trend_score": trend_result.trend_score if trend_result.success else 0.5,
            "competitor_insights": competitor_insights,
            "content_gaps": content_gaps,
            "audience_interests": trend_result.audience_interests if trend_result.success else [],
        }

        return self._success(
            output=output,
            summary=f"Research complete for '{topic}' — {len(output['trending_hashtags'])} hashtags, trend score {output['trend_score']:.1f}",
            context={
                "hashtags": " ".join(output["trending_hashtags"][:8]),
                "recommended_tone": output["recommended_tone"],
                "best_content_type": output["best_content_type"],
                "market_intelligence": competitor_insights,
            },
            next_hint="ContentIntelligenceAgent",
            time=time.time() - start,
        )
