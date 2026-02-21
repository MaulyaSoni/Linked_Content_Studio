"""
Agent Orchestrator
==================
Coordinates all 6 agents in sequence, passing context between them.
Provides real-time status callbacks for UI visualization.

Workflow:
    InputProcessor → Research → ContentIntelligence → Generation → BrandVoice → Optimization
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from agents.base_agent import AgentResult
from agents.input_processor_agent import InputProcessorAgent
from agents.research_agent import ResearchAgent
from agents.content_intelligence_agent import ContentIntelligenceAgent
from agents.generation_agent import GenerationAgent
from agents.brand_voice_agent import BrandVoiceAgent
from agents.optimization_agent import OptimizationAgent

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStatus:
    """Real-time status update for UI."""
    agent_name: str
    status: str          # "running" | "complete" | "error" | "skipped"
    message: str = ""
    progress: float = 0.0  # 0-1
    elapsed: float = 0.0


@dataclass
class OrchestratorResult:
    """Final result from the entire agentic workflow."""
    success: bool
    # Core outputs
    variants: Dict[str, str] = field(default_factory=dict)
    hashtags: str = ""
    strategy: Dict = field(default_factory=dict)
    # Intelligence outputs
    research: Dict = field(default_factory=dict)
    brand_feedback: Dict = field(default_factory=dict)
    optimization: Dict = field(default_factory=dict)
    overall_recommendations: List[str] = field(default_factory=list)
    best_variant: str = "storyteller"
    # Metadata
    total_time: float = 0.0
    agents_run: List[str] = field(default_factory=list)
    error_message: str = ""


# Pipeline definition: (agent_class, weight_for_progress)
PIPELINE = [
    ("InputProcessor",       InputProcessorAgent,       0.10),
    ("Research",             ResearchAgent,             0.20),
    ("ContentIntelligence",  ContentIntelligenceAgent,  0.30),
    ("Generation",           GenerationAgent,           0.55),
    ("BrandVoice",           BrandVoiceAgent,           0.75),
    ("Optimization",         OptimizationAgent,         0.95),
]


class AgentOrchestrator:
    """
    Runs all 6 agents end-to-end and merges context between steps.

    Args:
        llm_provider: The LLMProvider instance (from core.llm)
        status_callback: Optional callable(WorkflowStatus) for real-time UI updates
    """

    def __init__(
        self,
        llm_provider=None,
        status_callback: Optional[Callable[[WorkflowStatus], None]] = None,
    ):
        self.llm = llm_provider
        self.status_callback = status_callback
        self._init_agents()
        logger.info("✅ AgentOrchestrator initialized (6-agent pipeline)")

    def _init_agents(self):
        self.agents = {
            "InputProcessor":      InputProcessorAgent(self.llm),
            "Research":            ResearchAgent(self.llm),
            "ContentIntelligence": ContentIntelligenceAgent(self.llm),
            "Generation":          GenerationAgent(self.llm),
            "BrandVoice":          BrandVoiceAgent(self.llm),
            "Optimization":        OptimizationAgent(self.llm),
        }

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def execute_workflow(self, user_input: Dict) -> OrchestratorResult:
        """
        Run the full 6-agent pipeline.

        user_input keys:
            text           : str   (topic or raw text)
            image_paths    : list  (image file paths)
            document_paths : list  (PDF/DOCX paths)
            urls           : list  (web URLs)
            past_posts     : list  (optional — user's past posts for brand DNA)
            tone           : str   (optional style preference)
            audience       : str   (optional audience preference)
        """
        workflow_start = time.time()
        context: Dict[str, Any] = dict(user_input)
        agents_run: List[str] = []

        logger.info("🚀 Orchestrator: starting 6-agent workflow...")

        for label, _, progress in PIPELINE:
            agent = self.agents[label]
            self._emit_status(WorkflowStatus(
                agent_name=label, status="running",
                message=f"Running {label}...", progress=progress,
            ))

            try:
                result: AgentResult = agent.run(context)
                agents_run.append(label)

                if not result.success:
                    logger.warning(f"⚠️ Agent '{label}' failed: {result.error_message} — continuing")
                    self._emit_status(WorkflowStatus(
                        agent_name=label, status="error",
                        message=result.error_message, progress=progress,
                    ))
                    continue

                # Merge result context into shared context dict
                if result.context_passed:
                    context.update(result.context_passed)
                # Also merge the agent's direct output fields
                if isinstance(result.output, dict):
                    # Merge output into context, preferring existing values
                    for k, v in result.output.items():
                        if k not in context or not context[k]:
                            context[k] = v

                self._emit_status(WorkflowStatus(
                    agent_name=label, status="complete",
                    message=result.summary, progress=progress,
                    elapsed=result.processing_time,
                ))
                logger.info(f"  ✅ {label}: {result.summary}")

            except Exception as exc:
                logger.error(f"❌ Agent '{label}' raised exception: {exc}")
                self._emit_status(WorkflowStatus(
                    agent_name=label, status="error",
                    message=str(exc), progress=progress,
                ))

        total_time = time.time() - workflow_start
        self._emit_status(WorkflowStatus(
            agent_name="Orchestrator", status="complete",
            message=f"Workflow complete in {total_time:.1f}s",
            progress=1.0, elapsed=total_time,
        ))

        # Extract final outputs from merged context
        variants = context.get("variants", {})
        if not variants:
            return OrchestratorResult(
                success=False,
                error_message="No post variants were generated",
                total_time=total_time,
                agents_run=agents_run,
            )

        return OrchestratorResult(
            success=True,
            variants=variants,
            hashtags=context.get("hashtags", ""),
            strategy=context.get("strategy", {}),
            research={
                "trending_hashtags": context.get("trending_hashtags", []),
                "related_topics": context.get("related_topics", []),
                "content_opportunities": context.get("content_opportunities", []),
                "market_intelligence": context.get("market_intelligence", ""),
            },
            brand_feedback=context.get("brand_feedback", {}),
            optimization=context.get("optimization", {}),
            overall_recommendations=context.get("overall_recommendations", []),
            best_variant=context.get("best_variant", "storyteller"),
            total_time=round(total_time, 2),
            agents_run=agents_run,
        )

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _emit_status(self, status: WorkflowStatus):
        if self.status_callback:
            try:
                self.status_callback(status)
            except Exception:
                pass
