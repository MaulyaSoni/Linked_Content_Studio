"""
Agent Memory
============
Shared conversation memory that persists context across the 6-agent pipeline.
Also provides a session history store for the Streamlit UI.
"""

import json
import logging
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)

SESSION_HISTORY_PATH = "data/session_history.json"
MAX_HISTORY_SESSIONS = 20


@dataclass
class SessionRecord:
    """One completed agentic generation session."""
    session_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    input_summary: str = ""
    variants: Dict[str, str] = field(default_factory=dict)
    best_variant: str = ""
    hashtags: str = ""
    strategy: Dict = field(default_factory=dict)
    total_time: float = 0.0
    posted_to_linkedin: bool = False
    post_url: str = ""


class AgentMemory:
    """
    Short-term working memory for one agentic workflow execution.
    Stores intermediate agent outputs and shared context.
    """

    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._log: List[Dict] = []

    def set(self, key: str, value: Any):
        """Store a value."""
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def update(self, data: Dict):
        """Bulk update from a dict."""
        self._store.update(data)

    def record_event(self, agent: str, event: str, data: Optional[Dict] = None):
        self._log.append({
            "agent": agent,
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "data": data or {},
        })

    def get_log(self) -> List[Dict]:
        return list(self._log)

    def as_context(self) -> Dict:
        return dict(self._store)

    def clear(self):
        self._store.clear()
        self._log.clear()


class SessionHistoryManager:
    """
    Persists completed agentic sessions to disk and retrieves them.
    Used to show the user their past generations.
    """

    def __init__(self, history_path: str = SESSION_HISTORY_PATH):
        self.path = Path(history_path)
        self._history: Deque[SessionRecord] = deque(maxlen=MAX_HISTORY_SESSIONS)
        self._load()

    def save_session(self, record: SessionRecord):
        self._history.appendleft(record)
        self._persist()

    def get_recent(self, n: int = 10) -> List[SessionRecord]:
        return list(self._history)[:n]

    def get_past_posts(self) -> List[str]:
        """Collect post texts from history for brand DNA learning."""
        posts = []
        for record in self._history:
            for text in record.variants.values():
                if text:
                    posts.append(text)
        return posts

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------

    def _load(self):
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text())
            for item in reversed(data[-MAX_HISTORY_SESSIONS:]):
                self._history.append(SessionRecord(**item))
        except Exception as exc:
            logger.warning(f"⚠️ Could not load session history: {exc}")

    def _persist(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            records = [asdict(r) for r in self._history]
            self.path.write_text(json.dumps(records, indent=2))
        except Exception as exc:
            logger.warning(f"⚠️ Could not save session history: {exc}")
