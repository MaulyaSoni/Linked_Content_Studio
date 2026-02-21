"""
Brand DNA Manager
=================
Persistent management of a user's brand voice profile.
Stores analyzed profiles to disk and retrieves them across sessions.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from tools.brand_analyzer import BrandAnalyzer, BrandProfile

logger = logging.getLogger(__name__)

DEFAULT_PROFILE_PATH = "data/brand_dna.json"


class BrandDNAManager:
    """
    High-level API for managing a user's Brand DNA.

    Workflow:
        1. Call learn(past_posts) — analyzes posts and saves profile
        2. Call get_profile() — retrieves saved profile
        3. Call check(new_post) — checks new post against profile
        4. Call apply(post) — rewrites post to match brand voice
    """

    def __init__(self, llm_provider=None, profile_path: str = DEFAULT_PROFILE_PATH):
        self.llm = llm_provider
        self.profile_path = Path(profile_path)
        self.analyzer = BrandAnalyzer(llm_provider, profile_path=str(profile_path))
        self._profile: Optional[BrandProfile] = self.analyzer.load_profile()

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def learn(self, past_posts: List[str]) -> BrandProfile:
        """Analyze past posts and save brand profile."""
        if not past_posts:
            logger.warning("⚠️ No past posts provided — brand DNA not updated")
            return self._profile or BrandProfile(success=False, error_message="No posts provided")

        self._profile = self.analyzer.analyze_past_posts(past_posts)
        logger.info(
            f"✅ Brand DNA learned from {len(past_posts)} posts. "
            f"Tone: {self._profile.dominant_tone if self._profile.success else 'unknown'}"
        )
        return self._profile

    def get_profile(self) -> Optional[BrandProfile]:
        """Return the current brand profile (load from disk if needed)."""
        if not self._profile:
            self._profile = self.analyzer.load_profile()
        return self._profile

    def has_profile(self) -> bool:
        return bool(self._profile and self._profile.success)

    def check(self, new_post: str):
        """Check consistency of a new post against brand DNA."""
        return self.analyzer.check_consistency(new_post, self._profile)

    def get_summary(self) -> str:
        """Human-readable summary of brand DNA."""
        if not self.has_profile():
            return "No brand DNA profile yet. Add past posts to build your brand voice."
        p = self._profile
        return (
            f"**Brand DNA Summary**\n"
            f"- Dominant Tone: {p.dominant_tone}\n"
            f"- Avg Post Length: ~{p.avg_post_length} words\n"
            f"- Uses Emojis: {'Yes' if p.uses_emojis else 'No'}\n"
            f"- Storytelling: {'Yes' if p.uses_storytelling else 'No'}\n"
            f"- Hashtag Style: {p.hashtag_style} (~{p.avg_hashtag_count:.0f} per post)\n"
            f"- Themes: {', '.join(p.common_themes[:5])}\n"
            f"- Voice: {p.brand_voice_summary}"
        )
