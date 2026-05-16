# backend/app/tools/web_search_tool.py

import os
from typing import Dict, List, Optional
from tavily import TavilyClient


class WebSearchTool:
    """Fetch real-time context for post generation."""

    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None

    async def search_topic_context(
        self,
        topic: str,
        max_results: int = 3
    ) -> Dict:
        """
        Search for current context around a topic.
        Returns structured data for injection into prompt.
        """
        if not self.client:
            return {"found": False, "snippets": [], "query": topic}
            
        try:
            results = self.client.search(
                query=f"LinkedIn {topic} 2026 insights trends",
                max_results=max_results,
                search_depth="basic",
            )

            snippets = []
            for r in results.get("results", []):
                if r.get("content"):
                    snippets.append({
                        "title":   r.get("title", ""),
                        "snippet": r.get("content", "")[:300],
                        "url":     r.get("url", ""),
                    })

            return {
                "found": len(snippets) > 0,
                "snippets": snippets,
                "query": f"LinkedIn {topic} 2026",
            }

        except Exception:
            # Never crash generation because of search failure
            return {"found": False, "snippets": [], "query": topic}

    def format_for_prompt(self, search_result: Dict) -> str:
        """Format search results as prompt context block."""
        if not search_result["found"]:
            return ""

        lines = ["\nREAL-TIME CONTEXT (use 1-2 of these naturally if relevant):"]
        for s in search_result["snippets"]:
            lines.append(f"- {s['snippet'][:200]}")

        return "\n".join(lines)
