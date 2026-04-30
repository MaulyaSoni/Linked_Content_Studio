from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List


class StreamlitCompatService:
    """Bridge v3 API requests to the proven Streamlit generator."""

    def __init__(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))

        from core.generator import LinkedInGenerator
        from core.models import (
            Audience,
            ContentType,
            GenerationMode,
            HackathonAchievement,
            HackathonProjectRequest,
            HackathonType,
            PostRequest,
            Tone,
        )

        self.generator = LinkedInGenerator()
        self.PostRequest = PostRequest
        self.GenerationMode = GenerationMode
        self.ContentType = ContentType
        self.Tone = Tone
        self.Audience = Audience
        self.HackathonProjectRequest = HackathonProjectRequest
        self.HackathonAchievement = HackathonAchievement
        self.HackathonType = HackathonType

    def generate_standard_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        content_type = self._parse_enum(
            self.ContentType,
            payload.get("content_type", "educational"),
            self.ContentType.EDUCATIONAL,
        )
        mode = self._parse_enum(
            self.GenerationMode,
            payload.get("mode", "simple"),
            self.GenerationMode.SIMPLE,
        )
        tone = self._parse_enum(
            self.Tone,
            payload.get("tone", "professional"),
            self.Tone.PROFESSIONAL,
        )
        audience = self._parse_enum(
            self.Audience,
            payload.get("audience", "professionals"),
            self.Audience.PROFESSIONALS,
        )

        request = self.PostRequest(
            content_type=content_type,
            mode=mode,
            topic=(payload.get("topic") or "").strip(),
            github_url=(payload.get("github_url") or "").strip(),
            text_input=(payload.get("text_input") or "").strip(),
            user_key_message=(payload.get("user_key_message") or "").strip(),
            tags_people=payload.get("tags_people") or [],
            tags_organizations=payload.get("tags_organizations") or [],
            tone=tone,
            audience=audience,
            include_hashtags=bool(payload.get("include_hashtags", True)),
            include_caption=bool(payload.get("include_caption", False)),
            max_length=int(payload.get("max_length", 2000)),
        )

        response = self.generator.generate(request)
        data = asdict(response)
        data["hashtags_list"] = self._hashtags_to_list(data.get("hashtags", ""))
        return data

    def generate_hackathon_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        request = self.HackathonProjectRequest(
            hackathon_name=payload.get("hackathon_name", "").strip(),
            project_name=payload.get("project_name", "").strip(),
            team_size=int(payload.get("team_size", 4)),
            team_members=payload.get("team_members") or [],
            your_role=payload.get("your_role", "Developer"),
            problem_statement=payload.get("problem_statement", "").strip(),
            solution_description=payload.get("solution_description", "").strip(),
            tech_stack=payload.get("tech_stack") or [],
            key_features=payload.get("key_features") or [],
            achievement=self._parse_enum(
                self.HackathonAchievement,
                payload.get("achievement", "participant"),
                self.HackathonAchievement.PARTICIPANT,
            ),
            completion_time_hours=int(payload.get("completion_time_hours", 24)),
            personal_journey=payload.get("personal_journey", "").strip(),
            key_learnings=payload.get("key_learnings") or [],
            tone=payload.get("tone", "thoughtful"),
            audience=payload.get("audience", "developers"),
            hackathon_type=self._parse_enum(
                self.HackathonType,
                payload.get("hackathon_type", "general"),
                self.HackathonType.GENERAL,
            ),
        )

        response = self.generator.generate_hackathon_post(request)
        data = asdict(response)
        data["hashtags_list"] = self._hashtags_to_list(data.get("hashtags", ""))
        return data

    @staticmethod
    def _parse_enum(enum_cls: Any, raw_value: str, fallback: Any) -> Any:
        try:
            return enum_cls(raw_value)
        except Exception:
            return fallback

    @staticmethod
    def _hashtags_to_list(raw: str) -> List[str]:
        return [token for token in (raw or "").split() if token.startswith("#")]
