"""
LinkedIn Poster Tool
====================
Posts content directly to LinkedIn via the UGC Posts API.
Requires LINKEDIN_ACCESS_TOKEN and LINKEDIN_USER_ID in .env

Usage:
    poster = LinkedInPoster()
    result = poster.post_to_linkedin(
        post_content="...",
        hashtags="#AI #Innovation",
    )
    if result.success:
        print(result.post_url)
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LinkedInPostResult:
    """Result of a LinkedIn posting operation."""
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: str = ""
    share_commentary_preview: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class LinkedInPoster:
    """
    Posts content to LinkedIn via OAuth 2.0 / UGC Posts API.
    
    Required env variables:
        LINKEDIN_ACCESS_TOKEN
        LINKEDIN_USER_ID
    Optional:
        LINKEDIN_CLIENT_ID
        LINKEDIN_CLIENT_SECRET
    """

    API_BASE = "https://api.linkedin.com/v2"
    LINKEDIN_BASE = "https://www.linkedin.com"

    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.user_id = os.getenv("LINKEDIN_USER_ID", "")
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")

        if not self.access_token or not self.user_id:
            msg = (
                "LinkedIn credentials missing. "
                "Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_USER_ID in your .env file."
            )
            logger.warning(f"⚠️ {msg}")
            # Do NOT raise — allow the app to start without credentials
        else:
            logger.info("✅ LinkedInPoster initialized")

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def post_to_linkedin(
        self,
        post_content: str,
        hashtags: Optional[str] = None,
        visibility: str = "PUBLIC",
        post_type: str = "TEXT",
        media_urls: Optional[List[str]] = None,
        scheduled_time: Optional[str] = None,
    ) -> LinkedInPostResult:
        """
        Post text content (with optional hashtags) to LinkedIn.

        Args:
            post_content:   Main post text (max 3000 chars)
            hashtags:       Optional hashtag string appended to content
            visibility:     PUBLIC or CONNECTIONS_ONLY
            post_type:      TEXT | IMAGE | VIDEO | DOCUMENT
            media_urls:     URLs of media to attach (for non-TEXT posts)
            scheduled_time: ISO datetime string for scheduled posts

        Returns:
            LinkedInPostResult
        """
        if not self._credentials_available():
            return LinkedInPostResult(
                success=False,
                error_message=(
                    "LinkedIn credentials not configured. "
                    "Add LINKEDIN_ACCESS_TOKEN and LINKEDIN_USER_ID to .env"
                ),
            )

        full_content = post_content
        if hashtags:
            full_content = f"{post_content}\n\n{hashtags}"

        payload = self._build_payload(
            content=full_content,
            post_type=post_type,
            media_urls=media_urls,
            visibility=visibility,
            scheduled_time=scheduled_time,
        )

        api_result = self._call_api(payload)

        if api_result["success"]:
            post_id = api_result["post_id"]
            post_url = f"{self.LINKEDIN_BASE}/feed/update/{post_id}"
            logger.info(f"✅ Posted to LinkedIn. ID: {post_id}")
            return LinkedInPostResult(
                success=True,
                post_id=post_id,
                post_url=post_url,
                share_commentary_preview=full_content[:120],
            )
        else:
            logger.error(f"❌ LinkedIn posting failed: {api_result['error']}")
            return LinkedInPostResult(
                success=False,
                error_message=api_result["error"],
            )

    def schedule_post(
        self,
        post_content: str,
        scheduled_time: str,
        hashtags: Optional[str] = None,
    ) -> LinkedInPostResult:
        """Schedule a post for a future time (ISO datetime string)."""
        return self.post_to_linkedin(
            post_content=post_content,
            hashtags=hashtags,
            scheduled_time=scheduled_time,
        )

    def delete_post(self, post_id: str) -> LinkedInPostResult:
        """Delete a previously published post."""
        if not self._credentials_available():
            return LinkedInPostResult(success=False, error_message="Credentials not configured")

        try:
            import requests  # type: ignore

            resp = requests.delete(
                f"{self.API_BASE}/ugcPosts/{post_id}",
                headers=self._headers(),
                timeout=10,
            )
            if resp.status_code in (200, 204):
                logger.info(f"✅ Deleted post {post_id}")
                return LinkedInPostResult(success=True, post_id=post_id)
            return LinkedInPostResult(success=False, error_message=resp.text)
        except Exception as exc:
            return LinkedInPostResult(success=False, error_message=str(exc))

    def get_post_stats(self, post_id: str) -> Dict:
        """Retrieve basic stats for a post."""
        if not self._credentials_available():
            return {"success": False, "error": "Credentials not configured"}
        try:
            import requests  # type: ignore

            resp = requests.get(
                f"{self.API_BASE}/ugcPosts/{post_id}",
                headers=self._headers(),
                timeout=10,
            )
            if resp.status_code == 200:
                return {"success": True, "stats": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------

    def _credentials_available(self) -> bool:
        return bool(self.access_token and self.user_id)

    def _headers(self) -> Dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }

    def _build_payload(
        self,
        content: str,
        post_type: str,
        media_urls: Optional[List[str]],
        visibility: str,
        scheduled_time: Optional[str],
    ) -> Dict:
        payload: Dict = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.Share": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": post_type,
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            },
        }

        if media_urls and post_type != "TEXT":
            payload["specificContent"]["com.linkedin.ugc.Share"]["media"] = [
                {"type": "ARTICLE", "status": "READY", "originalUrl": u}
                for u in media_urls
            ]

        if scheduled_time:
            payload["lifecycleState"] = "SCHEDULED"
            payload["firstPublishedAt"] = self._to_ms_epoch(scheduled_time)

        return payload

    def _call_api(self, payload: Dict) -> Dict:
        try:
            import requests  # type: ignore

            resp = requests.post(
                f"{self.API_BASE}/ugcPosts",
                headers=self._headers(),
                json=payload,
                timeout=10,
            )
            if resp.status_code == 201:
                post_id = resp.headers.get("X-LinkedIn-Id", "unknown")
                return {"success": True, "post_id": post_id}
            error = resp.json().get("message", resp.text) if resp.text else str(resp.status_code)
            return {"success": False, "error": error}
        except ImportError:
            return {"success": False, "error": "requests library not installed. Run: pip install requests"}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def _to_ms_epoch(self, iso_str: str) -> str:
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return str(int(dt.timestamp() * 1000))
        except Exception:
            return str(int(datetime.now().timestamp() * 1000))


# ---------------------------------------------------------------------------
# TOOL DEFINITIONS (for agent tool calling)
# ---------------------------------------------------------------------------

def get_linkedin_posting_tools() -> List[Dict]:
    """Return tool schemas for LLM/agent tool calling."""
    return [
        {
            "name": "post_to_linkedin",
            "description": "Post content directly to LinkedIn after generation.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "post_content": {"type": "string", "description": "Post text (max 3000 chars)"},
                    "hashtags": {"type": "string", "description": "Hashtag string to append"},
                    "visibility": {
                        "type": "string",
                        "enum": ["PUBLIC", "CONNECTIONS_ONLY"],
                        "description": "Post visibility",
                    },
                    "post_type": {
                        "type": "string",
                        "enum": ["TEXT", "IMAGE", "VIDEO", "DOCUMENT"],
                    },
                },
                "required": ["post_content"],
            },
        },
        {
            "name": "schedule_linkedin_post",
            "description": "Schedule a LinkedIn post for a future time.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "post_content": {"type": "string"},
                    "scheduled_time": {
                        "type": "string",
                        "description": "ISO datetime e.g. '2025-03-01T09:00:00'",
                    },
                    "hashtags": {"type": "string"},
                },
                "required": ["post_content", "scheduled_time"],
            },
        },
    ]
