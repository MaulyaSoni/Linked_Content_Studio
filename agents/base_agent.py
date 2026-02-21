"""
Base Agent
==========
Abstract foundation for all agents. Provides:
  - LLM access via the existing LLMProvider
  - Short-term memory (conversation history)
  - Tool registration and execution
  - Structured logging / status reporting
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Single message in an agent's conversation history."""
    role: str       # "user" | "assistant" | "system" | "tool"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class AgentResult:
    """Standardized output from any agent."""
    success: bool
    agent_name: str
    output: Any = None                  # Agent-specific structured data
    summary: str = ""                   # Human-readable summary
    next_agent_hint: str = ""           # Suggested next step
    context_passed: Dict = field(default_factory=dict)
    processing_time: float = 0.0
    error_message: str = ""
    metadata: Dict = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base for all Content Studio agents.

    Subclasses must implement:
        run(input_data: Dict) -> AgentResult
    """

    def __init__(self, name: str, llm_provider=None):
        self.name = name
        self.llm = llm_provider
        self.memory: List[AgentMessage] = []
        self._tools: Dict[str, Callable] = {}
        self.logger = logging.getLogger(f"agent.{name}")
        self.logger.info(f"🤖 Agent '{name}' initialized")

    # ------------------------------------------------------------------
    # ABSTRACT
    # ------------------------------------------------------------------

    @abstractmethod
    def run(self, input_data: Dict) -> AgentResult:
        """Execute this agent's primary task and return a result."""

    # ------------------------------------------------------------------
    # TOOL MANAGEMENT
    # ------------------------------------------------------------------

    def register_tool(self, name: str, func: Callable):
        """Register a callable tool this agent can invoke."""
        self._tools[name] = func
        self.logger.debug(f"🔧 Tool registered: {name}")

    def call_tool(self, name: str, **kwargs) -> Any:
        """Call a registered tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not registered on agent '{self.name}'")
        return self._tools[name](**kwargs)

    # ------------------------------------------------------------------
    # MEMORY
    # ------------------------------------------------------------------

    def remember(self, role: str, content: str, metadata: Optional[Dict] = None):
        self.memory.append(AgentMessage(role=role, content=content, metadata=metadata or {}))

    def get_context_window(self, last_n: int = 10) -> str:
        """Return last N messages as formatted string."""
        msgs = self.memory[-last_n:]
        return "\n".join(f"[{m.role.upper()}]: {m.content}" for m in msgs)

    def clear_memory(self):
        self.memory.clear()

    # ------------------------------------------------------------------
    # LLM WRAPPER
    # ------------------------------------------------------------------

    def think(self, prompt: str, system_prompt: str = "") -> str:
        """Ask the LLM a question and store the exchange in memory."""
        if not self.llm:
            self.logger.warning("⚠️ No LLM provider — returning empty response")
            return ""

        self.remember("user", prompt)
        sys = system_prompt or f"You are {self.name}, a specialized AI agent."
        result = self.llm.generate(prompt=prompt, system_prompt=sys)

        response = result.content if result.success else ""
        self.remember("assistant", response)
        return response

    # ------------------------------------------------------------------
    # STATUS HELPERS
    # ------------------------------------------------------------------

    def _success(
        self,
        output: Any,
        summary: str = "",
        context: Optional[Dict] = None,
        next_hint: str = "",
        time: float = 0.0,
        metadata: Optional[Dict] = None,
    ) -> AgentResult:
        return AgentResult(
            success=True,
            agent_name=self.name,
            output=output,
            summary=summary,
            context_passed=context or {},
            next_agent_hint=next_hint,
            processing_time=time,
            metadata=metadata or {},
        )

    def _failure(self, message: str, time: float = 0.0) -> AgentResult:
        self.logger.error(f"❌ Agent '{self.name}' failed: {message}")
        return AgentResult(
            success=False,
            agent_name=self.name,
            error_message=message,
            processing_time=time,
        )
